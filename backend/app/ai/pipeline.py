import logging
import numpy as np
from typing import Dict, Any, List
from collections import deque

from app.ai.models import DetectionContext
from app.ai.detection.yolo_detector import YOLODetector
from app.ai.tracking.sort_tracker import SortTrackerWrapper
from app.ai.pose.mediapipe_pose import MediaPipePoseEstimator
from app.ai.features.extractor import FeatureExtractor
from app.ai.activity.heuristic_recognizer import HeuristicActivityRecognizer
from app.ai.digital_twin.state_engine import DigitalTwinStateEngine

# Risk & Prediction imports (Phases 5 & 6)
from app.ai.anomaly.rule_detector import RuleBasedAnomalyDetector
from app.ai.risk.risk_engine import RiskEngine
from app.ai.prediction.predictor import BehaviorPredictor

logger = logging.getLogger(__name__)

class AIPipelineManager:
    def __init__(self):
        logger.info("Initializing AI Pipeline Manager...")
        self.detector = YOLODetector()
        self.tracker = SortTrackerWrapper()
        self.pose_estimator = MediaPipePoseEstimator()
        
        self.feature_extractor = FeatureExtractor(window_size=10, fps=30)
        self.activity_recognizer = HeuristicActivityRecognizer(smoothing_window=5)
        self.digital_twin_engine = DigitalTwinStateEngine()
        
        # Risk & Prediction Components
        self.anomaly_detector = RuleBasedAnomalyDetector()
        self.risk_engine = RiskEngine()
        self.predictor = BehaviorPredictor()
        
        # Track history
        self.person_history_map: Dict[str, deque] = {}
        self.state_history = deque(maxlen=90) # Track last 90 instances for rules & prediction
        
    async def process_frame(self, frame: np.ndarray, camera_id: str) -> Dict[str, Any]:
        if frame is None or frame.size == 0:
            logger.warning("Empty frame received. Skipping.")
            return {}

        h, w, _ = frame.shape
        context = DetectionContext(frame_width=w, frame_height=h, camera_id=camera_id)

        # 1. Pipeline basics
        detections = await self.detector.detect(frame, context)
        tracked_persons = self.tracker.update(detections, frame)

        active_track_ids = set()
        enhanced_tracked_persons = []
        
        for person in tracked_persons:
            track_id = person.tracking_id
            active_track_ids.add(track_id)
            
            if track_id not in self.person_history_map:
                self.person_history_map[track_id] = deque(maxlen=10)
            self.person_history_map[track_id].append(person)
            
            pose = await self.pose_estimator.estimate_pose(frame, person)
            
            person_dict = person.model_dump()
            person_dict["pose"] = pose.model_dump() if pose else {}
            
            person_history = list(self.person_history_map[track_id])
            features = self.feature_extractor.extract(person_history)
            person_dict["features"] = features
            
            activity_result = await self.activity_recognizer.recognize(features, person_history)
            person_dict["activity"] = activity_result.activity
            person_dict["activity_confidence"] = activity_result.confidence
            
            enhanced_tracked_persons.append(person_dict)
            
        stale_tracks = set(self.person_history_map.keys()) - active_track_ids
        for stale_id in stale_tracks:
            del self.person_history_map[stale_id]

        pipeline_output = {
            "timestamp": context.timestamp.isoformat(),
            "camera_id": camera_id,
            "tracked_persons": enhanced_tracked_persons
        }
        
        # 2. Digital Twin State
        persons_twins = self.digital_twin_engine.update_from_pipeline(pipeline_output)
        
        # Construct the unified dict state for Phase 5 & 6
        twin_state = {
            "timestamp": pipeline_output["timestamp"],
            "persons": persons_twins,
            "zones": [z.model_dump() for z in getattr(self.digital_twin_engine, 'zones', {}).values()],
            "objects": [o.model_dump() for o in getattr(self.digital_twin_engine, 'objects', {}).values()]
        }
        
        history_list = list(self.state_history)
        
        # 3. Phase 5: Anomaly & Risk Evaluation
        anomalies = self.anomaly_detector.check(twin_state, history_list)
        risk = self.risk_engine.evaluate(twin_state, anomalies)
        
        # 4. Phase 6: Prediction
        predictions = self.predictor.predict(twin_state, history_list)
        
        # Attach to state
        twin_state["anomalies"] = anomalies
        twin_state["risk"] = risk
        twin_state["predictions"] = predictions
        
        # Manage history
        self.state_history.append(twin_state)
        
        # 5. Alert Triggering
        alert_triggered = False
        if risk.get("overall_level") in ["HIGH", "CRITICAL"]:
            alert_triggered = True
            
        twin_state["alert"] = alert_triggered
        
        state = {
            "timestamp": pipeline_output["timestamp"],
            "camera_id": camera_id,
            "digital_twin_state": twin_state,
            "raw_pipeline_data": pipeline_output
        }
        
        return state

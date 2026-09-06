import numpy as np
from typing import List
from app.ai.tracking.base import BaseTracker
from app.ai.models import DetectedObject, TrackedPerson, BoundingBox

def calculate_iou(box1: BoundingBox, box2: BoundingBox) -> float:
    """Calculate the Intersection over Union (IoU) of two bounding boxes."""
    x1_inter = max(box1.x, box2.x)
    y1_inter = max(box1.y, box2.y)
    x2_inter = min(box1.x + box1.w, box2.x + box2.w)
    y2_inter = min(box1.y + box1.h, box2.y + box2.h)

    inter_width = max(0, x2_inter - x1_inter)
    inter_height = max(0, y2_inter - y1_inter)
    inter_area = inter_width * inter_height

    box1_area = box1.w * box1.h
    box2_area = box2.w * box2.h

    union_area = box1_area + box2_area - inter_area
    if union_area == 0:
        return 0.0

    return inter_area / union_area

class SortTrackerWrapper(BaseTracker):
    """
    A simple IOU-based tracker that assigns persistent IDs to consecutive detections.
    Serves as a placeholder for a true SORT or ByteTrack implementation.
    """
    def __init__(self, iou_threshold: float = 0.3, max_age: int = 5):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        
        self.next_id_num = 1
        self.tracked_objects = {}  # id -> {'bbox': BoundingBox, 'age': int, 'history': List}

    def _generate_id(self) -> str:
        new_id = f"P{self.next_id_num:03d}"
        self.next_id_num += 1
        return new_id

    def update(self, detections: List[DetectedObject], frame: np.ndarray) -> List[TrackedPerson]:
        unmatched_detections = list(detections)
        unmatched_trackers = list(self.tracked_objects.keys())
        
        # Increase age of all existing tracks
        for trk_id in self.tracked_objects:
            self.tracked_objects[trk_id]['age'] += 1

        # Match detections to existing tracks based on highest IoU
        matched = []
        for det in unmatched_detections:
            best_iou = self.iou_threshold
            best_trk_id = None
            
            for trk_id in unmatched_trackers:
                iou = calculate_iou(det.bbox, self.tracked_objects[trk_id]['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_trk_id = trk_id
                    
            if best_trk_id is not None:
                matched.append((det, best_trk_id))
                unmatched_trackers.remove(best_trk_id)
                
        # Update matched tracks
        for det, trk_id in matched:
            self.tracked_objects[trk_id]['bbox'] = det.bbox
            self.tracked_objects[trk_id]['age'] = 0
            # Keep history limited
            hist = self.tracked_objects[trk_id].get('history', [])
            hist.append(det.center)
            if len(hist) > 30:
                hist.pop(0)
            self.tracked_objects[trk_id]['history'] = hist
            
            # Remove from unmatched
            if det in unmatched_detections:
                unmatched_detections.remove(det)
                
        # Create new tracks for unmatched detections
        for det in unmatched_detections:
            new_id = self._generate_id()
            self.tracked_objects[new_id] = {
                'bbox': det.bbox,
                'age': 0,
                'history': [det.center]
            }

        # Delete expired tracks
        expired = [trk_id for trk_id, data in self.tracked_objects.items() if data['age'] > self.max_age]
        for trk_id in expired:
            del self.tracked_objects[trk_id]
            
        # Format output
        results = []
        for trk_id, data in self.tracked_objects.items():
            if data['age'] == 0:  # Only return currently visible tracks
                state_history = [{'center': p} for p in data['history']]
                results.append(
                    TrackedPerson(
                        tracking_id=trk_id,
                        bbox=data['bbox'],
                        state_history=state_history
                    )
                )
                
        return results

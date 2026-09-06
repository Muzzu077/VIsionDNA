import datetime
import math
from typing import Dict, Any

class SimulationEngine:
    def __init__(self, cycle_duration=30.0, fps=2.0):
        self.start_time = datetime.datetime.now()
        self.cycle_duration = cycle_duration
        self.fps = fps
        self.frame_count = 0

    def generate_frame_state(self, camera_id: str) -> Dict[str, Any]:
        """
        Generate a mocked pipeline state output to satisfy Demo Mode.
        Deterministic scenario: 
        - P001 Starts standing low risk.
        - Transitions to Walking, increasing velocity.
        - Trajectory heads toward Zone "Restricted Area".
        - Risk score increases, Prediction says HIGH RISK (86% restricted-zone entry).
        - Alert is triggered.
        Loops every 30 seconds.
        """
        now = datetime.datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        
        # Loop every `cycle_duration` seconds
        current_time_in_cycle = elapsed % self.cycle_duration
        cycle_progress = current_time_in_cycle / self.cycle_duration  # 0.0 to 1.0

        person_id = "P001"
        
        # Base variables
        activity = "standing"
        risk_level = "LOW"
        risk_score = 10.0
        prediction = "Normal standing behavior"
        alert_triggered = False
        velocity = 0.0
        
        x_start, y_start = 100.0, 500.0
        x_end, y_end = 800.0, 100.0 # Moving diagonally towards restricted area
        
        x_pos = x_start
        y_pos = y_start

        # State machine across 30 seconds
        if current_time_in_cycle < 5.0:
            # 0 - 5s: Standing, low risk
            activity = "standing"
            velocity = 0.0
            risk_score = 10.0
            risk_level = "LOW"
            x_pos = x_start
            y_pos = y_start
            
        elif current_time_in_cycle < 15.0:
            # 5 - 15s: Transitions to Walking, increasing velocity
            progress = (current_time_in_cycle - 5.0) / 10.0
            activity = "walking"
            velocity = 1.0 + (progress * 2.0) # velocity increases
            risk_score = 10 + (progress * 15.0)
            risk_level = "LOW"
            
            x_pos = x_start + (x_end - x_start) * progress * 0.4
            y_pos = y_start + (y_end - y_start) * progress * 0.4
            
        elif current_time_in_cycle < 25.0:
            # 15 - 25s: Trajectory heads toward Restricted Area. Risk increases.
            progress = (current_time_in_cycle - 15.0) / 10.0
            activity = "approaching_restricted_area"
            velocity = 3.0
            risk_score = 25.0 + (progress * 60.0) # goes up to 85
            risk_level = "MEDIUM" if risk_score < 70 else "HIGH"
            prediction = "HIGH RISK (86% restricted-zone entry)" if risk_score >= 70 else "Approaching restricted zone"
            
            x_pos = x_start + (x_end - x_start) * (0.4 + progress * 0.5)
            y_pos = y_start + (y_end - y_start) * (0.4 + progress * 0.5)
            
        else:
            # 25 - 30s: Inside Restricted Area. Alert is triggered.
            progress = (current_time_in_cycle - 25.0) / 5.0
            activity = "unauthorized_access"
            velocity = 1.0 # slows down inside
            risk_score = 90.0
            risk_level = "CRITICAL"
            prediction = "HIGH RISK (86% restricted-zone entry)"
            alert_triggered = True
            
            x_pos = x_start + (x_end - x_start) * (0.9 + progress * 0.1)
            y_pos = y_start + (y_end - y_start) * (0.9 + progress * 0.1)

        self.frame_count += 1
        # Fake sine bobbing for y position to simulate walking if velocity > 0
        if velocity > 0:
            y_pos += math.sin(self.frame_count * 0.5) * 5

        mock_bbox = {
            "x": float(x_pos),
            "y": float(y_pos),
            "w": 60.0,
            "h": 180.0
        }

        state = {
            "timestamp": now.isoformat(),
            "camera_id": camera_id,
            "person_id": person_id,
            "activity": activity,
            "velocity": velocity,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "prediction": prediction,
            "prediction_probability": 0.86 if risk_score >= 70 else None,
            "prediction_horizon_seconds": 10 if risk_score >= 70 else None,
            "explanation": (
                "Simulation only: increasing velocity and decreasing distance to Restricted Area."
                if risk_score >= 70
                else "Simulation only: baseline monitored movement."
            ),
            "alert_triggered": alert_triggered,
            "simulation_mode": True,
            "zone": "Restricted Area" if current_time_in_cycle >= 25.0 else "Main Hall",
            "x_pos": x_pos,
            "y_pos": y_pos,
            "tracked_persons": [
                {
                    "tracking_id": person_id,
                    "bbox": mock_bbox,
                    "activity_mock": activity
                }
            ]
        }
        return state

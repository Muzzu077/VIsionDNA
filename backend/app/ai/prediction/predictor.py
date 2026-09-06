import logging
import math
from typing import Dict, Any, List
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon

logger = logging.getLogger(__name__)

class BehaviorPredictor:
    def __init__(self):
        self.fps = 30 # Assumption, adjust as needed

    def predict(self, twin_state: dict, history: list) -> dict:
        """
        Predict future behavior (e.g. entering a restricted zone).
        
        Args:
            twin_state (dict): Current state
            history (list): List of previous state dicts (chronological, oldest first).
            
        Returns:
            dict: Mapping of person_id to a list of prediction dictionaries.
        """
        predictions = {}
        
        persons = twin_state.get('persons', [])
        zones = twin_state.get('zones', [])
        
        # Build Shapely polygons for zones
        zone_polygons = {}
        for zone in zones:
            pts = zone.get('points', [])
            if pts:
                try:
                    poly = Polygon([(pt['x'], pt['y']) for pt in pts])
                    zone_polygons[zone['id']] = (zone, poly)
                except Exception as e:
                    logger.error(f"Error parsing zone polygon for prediction: {e}")
                    
        for person in persons:
            p_id = person.get('tracking_id')
            current_pos = person.get('position')
            if not p_id or not current_pos:
                continue
                
            predictions[p_id] = []
            
            # Extract historical positions for this person
            traj = []
            for state in history:
                past_persons = [p for p in state.get('persons', []) if p.get('tracking_id') == p_id]
                if past_persons and past_persons[0].get('position'):
                    pos = past_persons[0]['position']
                    traj.append((pos['x'], pos['y']))
                    
            traj.append((current_pos['x'], current_pos['y']))
            
            # Need at least 2 points to get a velocity vector
            if len(traj) < 2:
                continue
                
            # Use a slightly smoothed velocity using last few frames
            # Calculate displacement over the available history window
            window = min(len(traj), 15)  # Let's look at last 15 frames (~0.5s)
            start_pt = traj[-window]
            end_pt = traj[-1]
            
            dx = end_pt[0] - start_pt[0]
            dy = end_pt[1] - start_pt[1]
            
            # Velocity in pixels/units per frame
            frames_elapsed = window - 1
            if frames_elapsed == 0:
                continue
                
            vx = dx / frames_elapsed
            vy = dy / frames_elapsed
            speed_per_frame = math.hypot(vx, vy)
            speed_per_sec = speed_per_frame * self.fps
            
            if speed_per_sec < 5.0:
                # person is relatively static, no need to predict trajectory collisions
                continue
                
            # Project trajectory 3 seconds into the future
            future_frames = 3 * self.fps
            future_x = end_pt[0] + vx * future_frames
            future_y = end_pt[1] + vy * future_frames
            
            trajectory_line = LineString([end_pt, (future_x, future_y)])
            
            # Check for intersections with restricted zones
            for zone_id, (zone_info, poly) in zone_polygons.items():
                if zone_info.get('type') == 'restricted':
                    if trajectory_line.intersects(poly):
                        # Calculate distance to intersection
                        intersection = trajectory_line.intersection(poly)
                        
                        # Intersection can be a point, linestring, or multigeometry
                        if intersection.is_empty:
                            continue
                            
                        # Get the closest point of intersection
                        if intersection.geom_type == 'Point':
                            closest_pt = intersection
                        elif intersection.geom_type == 'LineString':
                            closest_pt = Point(intersection.coords[0])
                        elif intersection.geom_type in ['MultiPoint', 'MultiLineString', 'GeometryCollection']:
                             # Approximate with the first geometry
                             closest_geom = list(intersection.geoms)[0]
                             if closest_geom.geom_type == 'Point':
                                 closest_pt = closest_geom
                             elif closest_geom.geom_type == 'LineString':
                                 closest_pt = Point(closest_geom.coords[0])
                             else:
                                 continue
                        else:
                            continue
                            
                        distance_to_zone = Point(end_pt).distance(closest_pt)
                        time_to_entry_sec = distance_to_zone / speed_per_sec if speed_per_sec > 0 else 999.0
                        
                        # Probability based on time to entry (closer = higher probability)
                        # Max probability 0.95 at 0 seconds, 0.5 at 3 seconds
                        prob = max(0.1, 0.95 - (time_to_entry_sec / 3.0) * 0.45)
                        
                        predictions[p_id].append({
                            "prediction": "restricted_zone_entry",
                            "probability": round(prob, 2),
                            "horizon_seconds": round(time_to_entry_sec, 2),
                            "risk_level": "HIGH"
                        })
                        
        return predictions

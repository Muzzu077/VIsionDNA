import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RuleBasedAnomalyDetector:
    def __init__(self):
        self.prolonged_inactivity_threshold_frames = 90  # roughly 3 seconds at 30 fps
        self.dangerous_proximity_threshold = 50.0  # spatial distance units (e.g. pixels or scaled meters)
        self.crowd_density_threshold = 4  # e.g., 4 people in the same zone is considered crowded
        
    def check(self, twin_state: dict, history: list) -> list:
        """
        Check for anomalies based on current digital twin state and its history.
        
        Args:
            twin_state (dict): The current environment state, with 'persons', 'zones', 'objects'.
            history (list): A list of previous twin_states.
            
        Returns:
            list: A list of anomaly dictionaries containing type, severity, and description.
        """
        anomalies = []
        
        persons = twin_state.get('persons', [])
        zones = twin_state.get('zones', [])
        objects = twin_state.get('objects', [])
        
        # Mapping for zones to quickly check types and calculate densities
        zone_info = {z['id']: z for z in zones}
        zone_occupancy: Dict[str, list] = {z['id']: [] for z in zones}
        
        for person in persons:
            p_id = person.get('tracking_id')
            activity = person.get('activity', '')
            zone_id = person.get('current_zone')
            pos = person.get('position', {})
            distances = person.get('distances_to_objects', {})

            if zone_id and zone_id in zone_occupancy:
                zone_occupancy[zone_id].append(p_id)
                
            # Rule 1: Restricted Zone Entry
            if zone_id and zone_id in zone_info:
                z_type = zone_info[zone_id].get('type', '')
                if z_type == 'restricted':
                    anomalies.append({
                        "type": "restricted_zone_entry",
                        "severity": "CRITICAL",
                        "person_id": p_id,
                        "zone_id": zone_id,
                        "description": f"Person {p_id} entered restricted zone '{zone_info[zone_id].get('name', zone_id)}'."
                    })
                    
            # Rule 2: Dangerous Proximity to Monitored Objects
            for obj_id, dist in distances.items():
                if dist < self.dangerous_proximity_threshold:
                    anomalies.append({
                        "type": "dangerous_proximity",
                        "severity": "HIGH",
                        "person_id": p_id,
                        "object_id": obj_id,
                        "description": f"Person {p_id} is dangerously close ({dist:.1f} units) to object {obj_id}."
                    })

            # Rule 3: Prolonged Inactivity
            inactivity_count = 0
            # Walk backwards through history to see if the person has been sitting/standing in the exact same zone/spot
            for past_state in reversed(history):
                past_persons = [p for p in past_state.get('persons', []) if p.get('tracking_id') == p_id]
                if past_persons:
                    p_past = past_persons[0]
                    p_act = p_past.get('activity', '')
                    if p_act in ['standing', 'sitting', 'lying_down']:
                        inactivity_count += 1
                    else:
                        break
                else:
                    break
                    
            if (activity in ['standing', 'sitting', 'lying_down'] and 
                inactivity_count >= self.prolonged_inactivity_threshold_frames):
                anomalies.append({
                    "type": "prolonged_inactivity",
                    "severity": "MEDIUM",
                    "person_id": p_id,
                    "description": f"Person {p_id} has been inactive ('{activity}') for an extended period."
                })
                
        # Rule 4: Crowd Density
        for z_id, occupants in zone_occupancy.items():
            if len(occupants) > self.crowd_density_threshold:
                anomalies.append({
                    "type": "crowd_density",
                    "severity": "MEDIUM",
                    "zone_id": z_id,
                    "description": f"High crowd density detected in zone {z_id} ({len(occupants)} persons)."
                })
                
        return anomalies

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self):
        # Configurable weights for score out of 100
        self.weights = {
            "activity": 0.25,
            "zone": 0.20,     # Max 20 points
            "proximity": 0.20, # Max 20 points
            "movement": 0.15,  # Max 15 points
            "behavior": 0.10,  # Max 10 points
            "anomaly": 0.10    # Max 10 points
        }
        
        # Base activity risk (0 to 100 before weighting)
        self.activity_risk_base = {
            "lying_down": 100,
            "falling": 100,
            "running": 70,
            "walking": 20,
            "standing": 10,
            "sitting": 10
        }
        
    def evaluate(self, twin_state: dict, anomalies: list) -> dict:
        """
        Calculates an aggregate Risk Score 0-100 per person and overall.
        
        Returns:
            dict: Mapping of 'persons' risks and 'overall' risk score and level.
        """
        persons = twin_state.get('persons', [])
        zones = twin_state.get('zones', [])
        zone_info = {z['id']: z for z in zones}
        
        results = {
            "persons": {},
            "overall_score": 0,
            "overall_level": "LOW"
        }
        
        max_overall_score = 0
        
        for person in persons:
            p_id = person.get('tracking_id')
            activity = person.get('activity', 'standing')
            current_zone = person.get('current_zone')
            
            risk_factors = []
            
            # 1. Activity (max 25)
            base_act_score = self.activity_risk_base.get(activity, 10)
            act_score = base_act_score * self.weights["activity"]
            if act_score > 0:
                risk_factors.append(("Activity", act_score, f"High-risk activity ({activity})"))
                
            # 2. Zone Risk (max 20)
            zone_score = 0
            if current_zone and current_zone in zone_info:
                z_type = zone_info[current_zone].get('type', 'safe')
                if z_type == 'restricted':
                    zone_score = 100 * self.weights["zone"]
                    risk_factors.append(("Zone", zone_score, f"In restricted zone"))
                elif z_type == 'danger':
                    zone_score = 100 * self.weights["zone"]
                    risk_factors.append(("Zone", zone_score, f"In danger zone"))
            
            # 3. Anomaly & Proximity Risk
            person_anomalies = [a for a in anomalies if a.get('person_id') == p_id]
            anomaly_score = 0
            proximity_score = 0
            
            for anon in person_anomalies:
                if anon['type'] == 'dangerous_proximity':
                    prox = 100 * self.weights["proximity"]
                    if prox > proximity_score:
                        proximity_score = prox
                    risk_factors.append(("Proximity", prox, anon['description']))
                else:
                    sev = anon.get('severity', 'LOW')
                    if sev == 'CRITICAL': val = 100
                    elif sev == 'HIGH': val = 80
                    elif sev == 'MEDIUM': val = 50
                    else: val = 20
                    
                    anon_sc = val * self.weights["anomaly"]
                    if anon_sc > anomaly_score:
                        anomaly_score = anon_sc
                    risk_factors.append(("Anomaly", anon_sc, anon['description']))
                    
            # Basic movement/behavior heuristics based on speed if available
            movement_score = 0
            
            # Sum up total score (capped at 100)
            total_score = act_score + zone_score + proximity_score + anomaly_score + movement_score
            total_score = min(100.0, total_score)
            
            # Determine Level
            level = "LOW"
            if total_score > 80:
                level = "CRITICAL"
            elif total_score > 60:
                level = "HIGH"
            elif total_score > 30:
                level = "MEDIUM"
                
            # Explanation
            # Sort risk factors by contribution
            risk_factors.sort(key=lambda x: x[1], reverse=True)
            explanation = ""
            if risk_factors:
                top_factor = risk_factors[0]
                explanation = f"Person {p_id} risk is {level}. Top factor: {top_factor[2]} +{top_factor[1]:.1f}"
                if len(risk_factors) > 1:
                    explanation += f", along with {risk_factors[1][2]} +{risk_factors[1][1]:.1f}"
                    
            results["persons"][p_id] = {
                "score": total_score,
                "level": level,
                "explanation": explanation,
                "factors": [{"type": r[0], "score": r[1], "description": r[2]} for r in risk_factors]
            }
            
            if total_score > max_overall_score:
                max_overall_score = total_score
                
        # Handle scene-wide anomalies (e.g. crowd_density) for overall score
        scene_anomalies = [a for a in anomalies if 'person_id' not in a]
        scene_anomaly_score = 0
        for anon in scene_anomalies:
            sev = anon.get('severity', 'LOW')
            if sev == 'CRITICAL': val = 100
            elif sev == 'HIGH': val = 80
            elif sev == 'MEDIUM': val = 50
            else: val = 20
            
            scene_anomaly_score = max(scene_anomaly_score, val * self.weights["anomaly"])
            
        overall_score = min(100.0, max_overall_score + scene_anomaly_score)
        overall_level = "LOW"
        if overall_score > 80:
            overall_level = "CRITICAL"
        elif overall_score > 60:
            overall_level = "HIGH"
        elif overall_score > 30:
            overall_level = "MEDIUM"
            
        results["overall_score"] = overall_score
        results["overall_level"] = overall_level
        
        return results

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class EldercareService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'eldercare.db')
        
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def dict_factory(self, cursor, row):
        """Convert sqlite row to dictionary"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    # === ELDER MANAGEMENT ===
    
    def get_all_elders(self) -> List[Dict[str, Any]]:
        """Get all active elders with their basic information"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    id, name, age, gender, profile_image,
                    emergency_contact_name, emergency_contact_phone,
                    family_contact_name, family_contact_phone,
                    medical_conditions, medications, allergies,
                    preferred_language, care_level, room_location,
                    bed_number, created_at, is_active
                FROM elders 
                WHERE is_active = 1
                ORDER BY name
            ''')
            
            elders = cursor.fetchall()
            conn.close()
            
            # Parse JSON fields
            for elder in elders:
                try:
                    elder['medical_conditions'] = json.loads(elder['medical_conditions']) if elder['medical_conditions'] else []
                    elder['medications'] = json.loads(elder['medications']) if elder['medications'] else []
                    elder['allergies'] = json.loads(elder['allergies']) if elder['allergies'] else []
                except json.JSONDecodeError:
                    elder['medical_conditions'] = []
                    elder['medications'] = []
                    elder['allergies'] = []
            
            return elders
            
        except Exception as e:
            print(f"Error getting elders: {e}")
            return []
    
    def get_elder_by_id(self, elder_id: int) -> Optional[Dict[str, Any]]:
        """Get specific elder by ID"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM elders WHERE id = ? AND is_active = 1
            ''', (elder_id,))
            
            elder = cursor.fetchone()
            conn.close()
            
            if elder:
                # Parse JSON fields
                try:
                    elder['medical_conditions'] = json.loads(elder['medical_conditions']) if elder['medical_conditions'] else []
                    elder['medications'] = json.loads(elder['medications']) if elder['medications'] else []
                    elder['allergies'] = json.loads(elder['allergies']) if elder['allergies'] else []
                except json.JSONDecodeError:
                    elder['medical_conditions'] = []
                    elder['medications'] = []
                    elder['allergies'] = []
            
            return elder
            
        except Exception as e:
            print(f"Error getting elder {elder_id}: {e}")
            return None
    
    def get_elder_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get elder by name (for AI interactions)"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM elders 
                WHERE LOWER(name) LIKE LOWER(?) AND is_active = 1
                LIMIT 1
            ''', (f'%{name}%',))
            
            elder = cursor.fetchone()
            conn.close()
            
            if elder:
                # Parse JSON fields
                try:
                    elder['medical_conditions'] = json.loads(elder['medical_conditions']) if elder['medical_conditions'] else []
                    elder['medications'] = json.loads(elder['medications']) if elder['medications'] else []
                    elder['allergies'] = json.loads(elder['allergies']) if elder['allergies'] else []
                except json.JSONDecodeError:
                    elder['medical_conditions'] = []
                    elder['medications'] = []
                    elder['allergies'] = []
            
            return elder
            
        except Exception as e:
            print(f"Error getting elder by name {name}: {e}")
            return None
    
    # === CAREGIVER MANAGEMENT ===
    
    def get_caregivers_for_elder(self, elder_id: int) -> List[Dict[str, Any]]:
        """Get all caregivers assigned to an elder"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    c.id, c.name, c.role, c.phone_number, c.email,
                    c.shift_start, c.shift_end, c.specialization,
                    ec.relationship
                FROM caregivers c
                JOIN elder_caregiver ec ON c.id = ec.caregiver_id
                WHERE ec.elder_id = ? AND ec.is_active = 1 AND c.is_active = 1
                ORDER BY 
                    CASE ec.relationship 
                        WHEN 'primary' THEN 1
                        WHEN 'secondary' THEN 2
                        WHEN 'family' THEN 3
                        ELSE 4
                    END, c.name
            ''', (elder_id,))
            
            caregivers = cursor.fetchall()
            conn.close()
            
            return caregivers
            
        except Exception as e:
            print(f"Error getting caregivers for elder {elder_id}: {e}")
            return []
    
    # === CARE ACTIVITIES ===
    
    def get_upcoming_activities(self, elder_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming care activities for an elder"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    ca.*, c.name as caregiver_name
                FROM care_activities ca
                LEFT JOIN caregivers c ON ca.completed_by = c.id
                WHERE ca.elder_id = ? AND ca.status = 'pending'
                    AND ca.scheduled_time >= datetime('now')
                ORDER BY ca.scheduled_time
                LIMIT ?
            ''', (elder_id, limit))
            
            activities = cursor.fetchall()
            conn.close()
            
            return activities
            
        except Exception as e:
            print(f"Error getting activities for elder {elder_id}: {e}")
            return []
    
    def get_recent_activities(self, elder_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent completed activities for an elder"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    ca.*, c.name as caregiver_name
                FROM care_activities ca
                LEFT JOIN caregivers c ON ca.completed_by = c.id
                WHERE ca.elder_id = ? AND ca.status = 'completed'
                ORDER BY ca.completed_time DESC
                LIMIT ?
            ''', (elder_id, limit))
            
            activities = cursor.fetchall()
            conn.close()
            
            return activities
            
        except Exception as e:
            print(f"Error getting recent activities for elder {elder_id}: {e}")
            return []
    
    # === HEALTH VITALS ===
    
    def get_recent_vitals(self, elder_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent health vitals for an elder"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    hv.*, c.name as measured_by_name
                FROM health_vitals hv
                LEFT JOIN caregivers c ON hv.measured_by = c.id
                WHERE hv.elder_id = ?
                ORDER BY hv.timestamp DESC
                LIMIT ?
            ''', (elder_id, limit))
            
            vitals = cursor.fetchall()
            conn.close()
            
            return vitals
            
        except Exception as e:
            print(f"Error getting vitals for elder {elder_id}: {e}")
            return []
    
    def add_vital_reading(self, elder_id: int, vital_type: str, value: str, 
                         unit: str = None, measured_by: int = None, 
                         measurement_method: str = 'manual', notes: str = None) -> bool:
        """Add a new vital reading"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_vitals 
                (elder_id, vital_type, value, unit, measured_by, measurement_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (elder_id, vital_type, value, unit, measured_by, measurement_method, notes))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error adding vital reading: {e}")
            return False
    
    # === EMERGENCY ALERTS ===
    
    def create_emergency_alert(self, elder_id: int, alert_type: str, severity: str,
                              description: str, location: str = None, 
                              triggered_by: str = 'ai_system') -> int:
        """Create a new emergency alert"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO emergency_alerts 
                (elder_id, alert_type, severity, description, location, triggered_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (elder_id, alert_type, severity, description, location, triggered_by))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return alert_id
            
        except Exception as e:
            print(f"Error creating emergency alert: {e}")
            return 0
    
    def get_active_alerts(self, elder_id: int = None) -> List[Dict[str, Any]]:
        """Get active emergency alerts"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            if elder_id:
                cursor.execute('''
                    SELECT 
                        ea.*, e.name as elder_name, c.name as acknowledged_by_name
                    FROM emergency_alerts ea
                    JOIN elders e ON ea.elder_id = e.id
                    LEFT JOIN caregivers c ON ea.acknowledged_by = c.id
                    WHERE ea.elder_id = ? AND ea.status = 'active'
                    ORDER BY ea.created_at DESC
                ''', (elder_id,))
            else:
                cursor.execute('''
                    SELECT 
                        ea.*, e.name as elder_name, c.name as acknowledged_by_name
                    FROM emergency_alerts ea
                    JOIN elders e ON ea.elder_id = e.id
                    LEFT JOIN caregivers c ON ea.acknowledged_by = c.id
                    WHERE ea.status = 'active'
                    ORDER BY ea.created_at DESC
                ''')
            
            alerts = cursor.fetchall()
            conn.close()
            
            return alerts
            
        except Exception as e:
            print(f"Error getting active alerts: {e}")
            return []
    
    # === INTERACTION LOGS ===
    
    def log_interaction(self, elder_id: int, interaction_type: str, message_content: str,
                       ai_response: str, intent_detected: str = None, 
                       confidence_score: float = None, suggested_action: str = None,
                       mood_assessment: str = None, risk_level: str = 'low',
                       session_id: str = None) -> int:
        """Log an AI interaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interaction_logs 
                (elder_id, interaction_type, message_content, ai_response, intent_detected,
                 confidence_score, suggested_action, mood_assessment, risk_level, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (elder_id, interaction_type, message_content, ai_response, intent_detected,
                  confidence_score, json.dumps(suggested_action) if suggested_action else None,
                  mood_assessment, risk_level, session_id))
            
            log_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return log_id
            
        except Exception as e:
            print(f"Error logging interaction: {e}")
            return 0
    
    def get_recent_interactions(self, elder_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent interactions for an elder"""
        try:
            conn = self.get_connection()
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM interaction_logs 
                WHERE elder_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (elder_id, limit))
            
            interactions = cursor.fetchall()
            conn.close()
            
            # Parse suggested_action JSON
            for interaction in interactions:
                try:
                    if interaction['suggested_action']:
                        interaction['suggested_action'] = json.loads(interaction['suggested_action'])
                except json.JSONDecodeError:
                    interaction['suggested_action'] = None
            
            return interactions
            
        except Exception as e:
            print(f"Error getting interactions for elder {elder_id}: {e}")
            return []
    
    # === DASHBOARD STATISTICS ===
    
    def get_elder_dashboard_stats(self, elder_id: int) -> Dict[str, Any]:
        """Get dashboard statistics for a specific elder"""
        try:
            stats = {
                'total_interactions_today': 0,
                'pending_activities': 0,
                'completed_activities_today': 0,
                'active_alerts': 0,
                'recent_vitals': [],
                'mood_trend': 'stable'
            }
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get today's interactions
            cursor.execute('''
                SELECT COUNT(*) FROM interaction_logs 
                WHERE elder_id = ? AND date(timestamp) = date('now')
            ''', (elder_id,))
            stats['total_interactions_today'] = cursor.fetchone()[0]
            
            # Get pending activities
            cursor.execute('''
                SELECT COUNT(*) FROM care_activities 
                WHERE elder_id = ? AND status = 'pending'
                    AND scheduled_time >= datetime('now', 'start of day')
            ''', (elder_id,))
            stats['pending_activities'] = cursor.fetchone()[0]
            
            # Get completed activities today
            cursor.execute('''
                SELECT COUNT(*) FROM care_activities 
                WHERE elder_id = ? AND status = 'completed'
                    AND date(completed_time) = date('now')
            ''', (elder_id,))
            stats['completed_activities_today'] = cursor.fetchone()[0]
            
            # Get active alerts
            cursor.execute('''
                SELECT COUNT(*) FROM emergency_alerts 
                WHERE elder_id = ? AND status = 'active'
            ''', (elder_id,))
            stats['active_alerts'] = cursor.fetchone()[0]
            
            conn.close()
            
            # Get recent vitals
            stats['recent_vitals'] = self.get_recent_vitals(elder_id, 5)
            
            return stats
            
        except Exception as e:
            print(f"Error getting dashboard stats for elder {elder_id}: {e}")
            return {}
    
    def get_facility_dashboard_stats(self) -> Dict[str, Any]:
        """Get overall facility dashboard statistics"""
        try:
            stats = {
                'total_elders': 0,
                'total_active_alerts': 0,
                'total_pending_activities': 0,
                'elders_with_interactions_today': 0,
                'recent_alerts': [],
                'activity_summary': {}
            }
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total active elders
            cursor.execute('SELECT COUNT(*) FROM elders WHERE is_active = 1')
            stats['total_elders'] = cursor.fetchone()[0]
            
            # Total active alerts
            cursor.execute('SELECT COUNT(*) FROM emergency_alerts WHERE status = "active"')
            stats['total_active_alerts'] = cursor.fetchone()[0]
            
            # Total pending activities for today
            cursor.execute('''
                SELECT COUNT(*) FROM care_activities 
                WHERE status = 'pending' AND date(scheduled_time) = date('now')
            ''')
            stats['total_pending_activities'] = cursor.fetchone()[0]
            
            # Elders with interactions today
            cursor.execute('''
                SELECT COUNT(DISTINCT elder_id) FROM interaction_logs 
                WHERE date(timestamp) = date('now')
            ''')
            stats['elders_with_interactions_today'] = cursor.fetchone()[0]
            
            conn.close()
            
            # Get recent alerts
            stats['recent_alerts'] = self.get_active_alerts()[:10]
            
            return stats
            
        except Exception as e:
            print(f"Error getting facility dashboard stats: {e}")
            return {}
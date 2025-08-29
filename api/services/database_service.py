import mysql.connector
from mysql.connector import Error
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from contextlib import contextmanager

class DatabaseService:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'eldercare_db'),
            'user': os.getenv('DB_USER', 'eldercare_user'),
            'password': os.getenv('DB_PASSWORD', 'eldercare_pass'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'autocommit': True,
            'charset': 'utf8mb4'
        }
        self.connection = None
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            print(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    async def initialize(self):
        """Initialize database connection and verify schema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                print("✓ Database connection established")
                return True
        except Error as e:
            print(f"⚠ Database initialization failed: {e}")
            return False
    
    # Elder management methods
    async def get_elder_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get elder profile by name"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT u.id, u.first_name, u.last_name, u.phone, u.email,
                           ep.date_of_birth, ep.address, ep.emergency_contacts,
                           ep.medical_record_number, ep.mobility_level, ep.living_situation
                    FROM users u
                    JOIN elder_profiles ep ON u.id = ep.user_id
                    WHERE CONCAT(u.first_name, ' ', u.last_name) = %s OR u.first_name = %s
                    AND u.user_type = 'elder' AND u.is_active = TRUE
                """
                cursor.execute(query, (name, name))
                result = cursor.fetchone()
                
                if result:
                    # Calculate age from date_of_birth
                    if result['date_of_birth']:
                        today = datetime.now().date()
                        birth_date = result['date_of_birth']
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        result['age'] = age
                    
                    # Parse JSON fields
                    if result['emergency_contacts']:
                        result['emergency_contacts'] = json.loads(result['emergency_contacts']) if isinstance(result['emergency_contacts'], str) else result['emergency_contacts']
                    if result['address']:
                        result['address'] = json.loads(result['address']) if isinstance(result['address'], str) else result['address']
                    
                    result['name'] = f"{result['first_name']} {result['last_name']}"
                    result['location'] = result['address'].get('city', 'Home') if result['address'] else 'Home'
                
                return result
                
        except Error as e:
            print(f"Error getting elder by name: {e}")
            return None
    
    async def create_or_update_elder(self, elder_info: Dict[str, Any]) -> str:
        """Create or update elder profile, return elder_id"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if elder exists
                existing_elder = await self.get_elder_by_name(elder_info['name'])
                
                if existing_elder:
                    return existing_elder['id']
                
                # Create new elder
                user_id = str(uuid.uuid4())
                name_parts = elder_info['name'].split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Insert into users table
                user_query = """
                    INSERT INTO users (id, first_name, last_name, phone, user_type, is_active)
                    VALUES (%s, %s, %s, %s, 'elder', TRUE)
                """
                cursor.execute(user_query, (user_id, first_name, last_name, elder_info.get('phone')))
                
                # Insert into elder_profiles table
                profile_query = """
                    INSERT INTO elder_profiles (user_id, address, emergency_contacts, living_situation)
                    VALUES (%s, %s, %s, %s)
                """
                address_json = json.dumps({'city': elder_info.get('location', 'Home')})
                emergency_contacts_json = json.dumps(elder_info.get('emergency_contacts', []))
                
                cursor.execute(profile_query, (user_id, address_json, emergency_contacts_json, 'independent'))
                
                return user_id
                
        except Error as e:
            print(f"Error creating/updating elder: {e}")
            return None
    
    # Message persistence methods
    async def save_chat_message(self, elder_id: str, message_data: Dict[str, Any]) -> bool:
        """Save chat message to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                message_id = str(uuid.uuid4())
                query = """
                    INSERT INTO elder_interactions 
                    (id, elder_id, interaction_type, input_content, ai_response, 
                     intent_detected, confidence_score, emotion_detected, 
                     mental_health_indicators, suggested_actions, emergency_triggered)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    message_id,
                    elder_id,
                    message_data.get('message_type', 'text'),
                    message_data.get('content', ''),
                    message_data.get('ai_response', ''),
                    message_data.get('intent_detected'),
                    message_data.get('confidence_score'),
                    message_data.get('emotion_detected'),
                    json.dumps(message_data.get('mental_health_assessment', {})),
                    json.dumps(message_data.get('suggested_action', {})),
                    message_data.get('is_emergency', False)
                ))
                
                return True
                
        except Error as e:
            print(f"Error saving chat message: {e}")
            return False
    
    async def get_chat_history(self, elder_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for elder"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT * FROM elder_interactions 
                    WHERE elder_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """
                cursor.execute(query, (elder_id, limit))
                results = cursor.fetchall()
                
                # Parse JSON fields
                for result in results:
                    if result.get('mental_health_indicators'):
                        result['mental_health_indicators'] = json.loads(result['mental_health_indicators'])
                    if result.get('suggested_actions'):
                        result['suggested_actions'] = json.loads(result['suggested_actions'])
                
                return results
                
        except Error as e:
            print(f"Error getting chat history: {e}")
            return []
    
    # Activity logging methods
    async def log_activity(self, elder_id: str, activity_data: Dict[str, Any]) -> bool:
        """Log activity detection result"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                activity_id = str(uuid.uuid4())
                query = """
                    INSERT INTO activity_logs 
                    (id, elder_id, activity_type, confidence_score, description, 
                     location, duration_seconds, anomaly_score, is_anomaly, 
                     ai_model_used, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    activity_id,
                    elder_id,
                    activity_data.get('activity_type'),
                    activity_data.get('confidence_score', 0.0),
                    activity_data.get('description', ''),
                    activity_data.get('location', 'Home'),
                    activity_data.get('duration_seconds', 0),
                    activity_data.get('anomaly_score', 0.0),
                    activity_data.get('is_anomaly', False),
                    activity_data.get('ai_model_used', 'unknown'),
                    json.dumps(activity_data.get('metadata', {}))
                ))
                
                return True
                
        except Error as e:
            print(f"Error logging activity: {e}")
            return False
    
    # Emergency alert methods
    async def create_emergency_alert(self, elder_id: str, alert_data: Dict[str, Any]) -> str:
        """Create emergency alert"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                alert_id = str(uuid.uuid4())
                query = """
                    INSERT INTO anomaly_alerts 
                    (id, elder_id, alert_type_id, severity, title, description, 
                     alert_data, location, triggered_by, triggered_at)
                    VALUES (%s, %s, 
                            (SELECT id FROM alert_types WHERE alert_code = %s), 
                            %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    alert_id,
                    elder_id,
                    alert_data.get('alert_code', 'EMERGENCY_BUTTON'),
                    alert_data.get('severity', 'high'),
                    alert_data.get('title', 'Emergency Alert'),
                    alert_data.get('description', ''),
                    json.dumps(alert_data),
                    alert_data.get('location', 'Home'),
                    alert_data.get('triggered_by', 'manual'),
                    datetime.now()
                ))
                
                return alert_id
                
        except Error as e:
            print(f"Error creating emergency alert: {e}")
            return None
    
    async def get_elder_caregivers(self, elder_id: str) -> List[Dict[str, Any]]:
        """Get caregivers for elder for notifications"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT u.id, u.first_name, u.last_name, u.email, u.phone,
                           eca.assignment_type, eca.access_level, eca.permissions
                    FROM users u
                    JOIN caregiver_profiles cp ON u.id = cp.user_id
                    JOIN elder_caregiver_assignments eca ON cp.id = eca.caregiver_id
                    WHERE eca.elder_id = %s AND eca.is_active = TRUE
                """
                cursor.execute(query, (elder_id,))
                results = cursor.fetchall()
                
                # Parse JSON permissions
                for result in results:
                    if result.get('permissions'):
                        result['permissions'] = json.loads(result['permissions'])
                
                return results
                
        except Error as e:
            print(f"Error getting elder caregivers: {e}")
            return []
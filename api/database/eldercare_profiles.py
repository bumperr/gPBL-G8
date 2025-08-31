import sqlite3
import os
from datetime import datetime

def create_eldercare_database():
    """Create eldercare profiles database with comprehensive elder information"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'eldercare.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create elders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            profile_image TEXT,
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            family_contact_name TEXT,
            family_contact_phone TEXT,
            medical_conditions TEXT, -- JSON string of conditions
            medications TEXT, -- JSON string of medications
            allergies TEXT, -- JSON string of allergies
            preferred_language TEXT DEFAULT 'en',
            care_level TEXT DEFAULT 'independent', -- independent, assisted, supervised
            room_location TEXT,
            bed_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create caregivers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caregivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT, -- nurse, doctor, family_member, aide
            phone_number TEXT,
            email TEXT,
            shift_start TIME,
            shift_end TIME,
            specialization TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create elder_caregiver assignments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elder_caregiver (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elder_id INTEGER,
            caregiver_id INTEGER,
            relationship TEXT, -- primary, secondary, emergency, family
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (elder_id) REFERENCES elders (id),
            FOREIGN KEY (caregiver_id) REFERENCES caregivers (id)
        )
    ''')
    
    # Create care_activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS care_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elder_id INTEGER,
            activity_type TEXT, -- medication, meal, exercise, social, medical_check
            description TEXT,
            scheduled_time TIMESTAMP,
            completed_time TIMESTAMP,
            completed_by INTEGER, -- caregiver_id
            status TEXT DEFAULT 'pending', -- pending, completed, missed, cancelled
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (elder_id) REFERENCES elders (id),
            FOREIGN KEY (completed_by) REFERENCES caregivers (id)
        )
    ''')
    
    # Create interaction_logs table for AI conversations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elder_id INTEGER,
            interaction_type TEXT, -- text, voice, video, emergency
            message_content TEXT,
            ai_response TEXT,
            intent_detected TEXT,
            confidence_score REAL,
            suggested_action TEXT, -- JSON string
            mood_assessment TEXT,
            risk_level TEXT, -- low, medium, high
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            FOREIGN KEY (elder_id) REFERENCES elders (id)
        )
    ''')
    
    # Create health_vitals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elder_id INTEGER,
            vital_type TEXT, -- blood_pressure, heart_rate, temperature, oxygen_saturation, weight, glucose
            value TEXT, -- Can store ranges like "120/80" or single values
            unit TEXT,
            measured_by INTEGER, -- caregiver_id or NULL for self-reported
            measurement_method TEXT, -- manual, automatic_sensor, self_reported
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (elder_id) REFERENCES elders (id),
            FOREIGN KEY (measured_by) REFERENCES caregivers (id)
        )
    ''')
    
    # Create emergency_alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elder_id INTEGER,
            alert_type TEXT, -- fall, medical, panic_button, ai_detected
            severity TEXT, -- low, medium, high, critical
            description TEXT,
            location TEXT,
            triggered_by TEXT, -- ai_system, manual, sensor, button
            acknowledged_by INTEGER, -- caregiver_id
            acknowledged_at TIMESTAMP,
            resolved_at TIMESTAMP,
            resolution_notes TEXT,
            status TEXT DEFAULT 'active', -- active, acknowledged, resolved, false_alarm
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (elder_id) REFERENCES elders (id),
            FOREIGN KEY (acknowledged_by) REFERENCES caregivers (id)
        )
    ''')
    
    # Create camera_analytics table for activity tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camera_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elder_id INTEGER,
            camera_id INTEGER DEFAULT 0,
            image_path TEXT, -- path to captured frame
            image_base64 TEXT, -- base64 encoded image for quick display
            activity_detected TEXT, -- walking, sitting, standing, sleeping, eating, etc.
            activity_type TEXT, -- normal, unusual, alert, emergency
            confidence_score REAL DEFAULT 0.0, -- AI confidence 0-1
            location TEXT, -- room location
            duration_seconds INTEGER DEFAULT 0, -- how long the activity lasted
            anomaly_detected BOOLEAN DEFAULT FALSE,
            ai_analysis TEXT, -- detailed AI analysis of the activity
            metadata TEXT, -- JSON string with additional data
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            FOREIGN KEY (elder_id) REFERENCES elders (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Eldercare database created successfully!")
    return db_path

def populate_sample_data():
    """Populate database with sample eldercare data"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'eldercare.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM camera_analytics')
    cursor.execute('DELETE FROM interaction_logs')
    cursor.execute('DELETE FROM emergency_alerts') 
    cursor.execute('DELETE FROM health_vitals')
    cursor.execute('DELETE FROM care_activities')
    cursor.execute('DELETE FROM elder_caregiver')
    cursor.execute('DELETE FROM caregivers')
    cursor.execute('DELETE FROM elders')
    
    # Sample elders data - John and Sarah
    elders_data = [
        (
            'John', 78, 'male', '/images/profiles/john.jpg',
            'Sarah', '+6011468550', 'Sarah', '+6011468550',
            '["hypertension", "mild_dementia", "arthritis"]',
            '["lisinopril_10mg_daily", "acetaminophen_as_needed", "multivitamin"]',
            '["penicillin", "shellfish"]',
            'en', 'assisted', 'Living Room', 'Main Area'
        )
    ]
    
    cursor.executemany('''
        INSERT INTO elders (
            name, age, gender, profile_image, emergency_contact_name, emergency_contact_phone,
            family_contact_name, family_contact_phone, medical_conditions, medications, allergies,
            preferred_language, care_level, room_location, bed_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', elders_data)
    
    # Sample caregivers data
    caregivers_data = [
        ('Sarah', 'caregiver', '+6011468550', 'sarah@eldercare.com', '08:00:00', '20:00:00', 'elderly_care')
    ]
    
    cursor.executemany('''
        INSERT INTO caregivers (name, role, phone_number, email, shift_start, shift_end, specialization)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', caregivers_data)
    
    # Sample elder-caregiver assignments
    assignments_data = [
        (1, 1, 'primary')  # John -> Sarah
    ]
    
    cursor.executemany('''
        INSERT INTO elder_caregiver (elder_id, caregiver_id, relationship)
        VALUES (?, ?, ?)
    ''', assignments_data)
    
    # Sample care activities
    activities_data = [
        (1, 'medication', 'Morning medications - Lisinopril, Multivitamin', datetime(2024, 1, 1, 8, 0), None, None, 'pending', None),
        (1, 'meal', 'Breakfast', datetime(2024, 1, 1, 8, 30), None, None, 'pending', None),
        (1, 'social', 'Chat with Sarah (caregiver)', datetime(2024, 1, 1, 14, 0), None, None, 'pending', None)
    ]
    
    cursor.executemany('''
        INSERT INTO care_activities (elder_id, activity_type, description, scheduled_time, completed_time, completed_by, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', activities_data)
    
    # Sample camera analytics data - 10 different activities over the past week
    import random
    from datetime import timedelta
    
    base_time = datetime.now()
    analytics_data = [
        # Normal daily activities
        (1, 0, None, None, 'walking', 'normal', 0.95, 'Living Room', 120, False, 
         'Elder walking steadily from sofa to kitchen area. Normal gait pattern observed.', 
         '{"steps_estimated": 15, "speed": "normal", "balance": "good"}', 
         base_time - timedelta(hours=2)),
        
        (1, 0, None, None, 'sitting', 'normal', 0.98, 'Living Room', 1800, False,
         'Elder sitting comfortably on sofa, watching TV. Relaxed posture maintained.',
         '{"posture": "relaxed", "activity": "watching_tv"}',
         base_time - timedelta(hours=3)),
        
        (1, 1, None, None, 'eating', 'normal', 0.92, 'Kitchen', 900, False,
         'Elder eating meal at kitchen table. Normal eating patterns observed.',
         '{"meal_duration": "15min", "eating_pace": "normal"}',
         base_time - timedelta(hours=5)),
        
        (1, 0, None, None, 'standing', 'normal', 0.88, 'Living Room', 45, False,
         'Elder standing up from chair, brief pause for balance before walking.',
         '{"balance_check": True, "assistance_needed": False}',
         base_time - timedelta(hours=8)),
        
        # Potentially concerning activities
        (1, 0, None, None, 'restless_movement', 'unusual', 0.78, 'Living Room', 600, True,
         'Elder showing restless movement patterns, frequent position changes. May indicate discomfort.',
         '{"position_changes": 8, "duration": "10min", "possible_cause": "discomfort"}',
         base_time - timedelta(hours=12)),
        
        (1, 1, None, None, 'prolonged_standing', 'alert', 0.85, 'Kitchen', 1200, True,
         'Elder standing at kitchen counter for extended period without movement. Monitoring needed.',
         '{"duration": "20min", "movement": "minimal", "risk_level": "medium"}',
         base_time - timedelta(days=1, hours=2)),
        
        # Nighttime activities
        (1, 0, None, None, 'nighttime_wandering', 'alert', 0.82, 'Living Room', 300, True,
         'Elder moving around living room at 2 AM. Possible confusion or bathroom needs.',
         '{"time": "02:15", "pattern": "wandering", "safety_concern": True}',
         base_time - timedelta(days=1, hours=18)),
        
        (1, 0, None, None, 'sleeping', 'normal', 0.94, 'Living Room', 28800, False,
         'Elder sleeping peacefully on recliner. Normal sleep posture and duration.',
         '{"sleep_quality": "good", "duration_hours": 8, "disturbances": 0}',
         base_time - timedelta(days=2, hours=8)),
        
        # Emergency/concerning events
        (1, 0, None, None, 'unsteady_walking', 'alert', 0.75, 'Living Room', 180, True,
         'Elder showing unsteady gait, using furniture for support. Fall risk assessment needed.',
         '{"support_used": True, "fall_risk": "high", "medical_check_recommended": True}',
         base_time - timedelta(days=3, hours=4)),
        
        (1, 1, None, None, 'sudden_sitting', 'emergency', 0.88, 'Kitchen', 60, True,
         'Elder suddenly sat down while preparing food. Possible dizziness or weakness episode.',
         '{"sudden_movement": True, "medical_attention": "recommended", "vital_check_needed": True}',
         base_time - timedelta(days=4, hours=6))
    ]
    
    cursor.executemany('''
        INSERT INTO camera_analytics (
            elder_id, camera_id, image_path, image_base64, activity_detected, activity_type, 
            confidence_score, location, duration_seconds, anomaly_detected, ai_analysis, 
            metadata, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', analytics_data)
    
    conn.commit()
    conn.close()
    
    print("Sample eldercare data populated successfully!")

if __name__ == "__main__":
    create_eldercare_database()
    populate_sample_data()
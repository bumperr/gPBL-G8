-- MySQL Database Schema for Eldercare System
-- Generated based on the codebase analysis

-- Create database
CREATE DATABASE IF NOT EXISTS eldercare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eldercare_db;

-- Create database user (run these commands as root/admin)
-- CREATE USER IF NOT EXISTS 'eldercare_user'@'localhost' IDENTIFIED BY 'eldercare_pass';
-- GRANT ALL PRIVILEGES ON eldercare_db.* TO 'eldercare_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Users table (base table for all users: elders, caregivers, admins)
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    user_type ENUM('elder', 'caregiver', 'admin', 'family') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_type (user_type),
    INDEX idx_is_active (is_active),
    INDEX idx_name (first_name, last_name)
);

-- Elder profiles (specific data for elder users)
CREATE TABLE elder_profiles (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) UNIQUE NOT NULL,
    date_of_birth DATE,
    address JSON,
    emergency_contacts JSON,
    medical_conditions JSON,
    medications JSON,
    care_preferences JSON,
    medical_record_number VARCHAR(50),
    mobility_level ENUM('independent', 'assisted', 'wheelchair', 'bedridden') DEFAULT 'independent',
    living_situation ENUM('independent', 'assisted_living', 'nursing_home', 'family_home') DEFAULT 'independent',
    cognitive_status ENUM('normal', 'mild_impairment', 'moderate_impairment', 'severe_impairment') DEFAULT 'normal',
    fall_risk_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'low',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_mobility_level (mobility_level),
    INDEX idx_living_situation (living_situation)
);

-- Caregiver profiles
CREATE TABLE caregiver_profiles (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) UNIQUE NOT NULL,
    license_number VARCHAR(50),
    specializations JSON,
    qualifications JSON,
    work_schedule JSON,
    contact_preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Elder-Caregiver assignments
CREATE TABLE elder_caregiver_assignments (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    elder_id VARCHAR(36) NOT NULL,
    caregiver_id VARCHAR(36) NOT NULL,
    assignment_type ENUM('primary', 'secondary', 'emergency', 'family') NOT NULL,
    access_level ENUM('full', 'limited', 'view_only') DEFAULT 'limited',
    permissions JSON,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (elder_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (caregiver_id) REFERENCES caregiver_profiles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (elder_id, caregiver_id),
    INDEX idx_elder_assignments (elder_id),
    INDEX idx_caregiver_assignments (caregiver_id),
    INDEX idx_assignment_type (assignment_type)
);

-- Elder interactions (chat messages, speech transcriptions, AI responses)
CREATE TABLE elder_interactions (
    id VARCHAR(36) PRIMARY KEY,
    elder_id VARCHAR(36) NOT NULL,
    interaction_type ENUM('text', 'speech', 'system') NOT NULL,
    input_content TEXT,
    ai_response TEXT,
    intent_detected VARCHAR(100),
    confidence_score DECIMAL(3,2),
    emotion_detected VARCHAR(50),
    mental_health_indicators JSON,
    suggested_actions JSON,
    emergency_triggered BOOLEAN DEFAULT FALSE,
    response_time_ms INT,
    ai_model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (elder_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_elder_interactions (elder_id),
    INDEX idx_interaction_type (interaction_type),
    INDEX idx_emergency (emergency_triggered),
    INDEX idx_created_at (created_at),
    INDEX idx_intent (intent_detected)
);

-- Activity logs (movement detection, daily activities)
CREATE TABLE activity_logs (
    id VARCHAR(36) PRIMARY KEY,
    elder_id VARCHAR(36) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(3,2),
    description TEXT,
    location VARCHAR(100) DEFAULT 'Home',
    duration_seconds INT DEFAULT 0,
    anomaly_score DECIMAL(3,2) DEFAULT 0.0,
    is_anomaly BOOLEAN DEFAULT FALSE,
    ai_model_used VARCHAR(50),
    metadata JSON,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (elder_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_elder_activities (elder_id),
    INDEX idx_activity_type (activity_type),
    INDEX idx_anomaly (is_anomaly),
    INDEX idx_detected_at (detected_at)
);

-- Alert types (predefined alert categories)
CREATE TABLE alert_types (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    alert_code VARCHAR(50) UNIQUE NOT NULL,
    alert_name VARCHAR(100) NOT NULL,
    description TEXT,
    default_severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    auto_escalation BOOLEAN DEFAULT FALSE,
    escalation_minutes INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomaly alerts (emergency alerts, health alerts, behavioral alerts)
CREATE TABLE anomaly_alerts (
    id VARCHAR(36) PRIMARY KEY,
    elder_id VARCHAR(36) NOT NULL,
    alert_type_id VARCHAR(36) NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    status ENUM('active', 'acknowledged', 'resolved', 'false_positive') DEFAULT 'active',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    alert_data JSON,
    location VARCHAR(100),
    triggered_by VARCHAR(100),
    triggered_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP NULL,
    resolved_at TIMESTAMP NULL,
    acknowledged_by VARCHAR(36),
    resolved_by VARCHAR(36),
    notes TEXT,
    
    FOREIGN KEY (elder_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (alert_type_id) REFERENCES alert_types(id),
    FOREIGN KEY (acknowledged_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_elder_alerts (elder_id),
    INDEX idx_alert_status (status),
    INDEX idx_severity (severity),
    INDEX idx_triggered_at (triggered_at)
);

-- Health metrics (vital signs, medication tracking, wellness data)
CREATE TABLE health_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    elder_id VARCHAR(36) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value VARCHAR(100) NOT NULL,
    unit VARCHAR(20),
    normal_range_min DECIMAL(10,2),
    normal_range_max DECIMAL(10,2),
    is_critical BOOLEAN DEFAULT FALSE,
    notes TEXT,
    recorded_by VARCHAR(36),
    device_id VARCHAR(100),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (elder_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_elder_metrics (elder_id),
    INDEX idx_metric_type (metric_type),
    INDEX idx_recorded_at (recorded_at),
    INDEX idx_critical (is_critical)
);

-- Smart home device commands and status
CREATE TABLE smart_home_commands (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    elder_id VARCHAR(36) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    device_id VARCHAR(100),
    command VARCHAR(100) NOT NULL,
    parameters JSON,
    room VARCHAR(50),
    status ENUM('pending', 'executed', 'failed', 'timeout') DEFAULT 'pending',
    executed_at TIMESTAMP NULL,
    response_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (elder_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_elder_commands (elder_id),
    INDEX idx_device_type (device_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- MQTT message logs (for debugging and audit trail)
CREATE TABLE mqtt_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    topic VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    elder_id VARCHAR(36),
    message_type ENUM('command', 'status', 'alert', 'health', 'activity') NOT NULL,
    direction ENUM('inbound', 'outbound') NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (elder_id) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_topic (topic),
    INDEX idx_elder_mqtt (elder_id),
    INDEX idx_message_type (message_type),
    INDEX idx_processed (processed),
    INDEX idx_created_at (created_at)
);

-- System configurations
CREATE TABLE system_config (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    updated_by VARCHAR(36),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert default alert types
INSERT INTO alert_types (alert_code, alert_name, description, default_severity, auto_escalation) VALUES
('FALL_DETECTED', 'Fall Detection', 'Potential fall detected by AI analysis', 'high', TRUE),
('EMERGENCY_BUTTON', 'Emergency Button', 'Manual emergency button pressed', 'critical', TRUE),
('INACTIVITY_EXTENDED', 'Extended Inactivity', 'No movement detected for extended period', 'medium', TRUE),
('HEALTH_CRITICAL', 'Critical Health Reading', 'Health metric outside critical range', 'critical', TRUE),
('MEDICATION_MISSED', 'Missed Medication', 'Medication not taken at scheduled time', 'medium', FALSE),
('UNUSUAL_BEHAVIOR', 'Unusual Behavior', 'AI detected unusual behavioral pattern', 'medium', FALSE),
('DEVICE_OFFLINE', 'Device Offline', 'Monitoring device lost connection', 'low', FALSE),
('GEOFENCE_VIOLATION', 'Left Safe Area', 'Elder left designated safe area', 'high', TRUE);

-- Insert sample system configurations
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('ai_response_timeout', '30000', 'number', 'AI response timeout in milliseconds'),
('emergency_escalation_minutes', '15', 'number', 'Minutes before emergency alert escalation'),
('inactivity_threshold_hours', '4', 'number', 'Hours of inactivity before alert'),
('fall_detection_sensitivity', '0.8', 'number', 'Fall detection confidence threshold'),
('mqtt_keepalive', '60', 'number', 'MQTT connection keepalive seconds'),
('supported_languages', '["en", "es", "fr", "de"]', 'json', 'Supported speech recognition languages'),
('default_ai_model', 'whisper', 'string', 'Default speech-to-text model');
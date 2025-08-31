import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple

class DeviceService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'devices.db')
        
    def get_connection(self):
        """Get database connection with row factory for dict-like access"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all active devices with their basic information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, room, mqtt_topic, device_type, description
            FROM devices 
            WHERE is_active = 1
            ORDER BY category, room, name
        ''')
        
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices
    
    def get_device_by_id(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get specific device by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM devices WHERE id = ? AND is_active = 1
        ''', (device_id,))
        
        row = cursor.fetchone()
        device = dict(row) if row else None
        conn.close()
        return device
    
    def get_device_actions(self, device_id: int) -> List[Dict[str, Any]]:
        """Get all actions for a specific device"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM device_actions WHERE device_id = ?
            ORDER BY action_name
        ''', (device_id,))
        
        actions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return actions
    
    def find_device_by_keyword(self, text: str) -> List[Dict[str, Any]]:
        """Find devices based on keywords in the text"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        text_lower = text.lower()
        
        cursor.execute('''
            SELECT DISTINCT d.*, dk.keyword, dk.context
            FROM devices d
            JOIN device_keywords dk ON d.id = dk.device_id
            WHERE d.is_active = 1 AND LOWER(?) LIKE '%' || LOWER(dk.keyword) || '%'
            ORDER BY LENGTH(dk.keyword) DESC
        ''', (text,))
        
        matches = []
        seen_devices = set()
        
        for row in cursor.fetchall():
            device_id = row['id']
            if device_id not in seen_devices:
                device_data = dict(row)
                device_data['matched_keyword'] = row['keyword']
                device_data['match_context'] = row['context']
                matches.append(device_data)
                seen_devices.add(device_id)
        
        conn.close()
        return matches
    
    def get_device_action(self, device_id: int, action_name: str) -> Optional[Dict[str, Any]]:
        """Get specific action for a device"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM device_actions 
            WHERE device_id = ? AND action_name = ?
        ''', (device_id, action_name))
        
        row = cursor.fetchone()
        action = dict(row) if row else None
        conn.close()
        return action
    
    def find_best_action(self, device_id: int, action_text: str) -> Optional[Dict[str, Any]]:
        """Find the best matching action for a device based on text"""
        actions = self.get_device_actions(device_id)
        action_text_lower = action_text.lower()
        
        # Direct action name matches
        for action in actions:
            if action['action_name'].lower() in action_text_lower:
                return action
        
        # Keyword-based matching
        action_keywords = {
            'turn_on': ['on', 'turn on', 'switch on', 'start', 'activate'],
            'turn_off': ['off', 'turn off', 'switch off', 'stop', 'deactivate'],
            'dim': ['dim', 'lower', 'reduce brightness'],
            'brighten': ['bright', 'brighten', 'increase brightness'],
            'set_temperature': ['temperature', 'temp', 'degrees'],
            'volume_up': ['volume up', 'louder', 'increase volume'],
            'volume_down': ['volume down', 'quieter', 'decrease volume'],
            'lock': ['lock'],
            'unlock': ['unlock'],
            'arm': ['arm', 'activate security'],
            'disarm': ['disarm', 'deactivate security']
        }
        
        for action in actions:
            action_name = action['action_name']
            if action_name in action_keywords:
                for keyword in action_keywords[action_name]:
                    if keyword in action_text_lower:
                        return action
        
        # Default to first available action
        return actions[0] if actions else None
    
    def get_mqtt_command(self, device_id: int, action_name: str, custom_value: str = None) -> Optional[Tuple[str, str]]:
        """Get MQTT topic and payload for a device action"""
        device = self.get_device_by_id(device_id)
        action = self.get_device_action(device_id, action_name)
        
        if not device or not action:
            return None
        
        topic = device['mqtt_topic']
        payload = custom_value or action['mqtt_payload']
        
        return topic, payload
    
    def get_devices_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all devices in a specific category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM devices 
            WHERE category = ? AND is_active = 1
            ORDER BY room, name
        ''', (category,))
        
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices
    
    def get_devices_by_room(self, room: str) -> List[Dict[str, Any]]:
        """Get all devices in a specific room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM devices 
            WHERE room = ? AND is_active = 1
            ORDER BY category, name
        ''', (room,))
        
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices
    
    def search_devices(self, query: str) -> List[Dict[str, Any]]:
        """Search devices by name, category, room, or description"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query_pattern = f'%{query.lower()}%'
        
        cursor.execute('''
            SELECT DISTINCT d.*
            FROM devices d
            LEFT JOIN device_keywords dk ON d.id = dk.device_id
            WHERE d.is_active = 1 AND (
                LOWER(d.name) LIKE ? OR
                LOWER(d.category) LIKE ? OR
                LOWER(d.room) LIKE ? OR
                LOWER(d.description) LIKE ? OR
                LOWER(dk.keyword) LIKE ?
            )
            ORDER BY d.category, d.room, d.name
        ''', (query_pattern, query_pattern, query_pattern, query_pattern, query_pattern))
        
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices
    
    def get_device_summary(self) -> Dict[str, Any]:
        """Get summary statistics about devices"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count devices by category
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM devices 
            WHERE is_active = 1
            GROUP BY category
            ORDER BY count DESC
        ''')
        categories = {row['category']: row['count'] for row in cursor.fetchall()}
        
        # Count devices by room
        cursor.execute('''
            SELECT room, COUNT(*) as count
            FROM devices 
            WHERE is_active = 1
            GROUP BY room
            ORDER BY count DESC
        ''')
        rooms = {row['room']: row['count'] for row in cursor.fetchall()}
        
        # Total counts
        cursor.execute('SELECT COUNT(*) as total FROM devices WHERE is_active = 1')
        total_devices = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM device_actions')
        total_actions = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            'total_devices': total_devices,
            'total_actions': total_actions,
            'categories': categories,
            'rooms': rooms
        }
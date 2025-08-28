# MQTT Topics Structure for Elder Care Smart Home Integration

## Overview
This document outlines the structured MQTT topics implemented in the Elder Care Assistant API for seamless smart home integration with platforms like Home Assistant, Node-RED, and OpenHAB.

## Topic Structure

### 1. Commands (AI → Smart Home)
**Pattern:** `eldercare/commands/{device_type}/{action}`

**Device Types:**
- `lights` - Smart lighting control
- `thermostat` - Temperature control
- `locks` - Door/window locks
- `security` - Security systems
- `entertainment` - TV, music systems
- `appliances` - Kitchen/household appliances

**Examples:**
```
eldercare/commands/lights/turn_on
eldercare/commands/lights/turn_off
eldercare/commands/lights/set_brightness
eldercare/commands/thermostat/set_temperature
eldercare/commands/locks/lock
eldercare/commands/locks/unlock
eldercare/commands/security/arm
eldercare/commands/security/disarm
```

**Payload Structure:**
```json
{
  "elder_name": "john_doe",
  "device_type": "lights",
  "action": "turn_on",
  "parameters": {
    "brightness": 75,
    "color": "warm_white"
  },
  "room": "living_room",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "ai_assistant"
}
```

### 2. Emergency Alerts (AI → Caregivers/Emergency Services)
**Pattern:** `eldercare/emergency/{severity}`

**Severity Levels:**
- `critical` - Life-threatening emergencies
- `high` - Urgent medical attention needed
- `medium` - Health concerns, non-urgent
- `low` - Informational alerts

**Examples:**
```
eldercare/emergency/critical
eldercare/emergency/high
eldercare/emergency/medium
eldercare/emergency/low
```

**Payload Structure:**
```json
{
  "elder_name": "jane_smith",
  "message": "Fall detected in bathroom",
  "severity": "high",
  "location": "bathroom",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "ai_assistant",
  "requires_response": true
}
```

### 3. Health Monitoring (Sensors → AI → Caregivers)
**Pattern:** `eldercare/health/{metric}`

**Health Metrics:**
- `heart_rate` - Heart rate monitoring
- `blood_pressure` - Blood pressure readings
- `medication` - Medication adherence
- `sleep` - Sleep quality/duration
- `steps` - Daily activity/steps
- `weight` - Weight measurements
- `temperature` - Body temperature

**Examples:**
```
eldercare/health/heart_rate
eldercare/health/blood_pressure
eldercare/health/medication
eldercare/health/sleep
```

**Payload Structure:**
```json
{
  "elder_name": "bob_johnson",
  "metric_type": "heart_rate",
  "value": 78,
  "unit": "bpm",
  "timestamp": "2024-01-15T10:30:00Z",
  "notes": "Morning reading",
  "source": "ai_assistant"
}
```

### 4. Status Updates (AI → Dashboard)
**Pattern:** `eldercare/status/{elder_name}/{status_type}`

**Status Types:**
- `activity` - Current activity level
- `location` - Current location in home
- `mood` - Detected emotional state
- `emergency` - Emergency status
- `health` - Overall health status

**Examples:**
```
eldercare/status/john_doe/activity
eldercare/status/jane_smith/location
eldercare/status/bob_johnson/mood
```

**Payload Structure:**
```json
{
  "elder_name": "john_doe",
  "status_type": "activity",
  "status_value": "active",
  "confidence": 0.85,
  "timestamp": "2024-01-15T10:30:00Z",
  "additional_data": {
    "last_movement": "2024-01-15T10:25:00Z",
    "room": "kitchen"
  },
  "source": "ai_assistant"
}
```

### 5. Device Responses (Smart Home → AI)
**Pattern:** `eldercare/responses/{device_type}/{elder_name}`

**Examples:**
```
eldercare/responses/lights/john_doe
eldercare/responses/thermostat/jane_smith
eldercare/responses/locks/bob_johnson
```

**Payload Structure:**
```json
{
  "status": "success",
  "elder_name": "john_doe",
  "device_type": "lights",
  "action": "turn_on",
  "timestamp": "2024-01-15T10:30:00Z",
  "executed": true,
  "error": null
}
```

### 6. Voice Data (Backup/Analysis)
**Pattern:** `eldercare/voice/{type}/{elder_name}`

**Types:**
- `raw` - Original audio data
- `processed` - Transcribed text

**Examples:**
```
eldercare/voice/raw/john_doe
eldercare/voice/processed/jane_smith
```

## API Endpoints

### New MQTT Endpoints Added:
- `POST /mqtt/commands/smarthome` - Send structured smart home commands
- `POST /mqtt/health/metric` - Send health metrics
- `POST /mqtt/status/elder` - Send elder status updates
- `POST /mqtt/emergency/structured` - Send structured emergency alerts
- `GET /mqtt/topics` - Get all available topics and structure

### Example Usage:

**Send Smart Home Command:**
```bash
curl -X POST "http://localhost:8000/mqtt/commands/smarthome" \
-H "Content-Type: application/json" \
-d '{
  "elder_name": "john_doe",
  "device_type": "lights",
  "action": "turn_on",
  "parameters": {"brightness": 80},
  "room": "bedroom"
}'
```

**Send Health Metric:**
```bash
curl -X POST "http://localhost:8000/mqtt/health/metric" \
-H "Content-Type: application/json" \
-d '{
  "elder_name": "jane_smith",
  "metric_type": "heart_rate",
  "value": 75,
  "unit": "bpm"
}'
```

## Integration Platforms

### Home Assistant Integration
- Use MQTT discovery or manual configuration
- Subscribe to `eldercare/#` for all messages
- Create automations based on structured topics
- See `integration_examples/home_assistant_config.yaml`

### Node-RED Integration
- Create flows subscribing to topic patterns
- Process JSON payloads and route to device controls
- Implement health monitoring and alerting
- See `integration_examples/node_red_flows.json`

### OpenHAB Integration
- Configure MQTT binding with `eldercare` prefix
- Create Things and Items based on topic structure
- Use Rules for automation and alerting

## Best Practices

1. **Topic Naming:** Use lowercase, underscores for spaces
2. **Payload Format:** Always use JSON with consistent structure
3. **Timestamps:** Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
4. **Elder Names:** Use consistent identifiers (e.g., first_last format)
5. **Error Handling:** Include error fields in response payloads
6. **Logging:** Publish to log topics for debugging and analysis
7. **Security:** Use MQTT authentication and TLS in production
8. **Quality of Service:** Use QoS 2 for critical emergency messages

## Message Flow Example

```
1. Elder says: "Turn on the bedroom lights"
2. AI processes speech → eldercare/commands/lights/turn_on
3. Home Assistant receives command → turns on bedroom lights
4. Home Assistant confirms → eldercare/responses/lights/john_doe
5. AI receives confirmation → provides audio feedback to elder
```

This structured approach ensures reliable, scalable smart home integration while maintaining clear separation of concerns between AI processing and device control.
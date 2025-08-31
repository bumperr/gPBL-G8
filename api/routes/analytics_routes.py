from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List
import sqlite3
import os
from datetime import datetime, timedelta
import json
from api.services.ai_service import AIService

router = APIRouter(prefix="/analytics", tags=["Camera Analytics"])

# Initialize AI service for behavioral analysis
ai_service = AIService()

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'eldercare.db')
    return sqlite3.connect(db_path)

@router.get("/camera/{elder_id}")
async def get_camera_analytics(
    elder_id: int,
    period: str = Query("week", description="Filter period: day, week, month, all"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type: normal, unusual, alert, emergency"),
    limit: int = Query(50, description="Maximum number of records to return")
):
    """Get camera analytics data with filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build date filter based on period
        date_filter = ""
        if period == "day":
            date_filter = "AND timestamp >= datetime('now', '-1 day')"
        elif period == "week":
            date_filter = "AND timestamp >= datetime('now', '-7 days')"
        elif period == "month":
            date_filter = "AND timestamp >= datetime('now', '-30 days')"
        
        # Build activity type filter
        activity_filter = ""
        if activity_type:
            activity_filter = f"AND activity_type = '{activity_type}'"
        
        query = f"""
            SELECT 
                id, elder_id, camera_id, image_path, image_base64, activity_detected, 
                activity_type, confidence_score, location, duration_seconds, 
                anomaly_detected, ai_analysis, metadata, timestamp, processed_at
            FROM camera_analytics 
            WHERE elder_id = ? 
            {date_filter} 
            {activity_filter}
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        
        cursor.execute(query, (elder_id, limit))
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        columns = [desc[0] for desc in cursor.description]
        analytics = []
        
        for row in rows:
            record = dict(zip(columns, row))
            # Parse metadata JSON
            if record['metadata']:
                try:
                    record['metadata'] = json.loads(record['metadata'])
                except json.JSONDecodeError:
                    record['metadata'] = {}
            
            # Format timestamps
            if record['timestamp']:
                record['timestamp'] = record['timestamp']
            if record['processed_at']:
                record['processed_at'] = record['processed_at']
            
            analytics.append(record)
        
        conn.close()
        
        # Get summary statistics
        stats = await get_analytics_summary(elder_id, period, activity_type)
        
        return {
            "success": True,
            "elder_id": elder_id,
            "period": period,
            "activity_type": activity_type,
            "total_records": len(analytics),
            "analytics": analytics,
            "summary": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@router.get("/summary/{elder_id}")
async def get_analytics_summary(
    elder_id: int,
    period: str = Query("week", description="Summary period: day, week, month, all"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type")
):
    """Get analytics summary and statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build date filter
        date_filter = ""
        if period == "day":
            date_filter = "AND timestamp >= datetime('now', '-1 day')"
        elif period == "week":
            date_filter = "AND timestamp >= datetime('now', '-7 days')"
        elif period == "month":
            date_filter = "AND timestamp >= datetime('now', '-30 days')"
        
        # Build activity type filter
        activity_filter = ""
        if activity_type:
            activity_filter = f"AND activity_type = '{activity_type}'"
        
        # Get activity counts by type
        cursor.execute(f"""
            SELECT activity_type, COUNT(*) as count
            FROM camera_analytics 
            WHERE elder_id = ? {date_filter} {activity_filter}
            GROUP BY activity_type
            ORDER BY count DESC
        """, (elder_id,))
        
        activity_counts = dict(cursor.fetchall())
        
        # Get most common activities
        cursor.execute(f"""
            SELECT activity_detected, COUNT(*) as count
            FROM camera_analytics 
            WHERE elder_id = ? {date_filter} {activity_filter}
            GROUP BY activity_detected
            ORDER BY count DESC
            LIMIT 5
        """, (elder_id,))
        
        common_activities = dict(cursor.fetchall())
        
        # Get anomaly statistics
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_activities,
                SUM(CASE WHEN anomaly_detected = 1 THEN 1 ELSE 0 END) as anomalies,
                AVG(confidence_score) as avg_confidence,
                AVG(duration_seconds) as avg_duration
            FROM camera_analytics 
            WHERE elder_id = ? {date_filter} {activity_filter}
        """, (elder_id,))
        
        stats_row = cursor.fetchone()
        
        # Get hourly distribution for pattern analysis
        cursor.execute(f"""
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as activity_count
            FROM camera_analytics 
            WHERE elder_id = ? {date_filter} {activity_filter}
            GROUP BY strftime('%H', timestamp)
            ORDER BY hour
        """, (elder_id,))
        
        hourly_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        # Calculate statistics
        total_activities = stats_row[0] or 0
        anomalies = stats_row[1] or 0
        avg_confidence = round(stats_row[2] or 0, 2)
        avg_duration = round((stats_row[3] or 0) / 60, 1)  # Convert to minutes
        
        anomaly_rate = round((anomalies / total_activities * 100), 1) if total_activities > 0 else 0
        
        return {
            "success": True,
            "elder_id": elder_id,
            "period": period,
            "statistics": {
                "total_activities": total_activities,
                "anomalies_detected": anomalies,
                "anomaly_rate_percent": anomaly_rate,
                "average_confidence": avg_confidence,
                "average_duration_minutes": avg_duration
            },
            "activity_breakdown": activity_counts,
            "common_activities": common_activities,
            "hourly_distribution": hourly_distribution
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.get("/ai-analysis/{elder_id}")
async def get_ai_behavioral_analysis(
    elder_id: int,
    period: str = Query("week", description="Analysis period: day, week, month"),
    include_recommendations: bool = Query(True, description="Include care recommendations")
):
    """Get AI-powered behavioral analysis and recommendations"""
    try:
        # Get analytics data
        analytics_response = await get_camera_analytics(elder_id, period, None, 100)
        analytics = analytics_response["analytics"]
        summary = analytics_response["summary"]
        
        if not analytics:
            return {
                "success": False,
                "message": "No analytics data available for the specified period"
            }
        
        # Prepare data for AI analysis
        analysis_prompt = f"""
        You are an expert geriatric care analyst. Analyze the following elder monitoring data for behavioral patterns, anomalies, and care recommendations.

        Elder ID: {elder_id}
        Analysis Period: {period}
        
        Summary Statistics:
        - Total Activities: {summary['statistics']['total_activities']}
        - Anomalies Detected: {summary['statistics']['anomalies_detected']} ({summary['statistics']['anomaly_rate_percent']}%)
        - Average Activity Confidence: {summary['statistics']['average_confidence']}
        
        Activity Breakdown: {json.dumps(summary['activity_breakdown'], indent=2)}
        Common Activities: {json.dumps(summary['common_activities'], indent=2)}
        Hourly Distribution: {json.dumps(summary['hourly_distribution'], indent=2)}
        
        Recent Activity Details:
        """
        
        # Add detailed activity information
        for activity in analytics[:10]:  # Focus on most recent 10 activities
            analysis_prompt += f"""
        - Time: {activity['timestamp']} | Activity: {activity['activity_detected']} | Type: {activity['activity_type']} | Location: {activity['location']} | Duration: {activity['duration_seconds']}s | Anomaly: {activity['anomaly_detected']} | Analysis: {activity['ai_analysis']}
        """
        
        analysis_prompt += """
        
        Please provide a comprehensive behavioral analysis including:
        1. Overall behavioral patterns and trends
        2. Identification of concerning patterns or anomalies
        3. Sleep and daily routine assessment
        4. Risk factors and safety concerns
        5. Care recommendations for caregivers
        6. Suggested monitoring adjustments
        
        Format your response as a structured analysis with clear sections.
        """
        
        # Get AI analysis
        ai_response = await ai_service.chat_completion(
            analysis_prompt,
            model="gemma:2b"  # Use a fast model for analysis
        )
        
        return {
            "success": True,
            "elder_id": elder_id,
            "analysis_period": period,
            "generated_at": datetime.now().isoformat(),
            "summary_statistics": summary["statistics"],
            "ai_behavioral_analysis": ai_response["response"],
            "confidence_score": ai_response.get("confidence", 0.8),
            "recommendations_included": include_recommendations,
            "data_points_analyzed": len(analytics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI analysis: {str(e)}")

@router.post("/add-activity")
async def add_camera_activity(
    elder_id: int,
    camera_id: int,
    activity_detected: str,
    activity_type: str,
    location: str,
    duration_seconds: int = 0,
    confidence_score: float = 0.0,
    anomaly_detected: bool = False,
    ai_analysis: str = "",
    metadata: dict = None,
    image_base64: str = None
):
    """Add a new camera analytics record"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else "{}"
        
        cursor.execute("""
            INSERT INTO camera_analytics (
                elder_id, camera_id, image_base64, activity_detected, activity_type,
                confidence_score, location, duration_seconds, anomaly_detected,
                ai_analysis, metadata, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            elder_id, camera_id, image_base64, activity_detected, activity_type,
            confidence_score, location, duration_seconds, anomaly_detected,
            ai_analysis, metadata_json, datetime.now().isoformat()
        ))
        
        activity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "activity_id": activity_id,
            "message": "Camera activity recorded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding activity: {str(e)}")

@router.delete("/activity/{activity_id}")
async def delete_camera_activity(activity_id: int):
    """Delete a camera analytics record"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM camera_analytics WHERE id = ?", (activity_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Activity record not found")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Activity record deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting activity: {str(e)}")

@router.get("/activity-types")
async def get_activity_types():
    """Get available activity types and categories"""
    return {
        "activity_types": {
            "normal": {
                "color": "#4CAF50",
                "description": "Regular daily activities",
                "examples": ["walking", "sitting", "eating", "sleeping", "standing"]
            },
            "unusual": {
                "color": "#FF9800", 
                "description": "Unusual but not immediately concerning",
                "examples": ["restless_movement", "unusual_posture", "off_schedule_activity"]
            },
            "alert": {
                "color": "#F44336",
                "description": "Activities requiring attention",
                "examples": ["prolonged_standing", "nighttime_wandering", "unsteady_walking"]
            },
            "emergency": {
                "color": "#D32F2F",
                "description": "Emergency situations requiring immediate response", 
                "examples": ["fall_detected", "medical_emergency", "no_movement_extended"]
            }
        },
        "common_activities": [
            "walking", "sitting", "standing", "sleeping", "eating", "reading",
            "watching_tv", "using_phone", "restless_movement", "unsteady_walking",
            "prolonged_standing", "nighttime_wandering", "sudden_sitting", "fall_detected"
        ],
        "locations": ["Living Room", "Kitchen", "Bedroom", "Bathroom", "Hallway", "Garden"]
    }
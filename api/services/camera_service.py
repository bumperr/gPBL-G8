import cv2
import base64
import asyncio
import json
from typing import Optional, Dict, List
import threading
import time
from datetime import datetime
import numpy as np

class CameraService:
    def __init__(self):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.active_streams: Dict[int, bool] = {}
        self.latest_frames: Dict[int, str] = {}
        self.camera_info: List[Dict] = []
        self.streaming_threads: Dict[int, threading.Thread] = {}
        
    def get_available_cameras(self) -> List[Dict]:
        """Get list of available camera devices and video samples - simplified for demo"""
        print("Getting available cameras and video samples...")
        
        # Always provide virtual demo cameras for tunneling demo
        available_cameras = [
            {
                "id": 0,
                "name": "Demo Camera (Virtual)",
                "width": 640,
                "height": 480,
                "fps": 15,
                "available": True,
                "virtual": True,
                "type": "camera"
            },
            {
                "id": 1, 
                "name": "Security Camera (Virtual)",
                "width": 640,
                "height": 480,
                "fps": 15,
                "available": True,
                "virtual": True,
                "type": "camera"
            },
            # Add real video samples for VLM demonstration
            {
                "id": 100,
                "name": "ADL Activities Sample (ADL-2.mp4)",
                "width": 640,
                "height": 480,
                "fps": 30,
                "available": True,
                "virtual": False,
                "type": "video_sample",
                "description": "Real eldercare video showing Activities of Daily Living (ADL) for VLM analysis",
                "duration": 180,  # Approx 3 minutes
                "video_file": "ADL-2.mp4"
            },
            {
                "id": 101,
                "name": "Fall Detection Sample 1 (fall-1.mp4)", 
                "width": 640,
                "height": 480,
                "fps": 30,
                "available": True,
                "virtual": False,
                "type": "video_sample",
                "description": "Real fall detection demonstration video for emergency scenario analysis",
                "duration": 120,  # Approx 2 minutes
                "video_file": "fall-1.mp4"
            },
            {
                "id": 102,
                "name": "Fall Detection Sample 2 (fall-2.mp4)",
                "width": 640,
                "height": 480, 
                "fps": 30,
                "available": True,
                "virtual": False,
                "type": "video_sample",
                "description": "Additional fall detection video for comprehensive emergency analysis",
                "duration": 90,  # Approx 1.5 minutes
                "video_file": "fall-2.mp4"
            }
        ]
        
        # Try to detect one real camera quickly (with timeout)
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Camera detection timeout")
            
            # Set 3 second timeout for camera detection on Windows (skip signal on Windows)
            try:
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                # Quick test read
                ret, frame = cap.read()
                if ret and frame is not None:
                    print("Found physical camera 0")
                    available_cameras[0] = {
                        "id": 0,
                        "name": "Physical Camera 0",
                        "width": 640,
                        "height": 480,
                        "fps": 30,
                        "available": True,
                        "virtual": False
                    }
                cap.release()
            except:
                print("No physical camera found, using virtual cameras only")
                
        except Exception as e:
            print(f"Camera detection error: {e}, using virtual cameras")
        
        self.camera_info = available_cameras
        print(f"Available cameras: {[c['name'] for c in available_cameras]}")
        return available_cameras
    
    def start_camera_stream(self, camera_id: int = 0) -> bool:
        """Start streaming from a specific camera"""
        try:
            if camera_id in self.active_streams and self.active_streams[camera_id]:
                print(f"Camera {camera_id} is already streaming")
                return True
            
            print(f"Starting camera stream for camera {camera_id}")
            
            # Check if this camera is virtual
            camera_info = next((c for c in self.camera_info if c['id'] == camera_id), None)
            if not camera_info:
                # Default to virtual if not found
                camera_info = {"virtual": True}
            
            if camera_info.get('virtual', True):
                print(f"Starting virtual camera/video sample {camera_id}")
                self.active_streams[camera_id] = True
                
                # Determine if it's a video sample or regular virtual camera
                if camera_info.get('type') == 'video_sample':
                    if camera_info.get('video_file'):
                        # Stream real video file
                        stream_thread = threading.Thread(
                            target=self._stream_real_video_file,
                            args=(camera_id, camera_info.get('video_file')),
                            daemon=True
                        )
                    else:
                        # Stream virtual video sample
                        stream_thread = threading.Thread(
                            target=self._stream_video_sample,
                            args=(camera_id,),
                            daemon=True
                        )
                else:
                    # Start regular virtual camera streaming thread
                    stream_thread = threading.Thread(
                        target=self._stream_virtual_frames,
                        args=(camera_id,),
                        daemon=True
                    )
                
                stream_thread.start()
                self.streaming_threads[camera_id] = stream_thread
                
                print(f"Virtual camera/video sample {camera_id} streaming started successfully")
                return True
            else:
                # Try physical camera
                cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    print(f"Failed to open camera {camera_id}, falling back to virtual")
                    return self.start_camera_stream(999)  # Fallback to virtual
                
                # Set camera properties
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                self.cameras[camera_id] = cap
                self.active_streams[camera_id] = True
                
                # Start streaming thread
                stream_thread = threading.Thread(
                    target=self._stream_physical_frames,
                    args=(camera_id,),
                    daemon=True
                )
                stream_thread.start()
                self.streaming_threads[camera_id] = stream_thread
                
                print(f"Physical camera {camera_id} streaming started successfully")
                return True
                
        except Exception as e:
            print(f"Error starting camera {camera_id}: {e}")
            return False
    
    def stop_camera_stream(self, camera_id: int) -> bool:
        """Stop streaming from a specific camera"""
        try:
            if camera_id in self.active_streams:
                self.active_streams[camera_id] = False
                
            if camera_id in self.cameras:
                self.cameras[camera_id].release()
                del self.cameras[camera_id]
                
            if camera_id in self.latest_frames:
                del self.latest_frames[camera_id]
                
            if camera_id in self.streaming_threads:
                del self.streaming_threads[camera_id]
                
            print(f"Camera {camera_id} streaming stopped")
            return True
            
        except Exception as e:
            print(f"Error stopping camera {camera_id}: {e}")
            return False
    
    def _stream_physical_frames(self, camera_id: int):
        """Stream frames from physical camera"""
        cap = self.cameras[camera_id]
        
        while self.active_streams.get(camera_id, False):
            try:
                ret, frame = cap.read()
                if not ret:
                    print(f"Failed to read frame from camera {camera_id}")
                    break
                
                # Add timestamp overlay
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cv2.putText(frame, f'Elder Care Monitor - {timestamp}', (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Store latest frame
                self.latest_frames[camera_id] = frame_base64
                
                # Control frame rate
                time.sleep(1/15)  # ~15 FPS
                
            except Exception as e:
                print(f"Error in physical streaming thread for camera {camera_id}: {e}")
                break
        
        print(f"Physical streaming thread for camera {camera_id} ended")
        
    def _stream_virtual_frames(self, camera_id: int):
        """Stream virtual demo frames"""
        frame_count = 0
        
        while self.active_streams.get(camera_id, False):
            try:
                # Create different virtual scenes based on camera ID
                if camera_id == 0:
                    # Living room scene
                    frame = self._create_living_room_scene(frame_count)
                elif camera_id == 1:
                    # Kitchen scene  
                    frame = self._create_kitchen_scene(frame_count)
                else:
                    # Default scene
                    frame = self._create_default_scene(frame_count)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Store latest frame
                self.latest_frames[camera_id] = frame_base64
                
                frame_count += 1
                time.sleep(1/15)  # ~15 FPS for virtual camera
                
            except Exception as e:
                print(f"Error in virtual streaming thread for camera {camera_id}: {e}")
                break
        
        print(f"Virtual streaming thread for camera {camera_id} ended")
    
    def _stream_video_sample(self, camera_id: int):
        """Stream video sample frames with realistic elder care scenarios"""
        frame_count = 0
        scenario_duration = 450  # 30 seconds per scenario at 15fps
        
        while self.active_streams.get(camera_id, False):
            try:
                # Determine which video sample scenario to show
                if camera_id == 100:  # Elder Activities Sample
                    frame = self._create_elder_activities_sample(frame_count)
                elif camera_id == 101:  # Fall Detection Demo
                    frame = self._create_fall_detection_sample(frame_count)
                elif camera_id == 102:  # Daily Routine Analysis
                    frame = self._create_daily_routine_sample(frame_count)
                else:
                    # Default to activities sample
                    frame = self._create_elder_activities_sample(frame_count)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Store latest frame
                self.latest_frames[camera_id] = frame_base64
                
                # Every 15 seconds (225 frames at 15fps), trigger VLM analysis
                if frame_count > 0 and frame_count % 225 == 0:
                    self._trigger_vlm_analysis(camera_id, frame_base64, frame_count)
                
                frame_count += 1
                time.sleep(1/15)  # ~15 FPS for video samples
                
            except Exception as e:
                print(f"Error in video sample streaming thread for camera {camera_id}: {e}")
                break
        
        print(f"Video sample streaming thread for camera {camera_id} ended")
    
    def _stream_real_video_file(self, camera_id: int, video_filename: str):
        """Stream frames from real video files in video_sample folder"""
        import os
        
        # Path to video file
        video_path = os.path.join(os.path.dirname(__file__), '..', '..', 'video_sample', video_filename)
        
        try:
            # Open video file with OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print(f"Error: Could not open video file {video_path}")
                # Fallback to virtual streaming
                return self._stream_video_sample(camera_id)
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"Streaming real video: {video_filename}, FPS: {fps}, Total frames: {total_frames}")
            
            frame_count = 0
            loop_count = 0
            
            while self.active_streams.get(camera_id, False):
                ret, frame = cap.read()
                
                if not ret:
                    # Loop the video
                    loop_count += 1
                    print(f"Video {video_filename} completed loop {loop_count}, restarting...")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    frame_count = 0
                    
                    if not ret:
                        print(f"Error: Cannot read video file {video_path}")
                        break
                
                try:
                    # Resize frame if needed
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Add eldercare monitoring overlay
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    cv2.putText(frame, f'Real Video Analysis: {video_filename}', (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f'Time: {timestamp} | Loop: {loop_count}', (10, 60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    cv2.putText(frame, f'Frame: {frame_count} | VLM Analysis Active', (10, 90), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
                    
                    # VLM analysis indicator
                    if frame_count % 225 < 30:  # Flash for 2 seconds after each analysis
                        cv2.putText(frame, 'REAL VLM ANALYZING...', (300, 60), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 255), 2)
                    
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Store latest frame
                    self.latest_frames[camera_id] = frame_base64
                    
                    # Every 15 seconds (225 frames at 15fps), trigger VLM analysis
                    if frame_count > 0 and frame_count % 225 == 0:
                        self._trigger_vlm_analysis(camera_id, frame_base64, frame_count)
                    
                    frame_count += 1
                    
                    # Control frame rate (15 FPS for consistent analysis)
                    time.sleep(1/15)
                    
                except Exception as e:
                    print(f"Error processing frame from {video_filename}: {e}")
                    continue
            
            cap.release()
            print(f"Real video streaming thread for {video_filename} ended")
            
        except Exception as e:
            print(f"Error in real video streaming for {video_filename}: {e}")
            # Fallback to virtual streaming
            return self._stream_video_sample(camera_id)
    
    def _create_elder_activities_sample(self, frame_count):
        """Create realistic elder activities sample video frames"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (45, 55, 45)  # Slightly greenish background for home environment
        
        # Simulate different activities based on frame count
        cycle = (frame_count // 150) % 6  # Change activity every 10 seconds
        
        # Add room furniture
        # Sofa
        cv2.rectangle(frame, (50, 300), (200, 400), (101, 67, 33), -1)
        # TV
        cv2.rectangle(frame, (500, 200), (620, 320), (30, 30, 30), -1)
        cv2.rectangle(frame, (510, 210), (610, 310), (50, 50, 200), -1)
        # Table
        cv2.rectangle(frame, (250, 350), (350, 380), (139, 119, 101), -1)
        
        # Simulate different elder activities
        if cycle == 0:  # Walking
            person_x = int(100 + 200 * (frame_count % 150) / 150)
            person_y = 350
            activity = "Walking across room"
            cv2.circle(frame, (person_x, person_y), 25, (200, 180, 160), -1)
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+70), (100, 150, 200), -1)
        elif cycle == 1:  # Sitting on sofa
            person_x, person_y = 125, 320
            activity = "Sitting and resting"
            cv2.circle(frame, (person_x, person_y), 25, (200, 180, 160), -1)
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+50), (100, 150, 200), -1)
        elif cycle == 2:  # Standing at table
            person_x, person_y = 300, 330
            activity = "Standing at table"
            cv2.circle(frame, (person_x, person_y), 25, (200, 180, 160), -1)
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+70), (100, 150, 200), -1)
        elif cycle == 3:  # Watching TV
            person_x, person_y = 400, 350
            activity = "Watching television"
            cv2.circle(frame, (person_x, person_y), 25, (200, 180, 160), -1)
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+70), (100, 150, 200), -1)
        elif cycle == 4:  # Slow movement (potential concern)
            person_x = int(200 + 50 * np.sin(frame_count * 0.02))
            person_y = 360
            activity = "Slow/unsteady movement"
            cv2.circle(frame, (person_x, person_y), 25, (200, 160, 140), -1)  # Slightly different color
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+70), (120, 130, 180), -1)
        else:  # Resting/minimal movement
            person_x, person_y = 150, 370
            activity = "Minimal movement/resting"
            cv2.circle(frame, (person_x, person_y), 25, (200, 180, 160), -1)
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+60), (100, 150, 200), -1)
        
        # Add timestamp and activity info
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, 'Elder Activities Sample - VLM Analysis Demo', (20, 30), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f'Time: {timestamp}', (20, 60), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f'Activity: {activity}', (20, 90), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
        cv2.putText(frame, f'Frame: {frame_count}', (20, 120), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        # VLM analysis indicator
        if frame_count % 225 < 30:  # Flash for 2 seconds after each analysis
            cv2.putText(frame, 'VLM ANALYZING...', (400, 60), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 255), 2)
        
        return frame
    
    def _create_fall_detection_sample(self, frame_count):
        """Create fall detection demonstration video frames"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (40, 45, 50)  # Slightly darker for emergency scenarios
        
        # Room elements
        cv2.rectangle(frame, (100, 300), (250, 400), (101, 67, 33), -1)  # Chair
        cv2.rectangle(frame, (400, 350), (500, 380), (139, 119, 101), -1)  # Small table
        
        # Simulate fall detection scenario
        cycle = (frame_count // 225) % 4  # Change scenario every 15 seconds
        
        if cycle == 0:  # Normal walking
            person_x = int(150 + 100 * (frame_count % 225) / 225)
            person_y = 350
            status = "Normal walking"
            color = (200, 180, 160)
            alert_level = "NORMAL"
            alert_color = (100, 255, 100)
        elif cycle == 1:  # Unsteady movement
            person_x = int(300 + 50 * np.sin(frame_count * 0.1))
            person_y = int(350 + 20 * np.sin(frame_count * 0.15))
            status = "Unsteady movement detected"
            color = (200, 160, 120)
            alert_level = "CAUTION" 
            alert_color = (255, 255, 100)
        elif cycle == 2:  # Fall in progress
            fall_progress = (frame_count % 225) / 225
            person_x = 400
            person_y = int(350 + fall_progress * 100)  # Person falling down
            status = "FALL DETECTED!"
            color = (180, 100, 100)
            alert_level = "EMERGENCY"
            alert_color = (255, 100, 100)
        else:  # Person on ground
            person_x, person_y = 400, 450
            status = "Person on ground - Emergency!"
            color = (160, 80, 80)
            alert_level = "CRITICAL"
            alert_color = (255, 50, 50)
        
        # Draw person
        if cycle < 3:
            cv2.circle(frame, (person_x, person_y), 25, color, -1)
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+70), 
                         (color[2], color[1], color[0]), -1)
        else:
            # Person lying down
            cv2.ellipse(frame, (person_x, person_y), (40, 20), 0, 0, 360, color, -1)
        
        # Add emergency detection info
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, 'Fall Detection Demo - VLM Analysis', (20, 30), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f'Time: {timestamp}', (20, 60), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f'Status: {status}', (20, 90), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, alert_color, 2)
        cv2.putText(frame, f'Alert Level: {alert_level}', (20, 120), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, alert_color, 2)
        
        # Emergency indicator
        if cycle >= 2:
            cv2.putText(frame, '🚨 EMERGENCY ALERT 🚨', (200, 150), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 100), 3)
        
        return frame
    
    def _create_daily_routine_sample(self, frame_count):
        """Create daily routine analysis sample video frames"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (50, 45, 40)  # Warmer home environment
        
        # Room setup for daily routine
        # Kitchen counter
        cv2.rectangle(frame, (50, 300), (200, 350), (139, 119, 101), -1)
        # Living area
        cv2.rectangle(frame, (300, 320), (450, 400), (101, 67, 33), -1)  # Sofa
        # Bedroom area
        cv2.rectangle(frame, (500, 280), (600, 380), (80, 60, 40), -1)  # Bed
        
        # Time-based routine simulation
        hour_sim = ((frame_count // 450) % 24)  # Simulate 24-hour cycle
        
        if 6 <= hour_sim < 8:  # Morning routine
            person_x, person_y = 125, 330
            activity = "Morning activities - Kitchen"
            routine_status = "Normal morning routine"
        elif 8 <= hour_sim < 12:  # Morning sitting
            person_x, person_y = 375, 340
            activity = "Sitting/reading"
            routine_status = "Active morning period"
        elif 12 <= hour_sim < 14:  # Lunch time
            person_x, person_y = 125, 330
            activity = "Lunch preparation"
            routine_status = "Meal time activity"
        elif 14 <= hour_sim < 18:  # Afternoon rest
            person_x, person_y = 375, 340
            activity = "Afternoon rest"
            routine_status = "Rest period - normal"
        elif 18 <= hour_sim < 20:  # Evening activity
            person_x, person_y = 200, 350
            activity = "Evening movement"
            routine_status = "Evening routine"
        elif 20 <= hour_sim < 22:  # Pre-sleep
            person_x, person_y = 550, 330
            activity = "Preparing for sleep"
            routine_status = "Evening routine"
        else:  # Night/Sleep
            person_x, person_y = 550, 330
            activity = "Sleeping"
            routine_status = "Sleep period"
        
        # Draw person
        cv2.circle(frame, (person_x, person_y), 25, (200, 180, 160), -1)
        if "sleep" not in activity.lower():
            cv2.rectangle(frame, (person_x-15, person_y+25), (person_x+15, person_y+70), (100, 150, 200), -1)
        else:
            cv2.ellipse(frame, (person_x, person_y+20), (40, 15), 0, 0, 360, (100, 150, 200), -1)
        
        # Add routine analysis info
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, 'Daily Routine Analysis - VLM Demo', (20, 30), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f'Time: {timestamp} (Sim Hour: {hour_sim}:00)', (20, 60), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f'Activity: {activity}', (20, 90), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
        cv2.putText(frame, f'Status: {routine_status}', (20, 120), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 200, 255), 1)
        
        return frame
    
    def _trigger_vlm_analysis(self, camera_id: int, frame_base64: str, frame_count: int):
        """Trigger VLM analysis for 15-second clips"""
        try:
            print(f"Triggering VLM analysis for camera {camera_id} at frame {frame_count}")
            
            # Import VLM service
            from api.services.vlm_service import vlm_service
            
            # Add current frame to VLM buffer
            timestamp = datetime.now().isoformat()
            vlm_service.add_frame_to_buffer(camera_id, frame_base64, timestamp)
            
            # Queue analysis for processing
            vlm_service.queue_analysis(camera_id, elder_id=1)  # Default elder_id
            
            print(f"VLM analysis queued for camera {camera_id}")
            
        except Exception as e:
            print(f"Error triggering VLM analysis: {e}")
    
    def _create_living_room_scene(self, frame_count):
        """Create a living room monitoring scene"""
        # Create base frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (40, 60, 40)  # Dark green background
        
        # Add room elements
        # Sofa
        cv2.rectangle(frame, (100, 300), (300, 400), (101, 67, 33), -1)
        # TV
        cv2.rectangle(frame, (450, 200), (600, 350), (30, 30, 30), -1)
        cv2.rectangle(frame, (460, 210), (590, 340), (50, 50, 200), -1)
        
        # Add person simulation (moving)
        person_x = int(200 + 100 * np.sin(frame_count * 0.05))
        cv2.circle(frame, (person_x, 350), 25, (200, 180, 160), -1)  # Head
        cv2.rectangle(frame, (person_x-15, 375), (person_x+15, 420), (100, 150, 200), -1)  # Body
        
        # Add timestamp and info
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, 'Elder Care - Living Room Monitor', (20, 30), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f'Server Time: {timestamp}', (20, 60), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f'Motion Detected: {"YES" if frame_count % 100 < 50 else "NO"}', (20, 90), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100) if frame_count % 100 < 50 else (200, 200, 200), 1)
        
        # Add vitals simulation
        heart_rate = int(72 + 8 * np.sin(frame_count * 0.1))
        cv2.putText(frame, f'Heart Rate: {heart_rate} BPM', (400, 400), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)
        
        return frame
    
    def _create_kitchen_scene(self, frame_count):
        """Create a kitchen monitoring scene"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (60, 45, 30)  # Kitchen background
        
        # Add kitchen elements
        # Counter
        cv2.rectangle(frame, (50, 350), (590, 450), (139, 119, 101), -1)
        # Stove
        cv2.rectangle(frame, (400, 280), (500, 350), (80, 80, 80), -1)
        cv2.circle(frame, (430, 300), 15, (200, 50, 50), -1)  # Burner
        cv2.circle(frame, (470, 300), 15, (200, 50, 50), -1)  # Burner
        
        # Safety indicators
        stove_on = frame_count % 200 < 30  # Stove on for brief periods
        if stove_on:
            cv2.circle(frame, (430, 300), 20, (255, 100, 100), 3)
            cv2.putText(frame, 'STOVE ON - ALERT!', (200, 250), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 255), 2)
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, 'Elder Care - Kitchen Safety Monitor', (20, 30), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f'Server Time: {timestamp}', (20, 60), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f'Safety Status: {"ALERT" if stove_on else "SAFE"}', (20, 90), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100) if stove_on else (100, 255, 100), 1)
        
        return frame
        
    def _create_default_scene(self, frame_count):
        """Create default test scene"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (30, 50, 70)  # Blue background
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, 'Elder Care Demo Camera', (150, 200), 
                  cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(frame, f'Server Time: {timestamp}', (200, 250), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
        cv2.putText(frame, f'Frame: {frame_count}', (250, 300), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
        
        # Moving element
        center_x = int(320 + 200 * np.sin(frame_count * 0.1))
        cv2.circle(frame, (center_x, 350), 30, (255, 255, 255), -1)
        
        return frame
    
    def get_latest_frame(self, camera_id: int = 0) -> Optional[str]:
        """Get the latest frame from a camera as base64 encoded JPEG"""
        if camera_id in self.latest_frames:
            return self.latest_frames[camera_id]
        return None
    
    def take_snapshot(self, camera_id: int = 0) -> Optional[str]:
        """Take a snapshot from the camera"""
        if camera_id not in self.active_streams or not self.active_streams.get(camera_id, False):
            # Try to start camera if not active
            if not self.start_camera_stream(camera_id):
                return None
            time.sleep(0.5)  # Give camera time to initialize
        
        return self.get_latest_frame(camera_id)
    
    def get_camera_status(self) -> Dict:
        """Get status of all cameras"""
        return {
            "available_cameras": self.camera_info,
            "active_streams": self.active_streams,
            "streaming_cameras": list(self.active_streams.keys()),
            "total_cameras": len(self.camera_info),
            "timestamp": datetime.now().isoformat()
        }
    
    def cleanup(self):
        """Clean up all camera resources"""
        for camera_id in list(self.active_streams.keys()):
            self.stop_camera_stream(camera_id)
        
        for cap in self.cameras.values():
            if cap:
                cap.release()
        
        # Clear all data structures
        self.cameras.clear()
        self.active_streams.clear()
        self.latest_frames.clear()
        self.streaming_threads.clear()
        
        print("Camera service cleaned up")

# Global camera service instance
camera_service = CameraService()
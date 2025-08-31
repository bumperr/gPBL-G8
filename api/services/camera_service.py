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
        """Get list of available camera devices - simplified for demo"""
        print("Getting available cameras...")
        
        # Always provide virtual demo cameras for tunneling demo
        available_cameras = [
            {
                "id": 0,
                "name": "Demo Camera (Virtual)",
                "width": 640,
                "height": 480,
                "fps": 15,
                "available": True,
                "virtual": True
            },
            {
                "id": 1, 
                "name": "Security Camera (Virtual)",
                "width": 640,
                "height": 480,
                "fps": 15,
                "available": True,
                "virtual": True
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
                print(f"Starting virtual camera {camera_id}")
                self.active_streams[camera_id] = True
                
                # Start streaming thread for virtual camera
                stream_thread = threading.Thread(
                    target=self._stream_virtual_frames,
                    args=(camera_id,),
                    daemon=True
                )
                stream_thread.start()
                self.streaming_threads[camera_id] = stream_thread
                
                print(f"Virtual camera {camera_id} streaming started successfully")
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
import { useState, useRef, useCallback } from 'react';

const useAudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState('');
  const [audioBlob, setAudioBlob] = useState(null);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState('');
  
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const startTimeRef = useRef(0);
  const intervalRef = useRef(null);

  const startRecording = useCallback(async () => {
    try {
      setError('');
      
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      });
      
      streamRef.current = stream;
      chunksRef.current = [];
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { 
          type: 'audio/webm;codecs=opus' 
        });
        const audioURL = URL.createObjectURL(audioBlob);
        
        setAudioBlob(audioBlob);
        setAudioURL(audioURL);
        setIsRecording(false);
        
        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        
        // Clear duration timer
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      };
      
      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      startTimeRef.current = Date.now();
      
      // Update duration timer
      intervalRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setDuration(elapsed);
      }, 1000);
      
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording. Please check microphone permissions.');
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  }, [isRecording]);

  const clearRecording = useCallback(() => {
    if (audioURL) {
      URL.revokeObjectURL(audioURL);
    }
    setAudioURL('');
    setAudioBlob(null);
    setDuration(0);
    setError('');
  }, [audioURL]);

  const downloadRecording = useCallback(() => {
    if (audioURL) {
      const a = document.createElement('a');
      a.href = audioURL;
      a.download = `voice-message-${Date.now()}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  }, [audioURL]);

  // Convert audio blob to base64 for API transmission
  const getAudioBase64 = useCallback(() => {
    return new Promise((resolve, reject) => {
      if (!audioBlob) {
        reject(new Error('No audio recording available'));
        return;
      }
      
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result.split(',')[1]; // Remove data:audio/webm;base64, prefix
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(audioBlob);
    });
  }, [audioBlob]);

  // Format duration for display
  const formatDuration = useCallback((seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  return {
    isRecording,
    audioURL,
    audioBlob,
    duration: formatDuration(duration),
    durationSeconds: duration,
    error,
    startRecording,
    stopRecording,
    clearRecording,
    downloadRecording,
    getAudioBase64
  };
};

export default useAudioRecorder;
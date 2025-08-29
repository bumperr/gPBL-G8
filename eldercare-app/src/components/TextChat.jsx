import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Chip,
  Alert,
  IconButton,
  Divider
} from '@mui/material';
import {
  Send,
  Psychology,
  SmartToy,
  Person,
  LightbulbOutlined
} from '@mui/icons-material';
import apiService from '../services/api';

const TextChat = ({ elderInfo, onIntentDetected }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send to enhanced AI service with mental health focus
      const response = await apiService.processElderText(inputMessage, elderInfo);
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.response,
        timestamp: new Date(),
        intentDetected: response.intent_detected,
        suggestedAction: response.suggested_action,
        confidenceScore: response.confidence_score,
        mentalHealthAssessment: response.mental_health_assessment
      };

      setMessages(prev => [...prev, aiMessage]);

      // Notify parent component about detected intent
      if (response.intent_detected && onIntentDetected) {
        onIntentDetected(response);
      }

      // Speak the response
      if ('speechSynthesis' in window && response.response) {
        const utterance = new SpeechSynthesisUtterance(response.response);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        speechSynthesis.speak(utterance);
      }

    } catch (error) {
      console.error('Text chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I'm sorry, I'm having trouble understanding right now. Could you please try again?",
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const getIntentColor = (intent) => {
    const colors = {
      'emergency': '#f44336',
      'health_concern': '#ff9800',
      'loneliness': '#9c27b0',
      'request_help': '#2196f3',
      'conversation': '#4caf50',
      'smart_home': '#607d8b',
      'medication': '#e91e63'
    };
    return colors[intent] || '#757575';
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3, height: '500px', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Psychology color="primary" />
        Text Chat Assistant
      </Typography>
      
      {/* Messages Area */}
      <Box sx={{ flex: 1, overflow: 'auto', mb: 2, p: 1, border: '1px solid #e0e0e0', borderRadius: 2 }}>
        {messages.length === 0 ? (
          <Box sx={{ textAlign: 'center', mt: 4, opacity: 0.6 }}>
            <SmartToy sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="body2">
              Hi {elderInfo?.name || 'there'}! I'm here to chat and provide companionship. 
              Type a message to start our conversation.
            </Typography>
          </Box>
        ) : (
          messages.map((message) => (
            <Box key={message.id} sx={{ mb: 2 }}>
              {/* Message Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {message.type === 'user' ? (
                  <Person sx={{ color: '#2196f3', fontSize: 20 }} />
                ) : (
                  <SmartToy sx={{ color: '#9c27b0', fontSize: 20 }} />
                )}
                <Typography variant="caption" color="text.secondary">
                  {message.type === 'user' ? 'You' : 'AI Assistant'} • {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Box>

              {/* Message Content */}
              <Box sx={{
                p: 2,
                borderRadius: 2,
                backgroundColor: message.type === 'user' ? '#e3f2fd' : '#f3e5f5',
                border: `1px solid ${message.type === 'user' ? '#2196f3' : '#9c27b0'}`,
                ml: message.type === 'user' ? 4 : 0,
                mr: message.type === 'user' ? 0 : 4
              }}>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>

                {/* AI-specific information */}
                {message.type === 'ai' && (
                  <Box sx={{ mt: 2 }}>
                    {/* Intent Detection */}
                    {message.intentDetected && (
                      <Box sx={{ mb: 1 }}>
                        <Chip
                          icon={<LightbulbOutlined />}
                          label={`Intent: ${message.intentDetected.replace('_', ' ').toUpperCase()}`}
                          size="small"
                          sx={{ 
                            backgroundColor: getIntentColor(message.intentDetected),
                            color: 'white',
                            mr: 1
                          }}
                        />
                        {message.confidenceScore && (
                          <Chip
                            label={`Confidence: ${Math.round(message.confidenceScore * 100)}%`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    )}

                    {/* Suggested Action */}
                    {message.suggestedAction && (
                      <Alert severity="info" sx={{ mt: 1, fontSize: '0.875rem' }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          🎯 Detected Intent & Suggested Action:
                        </Typography>
                        <Typography variant="body2">
                          <strong>Function Call:</strong> {message.suggestedAction.function_name}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Parameters:</strong> {JSON.stringify(message.suggestedAction.parameters, null, 2)}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Reason:</strong> {message.suggestedAction.reasoning}
                        </Typography>
                      </Alert>
                    )}

                    {/* Mental Health Assessment */}
                    {message.mentalHealthAssessment && (
                      <Alert 
                        severity={message.mentalHealthAssessment.risk_level === 'high' ? 'error' : 
                                 message.mentalHealthAssessment.risk_level === 'medium' ? 'warning' : 'success'}
                        sx={{ mt: 1, fontSize: '0.875rem' }}
                      >
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          🧠 Mental Health Assessment:
                        </Typography>
                        <Typography variant="body2">
                          <strong>Mood:</strong> {message.mentalHealthAssessment.mood_indicators.join(', ')}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Risk Level:</strong> {message.mentalHealthAssessment.risk_level.toUpperCase()}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Recommendation:</strong> {message.mentalHealthAssessment.recommendations}
                        </Typography>
                      </Alert>
                    )}
                  </Box>
                )}

                {/* Error indicator */}
                {message.isError && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    Connection issue - please try again
                  </Alert>
                )}
              </Box>
            </Box>
          ))
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here... Press Enter to send"
          disabled={isLoading}
          variant="outlined"
          size="small"
        />
        <IconButton
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isLoading}
          color="primary"
          sx={{ 
            backgroundColor: '#2196f3', 
            color: 'white',
            '&:hover': { backgroundColor: '#1976d2' },
            '&:disabled': { backgroundColor: '#e0e0e0' }
          }}
        >
          <Send />
        </IconButton>
      </Box>

      {/* Loading indicator */}
      {isLoading && (
        <Typography variant="caption" sx={{ textAlign: 'center', mt: 1, opacity: 0.7 }}>
          AI is thinking...
        </Typography>
      )}
    </Paper>
  );
};

export default TextChat;
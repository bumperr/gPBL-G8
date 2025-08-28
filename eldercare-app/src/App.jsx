import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert
} from '@mui/material';
import { Person, Dashboard, Warning } from '@mui/icons-material';

import ElderInterface from './pages/ElderInterface';
import CaregiverDashboard from './pages/CaregiverDashboard';

// Create theme with accessibility and mobile-first approach
const theme = createTheme({
  palette: {
    primary: {
      main: '#2196F3',
      light: '#64B5F6',
      dark: '#1976D2',
    },
    secondary: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    button: {
      fontSize: '1rem',
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '12px 24px',
          fontSize: '1rem',
        },
        contained: {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          '&:hover': {
            boxShadow: '0 6px 16px rgba(0, 0, 0, 0.2)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        },
      },
    },
  },
});

// Login/Setup Component
const LoginSetup = ({ onUserSetup }) => {
  const [userType, setUserType] = useState('');
  const [userName, setUserName] = useState('');
  const [userInfo, setUserInfo] = useState({});
  const [error, setError] = useState('');

  const handleSetup = () => {
    if (!userType || !userName.trim()) {
      setError('Please select user type and enter your name');
      return;
    }

    const userData = {
      type: userType,
      name: userName.trim(),
      ...userInfo
    };

    onUserSetup(userData);
  };

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Elder Care Assistant
        </Typography>
        <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Please set up your profile to get started
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FormControl fullWidth>
            <InputLabel>I am a...</InputLabel>
            <Select
              value={userType}
              label="I am a..."
              onChange={(e) => setUserType(e.target.value)}
              size="large"
            >
              <MenuItem value="elder">Elder (Senior)</MenuItem>
              <MenuItem value="caregiver">Caregiver</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Your Name"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            size="large"
          />

          {userType === 'elder' && (
            <>
              <TextField
                fullWidth
                label="Age (Optional)"
                type="number"
                value={userInfo.age || ''}
                onChange={(e) => setUserInfo(prev => ({ ...prev, age: e.target.value }))}
              />
              <TextField
                fullWidth
                label="Emergency Contact (Optional)"
                value={userInfo.emergencyContact || ''}
                onChange={(e) => setUserInfo(prev => ({ ...prev, emergencyContact: e.target.value }))}
              />
            </>
          )}

          {userType === 'caregiver' && (
            <TextField
              fullWidth
              label="Role/Organization (Optional)"
              value={userInfo.role || ''}
              onChange={(e) => setUserInfo(prev => ({ ...prev, role: e.target.value }))}
            />
          )}

          <Button
            variant="contained"
            size="large"
            onClick={handleSetup}
            sx={{ mt: 2, py: 2 }}
            startIcon={userType === 'elder' ? <Person /> : <Dashboard />}
          >
            {userType === 'elder' ? 'Start Elder Interface' : 'Open Caregiver Dashboard'}
          </Button>
        </Box>

        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4 }}>
          This app connects to your smart home system and provides voice assistance for elder care
        </Typography>
      </Paper>
    </Container>
  );
};

// Emergency Alert Component
const EmergencyAlert = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <Alert 
      severity="error" 
      onClose={onDismiss}
      sx={{ 
        position: 'fixed', 
        top: 20, 
        left: 20, 
        right: 20, 
        zIndex: 9999,
        boxShadow: '0 8px 32px rgba(244, 67, 54, 0.3)'
      }}
    >
      <Typography variant="h6" gutterBottom>
        🚨 EMERGENCY ALERT
      </Typography>
      {message}
    </Alert>
  );
};

function App() {
  const [user, setUser] = useState(null);
  const [emergencyAlert, setEmergencyAlert] = useState('');

  // Load user from localStorage on app start
  useEffect(() => {
    const savedUser = localStorage.getItem('eldercare_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Failed to load saved user:', error);
      }
    }
  }, []);

  const handleUserSetup = (userData) => {
    setUser(userData);
    localStorage.setItem('eldercare_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('eldercare_user');
  };

  const handleEmergency = (message) => {
    setEmergencyAlert(message);
    // Auto-dismiss after 10 seconds
    setTimeout(() => setEmergencyAlert(''), 10000);
  };

  if (!user) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ 
          minHeight: '100vh', 
          backgroundColor: 'background.default',
          backgroundImage: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }}>
          <LoginSetup onUserSetup={handleUserSetup} />
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
          {/* App Bar */}
          <AppBar position="sticky" elevation={2}>
            <Toolbar>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                Elder Care Assistant
              </Typography>
              <Typography variant="body2" sx={{ mr: 2 }}>
                {user.name} ({user.type})
              </Typography>
              <Button color="inherit" onClick={handleLogout}>
                Logout
              </Button>
            </Toolbar>
          </AppBar>

          {/* Emergency Alert Overlay */}
          <EmergencyAlert 
            message={emergencyAlert} 
            onDismiss={() => setEmergencyAlert('')} 
          />

          {/* Main Content */}
          <Routes>
            <Route
              path="/"
              element={
                user.type === 'elder' ? (
                  <ElderInterface 
                    elderInfo={user} 
                    onEmergency={handleEmergency}
                  />
                ) : (
                  <CaregiverDashboard 
                    caregiverInfo={user}
                  />
                )
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
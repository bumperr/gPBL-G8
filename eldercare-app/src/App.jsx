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

// Create green theme for eldercare app
const theme = createTheme({
  palette: {
    primary: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#2e7d32',
    },
    secondary: {
      main: '#66bb6a',
      light: '#a5d6a7',
      dark: '#388e3c',
    },
    background: {
      default: '#f1f8e9',
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

// Simple Role Selection Component
const RoleSelection = ({ onUserSetup }) => {
  const [selectedRole, setSelectedRole] = useState('');

  const handleRoleSelect = (role) => {
    const userData = {
      type: role,
      name: role === 'elder' ? 'John' : 'Sarah',
      age: role === 'elder' ? 78 : undefined,
      family_contact_name: role === 'elder' ? 'Sarah' : undefined,
      family_phone: role === 'elder' ? '+6011468550' : undefined,
      emergency_contact_name: role === 'elder' ? 'Sarah' : undefined,
      emergency_contact_phone: role === 'elder' ? '+6011468550' : undefined,
      // Medical information for elder
      medical_conditions: role === 'elder' ? ['hypertension', 'mild dementia', 'arthritis'] : undefined,
      medications: role === 'elder' ? ['Lisinopril 10mg daily', 'Acetaminophen as needed', 'Multivitamin'] : undefined,
      allergies: role === 'elder' ? ['penicillin', 'shellfish'] : undefined,
      care_level: role === 'elder' ? 'assisted' : undefined,
      preferred_language: role === 'elder' ? 'en' : undefined,
      // Caregiver specific fields
      role: role === 'caregiver' ? 'Family Caregiver' : undefined,
      elder_name: role === 'caregiver' ? 'John' : undefined
    };

    onUserSetup(userData);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper 
        elevation={8} 
        sx={{ 
          p: 6, 
          borderRadius: 4,
          background: 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)',
          border: '3px solid #c8e6c9',
          boxShadow: '0 12px 48px rgba(76, 175, 80, 0.3)',
          textAlign: 'center'
        }}
      >
        <Typography 
          variant="h3" 
          align="center" 
          gutterBottom
          sx={{ 
            color: '#2e7d32',
            fontWeight: 'bold',
            mb: 2,
            background: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          🌿 Elder Care Assistant
        </Typography>
        <Typography 
          variant="h6" 
          align="center" 
          sx={{ 
            color: '#388e3c', 
            mb: 6,
            fontWeight: 500
          }}
        >
          Choose your role to get started
        </Typography>

        <Box sx={{ display: 'flex', gap: 4, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Paper
            elevation={4}
            onClick={() => handleRoleSelect('elder')}
            sx={{
              p: 4,
              borderRadius: 4,
              cursor: 'pointer',
              minWidth: 200,
              background: 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)',
              color: 'white',
              transition: 'all 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-8px) scale(1.05)',
                boxShadow: '0 16px 32px rgba(76, 175, 80, 0.4)'
              }
            }}
          >
            <Person sx={{ fontSize: 64, mb: 2 }} />
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
              Elder
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              John, 78 years old
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
              Access AI companion, health monitoring, and smart home control
            </Typography>
          </Paper>

          <Paper
            elevation={4}
            onClick={() => handleRoleSelect('caregiver')}
            sx={{
              p: 4,
              borderRadius: 4,
              cursor: 'pointer',
              minWidth: 200,
              background: 'linear-gradient(135deg, #66bb6a 0%, #81c784 100%)',
              color: 'white',
              transition: 'all 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-8px) scale(1.05)',
                boxShadow: '0 16px 32px rgba(102, 187, 106, 0.4)'
              }
            }}
          >
            <Dashboard sx={{ fontSize: 64, mb: 2 }} />
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
              Caregiver
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              Sarah (Family)
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
              Monitor John's activities, health status, and emergency alerts
            </Typography>
          </Paper>
        </Box>

        <Typography 
          variant="body1" 
          color="text.secondary" 
          align="center" 
          sx={{ 
            mt: 6,
            color: '#2e7d32',
            fontStyle: 'italic'
          }}
        >
          🏠 Smart home integration • 🤖 AI companion • 📱 Emergency alerts
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
          backgroundImage: 'linear-gradient(135deg, #c8e6c9 0%, #e8f5e8 100%)'
        }}>
          <RoleSelection onUserSetup={handleUserSetup} />
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
          {/* App Bar */}
          <AppBar position="sticky" elevation={2} sx={{ 
            background: 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)',
            boxShadow: '0 4px 20px rgba(76, 175, 80, 0.3)'
          }}>
            <Toolbar>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                flexGrow: 1,
                py: 1
              }}>
                <img 
                  src="/logo.png" 
                  alt="Elder Care Assistant" 
                  style={{ 
                    height: '50px',
                    maxWidth: '200px',
                    objectFit: 'contain',
                    filter: 'brightness(1.1) contrast(1.1)'
                  }}
                />
              </Box>
              <Typography variant="body1" sx={{ 
                mr: 2,
                color: 'white',
                fontWeight: 500,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                px: 2,
                py: 0.5,
                borderRadius: 2,
                backdropFilter: 'blur(10px)'
              }}>
                {user.name} ({user.type === 'elder' ? '👴 Elder' : '👩‍⚕️ Caregiver'})
              </Typography>
              <Button 
                color="inherit" 
                onClick={handleLogout}
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    transform: 'scale(1.05)'
                  },
                  borderRadius: 2,
                  px: 3,
                  fontWeight: 'bold',
                  transition: 'all 0.3s ease-in-out'
                }}
              >
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
# Elder Care Mobile Web App

A React-based mobile web application designed for elder care and smart home assistance. This app provides two main interfaces:

1. **Elder Interface** - Simple, accessible interface for seniors with voice recording and emergency features
2. **Caregiver Dashboard** - Monitoring and management interface for caregivers

## Features

### For Elders:
- 🎤 **Voice Recording** - Send voice messages for assistance
- 🆘 **Emergency Button** - One-tap emergency alerts to caregivers  
- 🏠 **Smart Home Control** - Control lights, temperature, locks with simple buttons
- 🔊 **Voice Responses** - AI responses are spoken aloud
- 📱 **Mobile-First Design** - Large buttons and text for easy use

### For Caregivers:
- 📊 **Real-time Monitoring** - View status of multiple elders
- ⚠️ **Alert Management** - Receive and respond to elder requests
- 💓 **Health Monitoring** - Track vital signs and health metrics
- 🤖 **Auto-Response** - Automated responses to common requests
- 📞 **Communication Tools** - Direct calling and messaging features

## Quick Start

### Prerequisites
- Node.js 16+ installed
- FastAPI backend server running (see parent directory)

### Installation

1. **Start Development Server**:
   ```bash
   # Windows
   start-dev.bat
   
   # Or manually:
   npm install
   npm start
   ```

2. **Open in Browser**:
   - Visit `http://localhost:3000`
   - The app will auto-open on mobile-friendly view

3. **Setup Your Profile**:
   - Choose "Elder" or "Caregiver" 
   - Enter your name and details
   - Start using the app!

## Building for Production

```bash
# Windows
build-app.bat

# Or manually:
npm run build
```

The built files will be in the `build/` folder ready for deployment.

## Configuration

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Update settings**:
   - `REACT_APP_API_URL` - Your FastAPI backend URL
   - Other settings as needed

## Mobile App Features

### Elder Interface

**Voice Assistant**:
- Tap and hold to record voice messages
- AI processes requests and responds with voice
- Messages are sent to caregivers via MQTT

**Emergency Features**:
- Large red emergency button
- Sends immediate alerts to all caregivers
- Includes location and elder information

**Smart Home Controls**:
- Turn lights on/off
- Adjust temperature
- Lock/unlock doors
- Call family members

**Accessibility**:
- Large fonts and buttons (44px minimum touch targets)
- High contrast colors
- Voice feedback for all actions
- Simple, clutter-free interface

### Caregiver Dashboard

**Monitoring**:
- Real-time elder status updates
- Health vitals tracking (heart rate, blood pressure, temperature)
- Last activity timestamps
- Location tracking

**Alert Management**:
- Prioritized alert system (high/medium/low)
- Voice message playback
- One-click response options
- Auto-response toggle

**Communication**:
- Direct calling to elders
- Voice announcements to smart home
- MQTT messaging integration

## API Integration

The app connects to your FastAPI backend for:

- **Chat/AI**: `/chat` endpoint for AI responses
- **TTS**: `/tts` endpoint for text-to-speech
- **MQTT**: `/mqtt/send` for real-time messaging
- **Health**: `/health` for system status

## Technology Stack

- **Frontend**: React 18, Material-UI 5
- **Audio**: Web Audio API, MediaRecorder
- **Communication**: Axios, MQTT over WebSocket
- **Styling**: CSS3, Material-UI theming
- **Build**: Create React App, Webpack

## Browser Support

- **Recommended**: Chrome, Safari, Edge (latest versions)
- **Mobile**: iOS Safari, Android Chrome
- **Features**: Requires microphone access for voice recording

## Deployment

### Web Server Deployment
1. Run `build-app.bat` to create production build
2. Upload `build/` folder contents to your web server
3. Configure URL rewriting for single-page app:
   
   **Apache (.htaccess)**:
   ```apache
   Options -MultiViews
   RewriteEngine On
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteRule ^ index.html [QR,L]
   ```
   
   **Nginx**:
   ```nginx
   location / {
     try_files $uri $uri/ /index.html;
   }
   ```

### Mobile App (PWA)
- The app includes a web app manifest for "Add to Home Screen"
- Works offline for basic functionality
- Push notifications can be enabled via service worker

## Security Considerations

- **HTTPS Required**: For microphone access and security
- **CORS**: Configure FastAPI backend to allow your domain
- **Authentication**: Consider adding user authentication for production
- **Data Privacy**: Voice recordings are processed locally when possible

## Troubleshooting

### Common Issues

**Microphone not working**:
- Ensure HTTPS (required for microphone access)
- Check browser permissions
- Try refreshing the page

**Can't connect to backend**:
- Check `REACT_APP_API_URL` in `.env`
- Ensure FastAPI server is running
- Check browser console for CORS errors

**App not responsive on mobile**:
- Clear browser cache
- Check mobile browser compatibility
- Try different mobile browser

### Development Tips

- Use browser developer tools mobile simulation
- Test with actual mobile devices
- Check network tab for API call failures
- Use React DevTools for component debugging

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review browser console errors
- Ensure backend server is running and accessible

## License

This project is licensed under the MIT License - see the LICENSE file for details.
@echo off
echo Starting Elder Care React App...
echo.
echo Installing dependencies if needed...
call npm install

echo.
echo Starting development server...
echo The app will open in your browser at http://localhost:3000
echo.
echo To stop the server, press Ctrl+C
echo.

set BROWSER=none
call npm start

pause
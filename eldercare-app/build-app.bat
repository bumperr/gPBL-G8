@echo off
echo Building Elder Care React App for production...
echo.

echo Installing/updating dependencies...
call npm install

echo.
echo Building production bundle...
call npm run build

echo.
if exist build (
    echo ✅ Build completed successfully!
    echo Built files are in the 'build' folder
    echo.
    echo You can now deploy these files to your web server:
    echo - Copy the contents of 'build' folder to your web server
    echo - Make sure to set up URL rewriting for single-page app routing
    echo.
    echo To test the production build locally:
    echo npx serve -s build -l 3000
    echo.
) else (
    echo ❌ Build failed! Check the error messages above.
)

pause
@echo off
cd /d "%~dp0"
echo Starting map server at http://localhost:8080
echo Open http://localhost:8080/index.html in your browser
python -m http.server 8080

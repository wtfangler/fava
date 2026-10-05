@echo off
setlocal
cd /d "%~dp0"
title Expedition Refined - Server
rem Set JAVA_EXE to the full java.exe path if Java 25 is not on PATH.
if not defined JAVA_EXE set "JAVA_EXE=java"
set "JAVA_VERSION="
for /f "tokens=3" %%v in ('"%JAVA_EXE%" -version 2^>^&1 ^| findstr /i "version"') do if not defined JAVA_VERSION set "JAVA_VERSION=%%~v"
set "JAVA_MAJOR="
for /f "tokens=1 delims=.-+" %%m in ("%JAVA_VERSION%") do set "JAVA_MAJOR=%%m"
if not defined JAVA_MAJOR goto wrongjava
if %JAVA_MAJOR% LSS 25 goto wrongjava
if not exist "fabric-server-launch.jar" (
  echo Missing fabric-server-launch.jar. Complete the server build first.
  exit /b 1
)
"%JAVA_EXE%" -Xms1G -Xmx@RAM@ -XX:+UseG1GC -jar fabric-server-launch.jar nogui
set "SERVER_EXIT=%ERRORLEVEL%"
pause
exit /b %SERVER_EXIT%
:wrongjava
echo Java 25 or newer is required. Found: %JAVA_VERSION%
echo Install Java 25, or set JAVA_EXE to its java.exe path.
pause
exit /b 1

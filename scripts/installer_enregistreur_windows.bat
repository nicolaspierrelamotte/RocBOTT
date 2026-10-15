@echo off
rem Installateur de l'enregistreur Myfxbook (Windows). Double-clic suffit.
rem Ce fichier ne fait que lancer installer_enregistreur_windows.ps1 (meme dossier),
rem sans avoir a changer la politique PowerShell de la machine.
rem Messages en ASCII : la console cmd n'affiche pas bien les accents.
title Installation de l'enregistreur Myfxbook (RocBOTT)
if not exist "%~dp0installer_enregistreur_windows.ps1" (
  echo Fichier manquant : installer_enregistreur_windows.ps1
  echo Il doit se trouver dans le meme dossier que ce fichier .bat.
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer_enregistreur_windows.ps1"
echo.
pause

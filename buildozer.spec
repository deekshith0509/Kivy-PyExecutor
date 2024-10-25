[app]
title = PyExecutor-Kivy
package.name = tester
package.domain = com.kivy
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
requirements = python3, kivy, kivymd, pygments, plyer, requests, beautifulsoup4, numpy, flask, pyyaml, pytest, scikit-learn, django, psutil,materialyoucolor,exceptiongroup,asyncgui,asynckivy, pyjnius
orientation = portrait
presplash.filename = presplash.png  
icon.filename = icon.png
fullscreen = 0
android.archs = arm64-v8a
android.release_artifact = apk
android.accept_sdk_license = True
android.api = 33
android.ndk = 25b
android.presplash_color = #000000
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Versioning
version = 0.2

# Debug mode
debug = 1

[buildozer]
log_level = 2
warn_on_root = 1

android.allow_backup = True
android.logcat = True

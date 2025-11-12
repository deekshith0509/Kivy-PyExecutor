[app]
title = PyExecutor-Kivy
package.name = debugger
package.domain = com.kivy
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
source.main = main.py
requirements = python3, kivy, kivymd, pygments, qrcode, plyer, requests, beautifulsoup4, numpy, flask, pyyaml, pytest, scikit-learn, django, psutil, materialyoucolor, exceptiongroup, asyncgui, asynckivy, pyjnius, Pillow, urllib3, ffmpeg-python, future, setuptools, libffi
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
android.permissions = MANAGE_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO
version = 0.3

# Debug mode
debug = 1

[buildozer]
log_level = 2
warn_on_root = 1

android.allow_backup = True
android.logcat = True




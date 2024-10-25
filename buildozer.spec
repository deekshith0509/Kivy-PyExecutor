[app]
title = PyExecutor-Kivy
package.name = tester
package.domain = com.kivy
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
# requirements = python3, kivy, kivymd, pygments, plyer, requests, beautifulsoup4, numpy, flask, pyyaml, pytest, scikit-learn, django, psutil,materialyoucolor,exceptiongroup,asyncgui,asynckivy, pyjnius

requirements = python3, kivy, kivymd,pygments, qrcode, plyer, requests, beautifulsoup4, numpy, flask, pyyaml, pytest, scikit-learn, django, psutil, materialyoucolor, exceptiongroup, asyncgui, asynckivy, pyjnius, Pillow, urllib3, setuptools, libffi

orientation = portrait
presplash.filename = presplash.png  
icon.filename = icon.png
fullscreen = 0
android.archs = arm64-v8a
android.release_artifact = apk
android.accept_sdk_license = True
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 31    #most important !!!!!!
android.ndk = 25b
android.presplash_color = #000000
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Versioning
version = 0.3

# Debug mode
debug = 1

[buildozer]
log_level = 2
warn_on_root = 1

android.allow_backup = True
android.logcat = True

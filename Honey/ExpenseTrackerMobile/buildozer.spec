[app]
# Expense Tracker Mobile App
title = Expense Tracker
package.name = expensetracker
package.domain = com.gps

# Source code location
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Application versioning
version = 1.0.0

# Application requirements
requirements = python3,kivy==2.2.1,mysql-connector-python,pillow,werkzeug

# Supported orientations
orientation = portrait

# Fullscreen mode
fullscreen = 0

# Android specific
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# App icon (create icon.png 512x512)
# icon.filename = %(source.dir)s/icon.png

# Presplash screen
# presplash.filename = %(source.dir)s/presplash.png

# Build type
android.arch = arm64-v8a

# Release signing
# android.keystore = my-release-key.keystore
# android.keyalias = alias_name

[buildozer]
# Log level (0 = error, 1 = info, 2 = debug)
log_level = 2
warn_on_root = 1

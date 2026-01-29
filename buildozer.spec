[app]

# (str) Title of your application
title = HEX

# (str) Package name
package.name = hex

# (str) Package domain
package.domain = org.hex

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,kv,json,png,jpg,jpeg,mp3,wav,txt

# (list) Files to exclude
source.exclude_exts = spec,pyc

# (list) Folders to include
source.include_patterns = assets/*,data/*

# (str) Application version
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.1,kivymd==1.2.0

# (str) Name of the main python file
entrypoint = main.py

# (str) Icon (optional – comment if error)
# icon.filename = assets/icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

# (str) Application theme
android.theme = @android:style/Theme.Material.Light.NoActionBar

# (list) Permissions (offline only)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (bool) Enable AndroidX
android.enable_androidx = True

# (int) Minimum Android API
android.minapi = 21

# (int) Target Android API
android.api = 33

# (int) NDK API
android.ndk_api = 21

# (bool) Allow backup
android.allow_backup = True

# (bool) Use logcat
android.logcat_filters = *:S python:D

# (bool) Copy libs instead of symlink
android.copy_libs = True

# (str) Gradle version
android.gradle_dependencies =

# (bool) Force permissions dialog only when needed
android.permission_dialog = True
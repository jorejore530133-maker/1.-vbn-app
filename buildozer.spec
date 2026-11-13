[app]

title = My Application
package.name = myapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,kivymd
orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.archs = arm64-v8a
android.accept_sdk_license = True
android.minapi = 21
android.api = 33
android.ndk = 25b

[buildozer]

log_level = 2
warn_on_root = 1

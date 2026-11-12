[app]

title = VBN Fortress
package.name = vbnfortress
package.domain = org.vbn.security
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy,requests,urllib3,certifi
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.archs = arm64-v8a
android.allow_backup = False
android.accept_sdk_license = True
android.minapi = 21
android.api = 34
android.ndk = 25b
android.build_tools_version = 34.0.0

[buildozer]

log_level = 2
warn_on_root = 1

[app]

title = VBN Fortress

package.name = vbnfortress

package.domain = org.vbn.security

source.dir = .

source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

orientation = portrait

fullscreen = 0

android.permissions = INTERNET

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = False

android.accept_sdk_license = True

android.api = 33

android.build_tools_version = 33.0.2


[buildozer]

log_level = 2

warn_on_root = 1

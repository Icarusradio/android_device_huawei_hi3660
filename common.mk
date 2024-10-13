#
# Copyright (C) 2024 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/product_launched_with_o.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/non_ab_device.mk)
# Setup dalvik vm configs
$(call inherit-product, frameworks/native/build/phone-xhdpi-4096-dalvik-heap.mk)
# Project ID Quota
$(call inherit-product, $(SRC_TARGET_DIR)/product/emulated_storage.mk)

# AAPT conf
PRODUCT_AAPT_CONFIG := normal 
PRODUCT_AAPT_PREF_CONFIG := xxhdpi
PRODUCT_CHARACTERISTICS := tablet

# Audio
$(call soong_config_set,android_hardware_audio,run_64bit,true)

PRODUCT_PACKAGES += \
    android.hardware.audio@4.0-impl \
    android.hardware.audio.effect@4.0-impl \
    android.hardware.audio.service \
    android.hardware.bluetooth.audio-impl

PRODUCT_PACKAGES += \
    audio.bluetooth.default \
    audio.r_submix.default \
    audio.usb.default

PRODUCT_PACKAGES += \
    libalsautils \
    libaudiopreprocessing \
    libtinycompress

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilts/audio_effects.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_effects.xml \
    $(LOCAL_PATH)/prebuilts/audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_policy_configuration.xml

PRODUCT_COPY_FILES += \
    frameworks/av/services/audiopolicy/config/bluetooth_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/bluetooth_audio_policy_configuration.xml \
    frameworks/av/services/audiopolicy/config/r_submix_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/r_submix_audio_policy_configuration.xml \
    frameworks/av/services/audiopolicy/config/usb_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/usb_audio_policy_configuration.xml \
    frameworks/av/services/audiopolicy/config/audio_policy_volumes.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_policy_volumes.xml \
    frameworks/av/services/audiopolicy/config/default_volume_tables.xml:$(TARGET_COPY_OUT_VENDOR)/etc/default_volume_tables.xml

# Binder
PRODUCT_PACKAGES += \
    android.hidl.allocator@1.0.vendor \
    android.hidl.base@1.0.vendor\
    android.hidl.base@1.0 \
    android.hidl.memory@1.0.vendor \
    android.hidl.manager@1.0 \
    libhidlmemory.vendor \
    libhidltransport.vendor \
    libhidltransport \
    libhwbinder.vendor \
    libhwbinder

# Bluetooth
PRODUCT_PACKAGES += \
    android.hardware.bluetooth@1.0-impl \
    android.hardware.bluetooth@1.0-service

# Bootanimation
TARGET_SCREEN_HEIGHT := 2560
TARGET_SCREEN_WIDTH := 1600

# Camera
PRODUCT_PACKAGES += \
    android.hardware.camera.provider@2.4-impl

PRODUCT_PACKAGES += \
    vendor.huawei.hardware.biometrics.hwfacerecognize@1.1.vendor \
    vendor.huawei.hardware.hwfactoryinterface@1.1.vendor \
    vendor.huawei.hardware.camera.cfgsvr@1.1.vendor \
    vendor.huawei.hardware.sensors@1.0.vendor

PRODUCT_PACKAGES += \
    libui_shim.vendor
    
PRODUCT_PACKAGES += \
    liblogshim

# DRM
PRODUCT_PACKAGES += \
    android.hardware.drm-service.clearkey \
    android.hardware.drm@1.1.vendor

PRODUCT_PACKAGES += \
    libmockdrmcryptoplugin

# Fastbootd
PRODUCT_PACKAGES += \
    fastbootd

# Fingerprint
PRODUCT_PACKAGES += \
    vendor.huawei.hardware.biometrics.fingerprint@2.1.vendor

PRODUCT_PACKAGES += \
    vendor.huawei.hardware.hwvibrator@1.0.vendor

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilts/fingerprint.kl:$(TARGET_COPY_OUT_VENDOR)/usr/keylayout/fingerprint.kl \
    $(LOCAL_PATH)/prebuilts/touch_key.kl:$(TARGET_COPY_OUT_VENDOR)/usr/keylayout/touch_key.kl

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilts/native_packages.bin:$(TARGET_COPY_OUT_VENDOR)/etc/native_packages.bin

# Folio
PRODUCT_PACKAGES += \
    folio_daemon

# Gatekeeper
PRODUCT_PACKAGES += \
    android.hardware.gatekeeper@1.0-service \
    android.hardware.gatekeeper@1.0-impl

# GPS/GNSS
PRODUCT_PACKAGES += \
    android.hardware.gnss.measurement_corrections@1.0.vendor \
    android.hardware.gnss.visibility_control@1.0.vendor \
    android.hardware.gnss@2.0.vendor

PRODUCT_COPY_FILES += \
     $(LOCAL_PATH)/prebuilts/gnss_suplconfig_hisi.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/gnss/config/gnss_suplconfig_hisi.xml \
     $(LOCAL_PATH)/prebuilts/privapp-permissions-supl.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/privapp-permissions-supl.xml

# Graphics
PRODUCT_PACKAGES += \
    android.hardware.graphics.allocator@2.0-impl \
    android.hardware.graphics.allocator@2.0-service \
    android.hardware.graphics.composer@2.2-service \
    android.hardware.graphics.mapper@2.0-impl

# Health
PRODUCT_PACKAGES += \
    android.hardware.health-service.example \
    android.hardware.health-service.example_recovery \
    android.hardware.health@2.1.vendor

# HIDL
PRODUCT_ENFORCE_VINTF_MANIFEST_OVERRIDE := true

# Hisi init
PRODUCT_PACKAGES += \
    hisi_init

# Init
PRODUCT_PACKAGES += \
    fstab.hi3660 \
    fstab.hi3660.ramdisk \
    init.connectivity.hi3660.rc \
    init.hi3660.rc \
    init.usb.hi3660.rc \
    ueventd.hi3660.rc

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/rootdir/etc/init.recovery.hi3660.rc:$(TARGET_RECOVERY_OUT)/root/init.recovery.hi3660.rc

# Keymaster
PRODUCT_PACKAGES += \
    android.hardware.keymaster@3.0-service

PRODUCT_PACKAGES += \
    libkeymaster3device.vendor \
    libkeystore-engine-wifi-hidl \
    libkeystore-wifi-hidl

# Light
PRODUCT_PACKAGES += \
    android.hardware.light-service.huawei

# Livedisplay
PRODUCT_PACKAGES += \
    vendor.lineage.livedisplay@2.1-service.hisi

# Media
PRODUCT_PACKAGES += \
    libmockcasplugin

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilts/media_codecs.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs.xml \
    $(LOCAL_PATH)/prebuilts/media_codecs_performance.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_performance.xml \
    $(LOCAL_PATH)/prebuilts/media_profiles_V1_0.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_profiles_V1_0.xml

PRODUCT_COPY_FILES += \
    frameworks/av/media/libstagefright/data/media_codecs_google_audio.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_google_audio.xml \
    frameworks/av/media/libstagefright/data/media_codecs_google_telephony.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_google_telephony.xml \
    frameworks/av/media/libstagefright/data/media_codecs_google_video.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_google_video.xml

# Memtrack
PRODUCT_PACKAGES += \
    android.hardware.memtrack@1.0-impl \
    android.hardware.memtrack@1.0-service

# Misc
PRODUCT_PACKAGES += \
    android.hardware.configstore-utils.vendor \
    libstagefright_softomx_plugin.vendor \
    libprotobuf-cpp-lite-vendorcompat \
    libutilscallstack.vendor \
    libhardware_legacy.vendor \
    libmemtrack.vendor \
    libaudioroute.vendor \
    libstdc++_vendor \
    libnetutils.vendor \
    libexif.vendor \
    libexpat.vendor \
    libjpeg.vendor \
    libyuv.vendor \
    libion.vendor \
    libion \

PRODUCT_PACKAGES += \
    libiawareperf_client \
    libperfgenius_vendor_client

PRODUCT_PACKAGES += \
    vendor.huawei.hardware.perfgenius@2.0.vendor

PRODUCT_PACKAGES += \
    libchrlog \
    libhwlog \
    libimonitor \
    libxcollie

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilts/cfg_cmr_hisi.ini:$(TARGET_COPY_OUT_VENDOR)/etc/cfg_cmr_hisi.ini \
    $(LOCAL_PATH)/prebuilts/cfg_cmr_w09_hisi.ini:$(TARGET_COPY_OUT_VENDOR)/etc/cfg_cmr_w09_hisi.ini \
    $(LOCAL_PATH)/prebuilts/cfg_sht_hisi.ini:$(TARGET_COPY_OUT_VENDOR)/etc/cfg_sht_hisi.ini \
    $(LOCAL_PATH)/prebuilts/cfg_sht_w09_hisi.ini:$(TARGET_COPY_OUT_VENDOR)/etc/cfg_sht_w09_hisi.ini

# Overlays
DEVICE_PACKAGE_OVERLAYS += \
    $(LOCAL_PATH)/overlay \
    $(LOCAL_PATH)/overlay-lineage

# Partitions
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Permissions
PRODUCT_COPY_FILES += \
    frameworks/native/data/etc/android.hardware.bluetooth.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.bluetooth.xml \
    frameworks/native/data/etc/android.hardware.bluetooth_le.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.bluetooth_le.xml \
    frameworks/native/data/etc/android.hardware.camera.autofocus.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.autofocus.xml \
    frameworks/native/data/etc/android.hardware.camera.front.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.front.xml \
    frameworks/native/data/etc/android.hardware.camera.manual_postprocessing.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.manual_postprocessing.xml \
    frameworks/native/data/etc/android.hardware.camera.raw.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.raw.xml \
    frameworks/native/data/etc/android.hardware.camera.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.xml \
    frameworks/native/data/etc/android.hardware.faketouch.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.faketouch.xml \
    frameworks/native/data/etc/android.hardware.fingerprint.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.fingerprint.xml \
    frameworks/native/data/etc/android.hardware.location.gps.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.location.gps.xml \
    frameworks/native/data/etc/android.hardware.location.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.location.xml \
    frameworks/native/data/etc/android.hardware.opengles.aep.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.opengles.aep.xml \
    frameworks/native/data/etc/android.hardware.sensor.accelerometer.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.accelerometer.xml \
    frameworks/native/data/etc/android.hardware.sensor.compass.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.compass.xml \
    frameworks/native/data/etc/android.hardware.sensor.gyroscope.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.gyroscope.xml \
    frameworks/native/data/etc/android.hardware.sensor.light.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.light.xml \
    frameworks/native/data/etc/android.hardware.sensor.proximity.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.proximity.xml \
    frameworks/native/data/etc/android.hardware.sensor.stepcounter.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.stepcounter.xml \
    frameworks/native/data/etc/android.hardware.touchscreen.multitouch.jazzhand.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.touchscreen.multitouch.jazzhand.xml \
    frameworks/native/data/etc/android.hardware.usb.accessory.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.usb.accessory.xml \
    frameworks/native/data/etc/android.hardware.usb.host.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.usb.host.xml \
    frameworks/native/data/etc/android.hardware.vulkan.level-1.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.vulkan.level.xml \
    frameworks/native/data/etc/android.hardware.vulkan.version-1_0_3.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.vulkan.version.xml \
    frameworks/native/data/etc/android.hardware.wifi.direct.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.wifi.direct.xml \
    frameworks/native/data/etc/android.hardware.wifi.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.wifi.xml \
    frameworks/native/data/etc/android.software.app_widgets.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.software.app_widgets.xml \
    frameworks/native/data/etc/android.software.midi.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.software.midi.xml \
    frameworks/native/data/etc/android.software.verified_boot.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.software.verified_boot.xml

# Power
PRODUCT_PACKAGES += \
    android.hardware.power-service.pixel-libperfmgr

PRODUCT_PACKAGES += \
    libshim_audioparams

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilts/powerhint.json:$(TARGET_COPY_OUT_VENDOR)/etc/powerhint.json

PRODUCT_COPY_FILES += \
    system/core/libprocessgroup/profiles/cgroups_28.json:$(TARGET_COPY_OUT_VENDOR)/etc/cgroups.json \
    system/core/libprocessgroup/profiles/task_profiles_28.json:$(TARGET_COPY_OUT_VENDOR)/etc/task_profiles.json

# RRO
PRODUCT_ENFORCE_RRO_TARGETS := *

# Sensors
PRODUCT_PACKAGES += \
    android.frameworks.sensorservice@1.0.vendor \
    android.hardware.sensors@1.0-impl \
    android.hardware.sensors@1.0-service

# Soong namespaces
PRODUCT_SOONG_NAMESPACES += \
    $(LOCAL_PATH) \
    hardware/google/interfaces \
    hardware/google/pixel \
    $(LOCAL_PATH)/resources

# Tee
PRODUCT_PACKAGES += \
    vendor.huawei.hardware.libteec@2.0 \
    vendor.huawei.hardware.libteec@2.0.vendor

# Touch
PRODUCT_PACKAGES += \
    vendor.lineage.touch@1.0-service.hi3660

# USB
PRODUCT_PACKAGES += \
    android.hardware.usb@1.3-service.basic \
    com.android.future.usb.accessory

# Vibrator
PRODUCT_PACKAGES += \
    android.hardware.vibrator@1.0-impl \
    android.hardware.vibrator@1.0-service

# WiFi
PRODUCT_PACKAGES += \
    android.hardware.wifi-service \
    hostapd \
    wpa_supplicant \
    wpa_supplicant.conf

PRODUCT_PACKAGES += \
    WifiOverlay

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/wifi/wpa_supplicant_overlay.conf:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/wpa_supplicant_overlay.conf \
    $(LOCAL_PATH)/wifi/p2p_supplicant_overlay.conf:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/p2p_supplicant_overlay.conf

PRODUCT_GMS_CLIENTID_BASE := android-huawei

# Inherit the proprietary files
$(call inherit-product, vendor/huawei/hi3660/hi3660-vendor.mk)

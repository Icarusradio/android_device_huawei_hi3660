#!/bin/bash
#
# Copyright (C) 2016 The CyanogenMod Project
# Copyright (C) 2017-2020 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

set -e

DEVICE=schubert
VENDOR=huawei

# Load extract_utils and do some sanity checks
MY_DIR="${BASH_SOURCE%/*}"
if [[ ! -d "${MY_DIR}" ]]; then MY_DIR="${PWD}"; fi

ANDROID_ROOT="${MY_DIR}/../../.."

HELPER="${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
if [ ! -f "${HELPER}" ]; then
    echo "Unable to find helper script at ${HELPER}"
    exit 1
fi
source "${HELPER}"

# Default to sanitizing the vendor folder before extraction
CLEAN_VENDOR=true

ONLY_TARGET=
KANG=
SECTION=

while [ "${#}" -gt 0 ]; do
    case "${1}" in
        -n | --no-cleanup )
                CLEAN_VENDOR=false
                ;;
        -k | --kang )
                KANG="--kang"
                ;;
        -s | --section )
                SECTION="${2}"; shift
                CLEAN_VENDOR=false
                ;;
        * )
                SRC="${1}"
                ;;
    esac
    shift
done

if [ -z "${SRC}" ]; then
    SRC="adb"
fi

function blob_fixup() {
    case "${1}" in
        vendor/lib64/hw/audio.primary_hisi.hi3660.so)
            "${PATCHELF}" --add-needed "libprocessgroup.so" "${2}"
            "${PATCHELF}" --add-needed "libshim_audioparams.so" "${2}"
            sed -i 's/str_parms_get_str/str_parms_get_mod/g' "${2}"
            ;;
        vendor/lib*/hw/gralloc.hi3660.so)
            "${PATCHELF}" --add-needed "libhidlbase.so" "${2}"
            ;;
        vendor/lib*/hw/hwcomposer.hi3660.so)
            "${PATCHELF}" --replace-needed "libui.so" "libui-v28.so" "${2}"
            ;;
        vendor/lib64/libbt-vendor.so)
            "${PATCHELF}" --set-soname "libbt-vendor.so" "${2}"
            ;;
        vendor/lib/libwvhidl.so)
            "${PATCHELF}" --replace-needed "libprotobuf-cpp-lite.so" "libprotobuf-cpp-lite-v29.so" "${2}"
            ;;
        vendor/bin/hw_charger)
            sed -i 's|/system/etc/%s.png|/vendor/etc/%s.png|g' "${2}"
            ;;
        vendor/lib*/libril-hisi.so)
            "${PATCHELF}" --set-soname "libril-hisi.so" "${2}"
            ;;
        vendor/lib64/libcamera_algo.so)
            "${PATCHELF}" --add-needed "libui_shim.so" "${2}"
            ;;
        vendor/lib64/libdcamera_effect.so)
            "${PATCHELF}" --add-needed "liblogshim.so" "${2}"
            ;;
        vendor/lib64/libRefocusContrastPosition.so)
            "${PATCHELF}" --add-needed "liblogshim.so" "${2}"
            ;;
        vendor/etc/camera/*|odm/etc/camera/*)
            sed -i 's/gb2312/iso-8859-1/g' "${2}"
            sed -i 's/GB2312/iso-8859-1/g' "${2}"
            sed -i 's/xmlversion/xml version/g' "${2}"
            ;;
        odm/lib64/hwcam/hwcam.hi3660.m.SHT.so|odm/lib64/hwcam/hwcam.hi3660.m.CMR.so)
            "${PATCHELF}" --remove-needed "vendor.huawei.hardware.ai@1.0.so" "${2}"
            "${PATCHELF}" --remove-needed "vendor.huawei.hardware.biometrics.hwsecurefacerecognize@1.0.so" "${2}"
            ;;
        vendor/lib64/hw/vendor.huawei.hardware.hwdisplay.displayengine@1.2-impl.so)
            "${PATCHELF}" --replace-needed "displayeffect.kirin970.so" "displayeffect.hi3660.so" "${2}"
            ;;
        vendor/lib64/displayeffect.hi3660.so)
            "${PATCHELF}" --set-soname "displayeffect.hi3660.so" "${2}"
            ;;
        vendor/lib64/hwcam/hwcam.services.so)
        "${PATCHELF}" --replace-needed "libhidlbase.so" "libhidlbase-v32.so" "${2}"
        ;;
    esac

    # For all ELF files
    if [[ "${1}" =~ ^.*(\.so|\/bin\/.*)$ ]]; then
        "${PATCHELF}" --replace-needed "libstdc++.so" "libstdc++_vendor.so" "${2}"
    fi
}

# Initialize the helper
setup_vendor "${DEVICE}" "${VENDOR}" "${ANDROID_ROOT}" false "${CLEAN_VENDOR}"

extract "${MY_DIR}/proprietary-files.txt" "${SRC}" "${KANG}" --section "${SECTION}"

"${MY_DIR}/setup-makefiles.sh"

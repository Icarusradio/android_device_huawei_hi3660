/*
 * Copyright (C) 2023 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#define LOG_TAG "hisi_utils"

#include "include/hisi_utils.h"

#include <android-base/logging.h>
#include <android-base/properties.h>

#include <string>
#include <vector>

void set_property(const std::string& prop, const std::string& value) {
    // Core telephony configuration must be set by vendor_init. Stage the
    // selected phone.prop values for the init action that releases rild.
    std::string target = prop;
    if (prop == "ro.telephony.default_network") {
        target = "vendor.hisi.default_network";
    } else if (prop == "persist.radio.multisim.config") {
        target = "vendor.hisi.multisim_config";
    } else if (prop == "ro.cdma.home.operator.numeric") {
        target = "vendor.hisi.cdma_home_operator_numeric";
    }

    LOG(INFO) << "Setting property: " << target << " to " << value;

    if (!android::base::SetProperty(target, value)) {
        LOG(ERROR) << "Unable to set: " << target << " to " << value;
    }
}

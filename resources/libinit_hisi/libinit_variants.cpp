/*
 * Copyright (C) 2023-2024 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#define LOG_TAG "libinit_variants"
#include <libinit_utils.h>
#include <libinit_variants.h>
#include <android-base/logging.h>
#include <cerrno>
#include <cstring>
#include <fstream>

using namespace std;

constexpr const char* kBoardInfoPath = "/sys/firmware/devicetree/base/hisi,product_name";

string ReadModelInfo() {
    ifstream fd;
    string buf;
    
    fd.open(kBoardInfoPath);
    if (!fd.is_open()) {
        LOG(ERROR) << "Unable to open: " << kBoardInfoPath << ", error: " << strerror(errno);
        return buf;
    }

    getline(fd, buf);
    fd.close();
    
    return buf;
}

void load_variants() {
    string check_model, model_info = ReadModelInfo();

    // Load the phone model dynamically from devicetree.
    if (!model_info.empty()) {
        LOG(INFO) << "Found model info: " << model_info;
        set_ro_build_prop("model", model_info, true);
        for (int i = 0; i < 3; i++)
        	check_model.push_back(model_info[i]);
        set_ro_build_prop("camera_product", check_model, true);
    } else {
        LOG(ERROR) << "Unable to parse model information!";
    }
}

#!/system/bin/sh
# Copyright (C) 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

# Huawei's formatter uses fixed 4 KiB blocks and a vendor-specific F2FS layout.
# Android 15 recovery supplies -b <page size>; accept only the equivalent 4096
# and keep all other options, including encryption and casefold, for the binary.
set -A args --
while getopts ':a:b:c:C:d:e:E:fg:il:mo:O:qrR:s:St:T:U:Vw:z:' option; do
    case "$option" in
        b)
            if [ "$OPTARG" != 4096 ]; then
                echo "make_f2fs: Huawei formatter only supports -b 4096 (got $OPTARG)" >&2
                exit 1
            fi
            ;;
        :)
            echo "make_f2fs: option -$OPTARG requires an argument" >&2
            exit 1
            ;;
        \?)
            echo "make_f2fs: unsupported option -$OPTARG" >&2
            exit 1
            ;;
        *)
            args[${#args[@]}]="-$option"
            case "$option" in
                a|c|C|d|e|E|g|l|o|O|R|s|t|T|U|w|z)
                    args[${#args[@]}]="$OPTARG"
                    ;;
            esac
            ;;
    esac
done
shift "$((OPTIND - 1))"

exec /system/bin/make_f2fs.huawei "${args[@]}" "$@"

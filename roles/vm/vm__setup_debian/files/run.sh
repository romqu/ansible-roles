#!/usr/bin/env bash

rm -rf ~/Downloads/debian.qcow2
qemu-img create -f qcow2 ~/Downloads/debian.qcow2 5G

sudo qemu-system-aarch64 \
    -bios '/opt/homebrew/share/qemu/edk2-aarch64-code.fd' \
    -accel hvf \
    -m 2048 \
    -cpu host \
    -smp 2 \
    -display none \
    -serial stdio \
    -M virt,highmem=off \
    -nic user,hostfwd=tcp::10022-:22 \
    -drive if=none,file=/Users/roman/Downloads/debian.qcow2,id=hd0 \
    -drive file=/tmp/preseed/out/debian_11.6.0_arm64_preseeded.iso,id=cdrom,if=none,media=cdrom \
    -device virtio-blk-device,drive=hd0 \
    -device virtio-scsi-device \
    -device scsi-cd,drive=cdrom
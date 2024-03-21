#!/usr/bin/env bash

pkill qemu
rm -rf /tmp/ansible/debian.qcow2
qemu-img create -f qcow2 /tmp/ansible/debian.qcow2 5G

qemu-system-aarch64 \
    -bios '/opt/homebrew/share/qemu/edk2-aarch64-code.fd' \
    -monitor unix:/tmp/qemu_monitor.socket,server,nowait \
    -accel hvf \
    -m 2048 \
    -cpu host \
    -smp 2 \
    -display none \
    -serial stdio \
    -M virt,highmem=off \
    -netdev vmnet-shared,id=net0,start-address=10.0.3.1,end-address=10.0.3.3,subnet-mask=255.255.255.0 \
    -nic vmnet-shared \
    -device driver=virtio-net,netdev=net0 \
    -drive if=none,file=/tmp/ansible/debian.qcow2,id=hd0 \
    -drive file=/tmp/ansible/debian_vm/iso/debian_12.2.0_arm64_preseed.iso,id=cdrom,if=none,media=cdrom \
    -device virtio-blk-device,drive=hd0 \
    -device virtio-scsi-device \
    -device scsi-cd,drive=cdrom

#!/usr/bin/env bash

rm -rf ~/Downloads/debian.qcow2
qemu-img create -f qcow2 ~/Downloads/debian.qcow2 5G

#sudo qemu-system-x86_64 \
    #-enable-kvm \
    #-monitor unix:/tmp/qemu_monitor.socket,server,nowait \
    #-m 2048 \
    #-cpu host \
    #-smp 2 \
    #-display none \
    #-serial stdio \
    #-machine ubuntu \
    #-netdev user,id=net0,net=10.0.2.0/24,dhcpstart=10.0.2.254 \
    #-device virtio-net-pci,netdev=net0 \
    #-drive if=none,file=/tmp/ansible/debian_vm/files/debian.qcow2,format=qcow2,id=hd0 \
    #-drive file="/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso",id=cdrom,if=none,media=cdrom \
    #-device virtio-blk-device,drive=hd0 \
    #-device virtio-scsi-device \
    #-device scsi-cd,drive=cdrom

#sudo qemu-system-x86_64 \
#    -bios '/usr/share/qemu/OVMF.fd' \
#    -enable-kvm \
#    -drive if=none,file=/tmp/ansible/debian_vm/files/debian.qcow2,format=qcow2,id=hd0 \
#    -drive file="/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso",id=cdrom,if=none,media=cdrom

qemu-system-x86_64 -hda "/home/roman/Downloads/debian.qcow2" -cdrom "/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso" -boot d -m 512


xorriso -osirrox on -indev debian.iso -extract / debian-iso-files
chmod +w -R debian-iso-files/install.amd/
gunzip debian-iso-files/install.amd/initrd.gz

cp grub.cfg debian-iso-files/boot/grub/
chmod +w -R debian-iso-files/install.amd/
echo preseed.cfg | cpio -H newc -o -A -F debian-iso-files/install.amd/initrd
gzip debian-iso-files/install.amd/initrd
chmod -w -R debian-iso-files/install.amd/

cd debian-iso-files
chmod +w md5sum.txt
find -follow -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt
chmod -w md5sum.txt
cd ..

xorriso -as mkisofs -o preseed-debian.iso \
        -c isolinux/boot.cat -b isolinux/isolinux.bin -no-emul-boot \
        -boot-load-size 4 -boot-info-table debian-iso-files

genisoimage -r -J -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -o preseed-debian.iso debian-iso-files/


sudo 
qemu-system-x86_64 \
    -bios '/usr/share/qemu/OVMF.fd' \
    -monitor unix:/tmp/qemu_monitor.socket,server,nowait \
    -enable-kvm \
    -smp 2 \
    -cpu host \
    -m 2048 \
    -boot order=n,strict=on,menu=on \
    -netdev user,id=net0,net=10.0.2.0/24,dhcpstart=10.0.2.254 \
    -device virtio-net-pci,netdev=net0 \
    -drive file=/tmp/ansible/debian_vm/files/debian.qcow2,if=none,id=drive0 \
    -device virtio-blk-pci,drive=drive0,id=virtblk0 \
    -drive id=cdrom0,if=none,format=raw,readonly=on,file="/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso" \
    -device virtio-scsi-pci,id=scsi0 \
    -device scsi-cd,bus=scsi0.0,drive=cdrom0


qemu-system-x86_64 \
    -bios '/usr/share/qemu/OVMF.fd' \
    -monitor unix:/tmp/qemu_monitor.socket,server,nowait \
    -enable-kvm \
    -smp 2 \
    -cpu host \
    -m 2048 \
    -netdev user,id=net0,net=10.0.2.0/24,dhcpstart=10.0.2.254 \
    -device virtio-net-pci,netdev=net0 \
    -drive file=/tmp/ansible/debian_vm/files/debian.qcow2,if=none,id=drive0 \
    -device virtio-blk-pci,drive=drive0,id=virtblk0,bootindex=1 \
    -drive id=cdrom0,if=none,format=raw,readonly=on,file="/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso" \
    -device virtio-scsi-pci,id=scsi0 \
    -device scsi-cd,bus=scsi0.0,drive=cdrom0,bootindex=2

qemu-system-x86_64 \
    -bios '/usr/share/qemu/OVMF.fd' \
    -monitor unix:/tmp/qemu_monitor.socket,server,nowait \
    -enable-kvm \
    -smp 2 \
    -cpu host \
    -m 2048 \
    -netdev user,id=net0,net=10.0.2.0/24,dhcpstart=10.0.2.254 \
    -device virtio-net-pci,netdev=net0 \
    -drive file=/tmp/ansible/debian_vm/files/debian.qcow2,if=none,id=drive0 \
    -device virtio-blk-pci,drive=drive0,id=virtblk0,bootindex=1 \
    -drive if=none,id=stick,format=raw,file="/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso" \
    -device nec-usb-xhci,id=xhci \
    -device usb-storage,bus=xhci.0,drive=stick,bootindex=2

qemu-system-x86_64 \
    -bios '/usr/share/qemu/OVMF.fd' \
    -append "root=/dev/mapper/primary-root noresume" \
    -initrd "/tmp/ansible/debian_vm/files/initrd.img-6.1.0-17-amd64" \
    -kernel "/tmp/ansible/debian_vm/files/vmlinuz-6.1.0-17-amd64"\
    -enable-kvm \
    -smp 2 \
    -cpu host \
    -m 2048 \
    -netdev user,id=net0,net=10.0.2.0/24,dhcpstart=10.0.2.254,hostfwd=tcp::22-:22 \
    -device virtio-net-pci,netdev=net0 \
    -drive file=/tmp/ansible/debian_vm/files/debian.qcow2,if=none,id=drive0 \
    -device virtio-blk-pci,drive=drive0,id=virtblk0

qemu-system-x86_64 \
    -enable-kvm \
    -nodefaults \
    -no-reboot \
    -bios '/usr/share/qemu/OVMF.fd' \
    -serial null -parallel null -monitor none -display none -vga none \
    -monitor unix:/tmp/qemu_monitor.socket,server,nowait \
    \
    -smp 2 \
    -cpu host \
    -m 2048 \
     \
    -netdev user,id=net0,net=10.0.2.0/24,dhcpstart=10.0.2.254 \
    -device virtio-net-pci,netdev=net0 \
     \
    -drive file=/home/roman/Downloads/debian.qcow2,if=none,id=drive0 \
    -device virtio-blk-pci,drive=drive0,id=virtblk0 \
     \
    -drive if=none,id=stick,format=raw,file="/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso" \
    -device nec-usb-xhci,id=xhci \
    -device usb-storage,bus=xhci.0,drive=stick

qemu-system-x86_64 \
    -bios '/usr/share/qemu/OVMF.fd' \
    -monitor unix:/tmp/qemu_monitor.socket,server,nowait \
    -enable-kvm \
    -smp 2 \
    -cpu host \
    -m 2048 \
    -netdev user,id=net0,net=10.0.2.0/24,dhcpstart=10.0.2.254 \
    -device virtio-net-pci,netdev=net0 \
    -drive file=/home/roman/Downloads/debian.qcow2,if=none,id=drive0 \
    -device virtio-blk-pci,drive=drive0,id=virtblk0 \
    -drive if=none,id=stick,format=raw,file="/tmp/ansible/debian_vm/iso/debian_12.4.0_amd64_preseed.iso" \
    -device nec-usb-xhci,id=xhci \
    -device usb-storage,bus=xhci.0,drive=stick


qemu-system-aarch64 \
-daemonize \
-serial null -parallel null -monitor none -display none -vga none \
\
-chardev socket,path={{ qemu_monitor_socket_path }},server=on,wait=off,id=qga0 \
-device virtio-serial \
-device virtserialport,chardev=qga0,name=org.qemu.guest_agent.0 \
\
-initrd {{ debian_vm_initrd_img_file_path }} \
-kernel {{ debian_vm_kernel_img_file_path }} \
{% if  vm__start_debian__is_encrypted %}
    -append "root=/dev/mapper/primary-root noresume" \
{% else %}
    -append "root=/dev/sda2 noresume" \
{% endif %}
\
-accel hvf \
-m 2048 \
-cpu host \
-smp 2 \
-M virt,highmem=off \
\
-netdev vmnet-shared,id=net0,start-address={{ debian_vm_dhcp_start_address }},end-address={{ debian_vm_dhcp_end_address }},subnet-mask={{ debian_vm_dhcp_subnet_mask }} \
-nic vmnet-shared \
-device driver=virtio-net,netdev=net0 \
\
-drive id=disk0,file={{ debian_vm_tmp_image_file_path }},if=none \
-device ahci,id=ahci0 \
-device ide-hd,drive=disk0,bus=ahci0.0 \
{% for item in debian_vm_hdd_image_files.results %}
    \
    -drive id=disk{{ loop.index }},file={{ tmp_files_dir_path }}/{{ item.stdout }},if=none \
    -device ahci,id=ahci{{ loop.index }} \
    -device ide-hd,drive=disk{{ loop.index }},bus=ahci{{ loop.index }}.0 \
{% endfor %}

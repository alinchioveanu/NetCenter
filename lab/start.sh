#!/bin/bash
set -e

cd "$(dirname "$0")/.."

ISO="lab/ipxe-netcenter.iso"
DISK="lab/images/testvm.qcow2"
LOG="lab/logs/serial.log"

mkdir -p lab/logs

qemu-system-x86_64 \
    -enable-kvm \
    -machine q35 \
    -cpu host \
    -m 2048 \
    -boot d \
    -cdrom "$ISO" \
    -drive file="$DISK",if=ide,format=qcow2 \
    -nic user \
    -vnc :1 \
    -serial file:"$LOG"

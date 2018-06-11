#!/bin/bash
txt="Inizio reboot programmato - "
dt=$(date)
txt="$txt $dt"
if [ -z $1 ]; then
    printf "Dst number not set. Use like this  \n ~ #./reboot.sh +393330101010101 \n"
else
    gammu sendsms TEXT $1 -text $txt
    reboot
    fi
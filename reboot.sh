#!/bin/bash
if [ -Z  $1     ]; then
    printf "Dst number not set. Use like this  \n ~ #./reboot.sh +393330101010101 \n"
else
    gammu sendsms TEXT $1 -text "Inizio reboot programmato - "
    reboot
    fi
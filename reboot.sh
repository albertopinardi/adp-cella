#!/bin/bash
txt="Inizio reboot programmato -"
dt="$(date)"
unix="$(date +%s)"
let unix-=86400
avg=$(sqlite3 ~/datalogger.db "select avg(temp_freezer) from records where time > $unix;")
tavg="- Temperatura media del giorno $avg"
tt="$txt $dt $tavg"
if [ -z $1 ]; then
    printf "Destination number not set. Usage example:  \n ~ #./reboot.sh +393330101010101 \n"
else
    gammu sendsms TEXT $1 -text "$tt"
    reboot
    fi
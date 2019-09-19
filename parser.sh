#!/bin/bash
#Alberto Pinardi

SMS_DIR="/var/spool/gammu/inbox/"
NUM="3406694374"

function date_selector(){
        dt_h="$(date +%Y%m%d_%H)"
        min=$(date +%M)
        if (( min <= 30 ));
        then
                dt_c=$dt_h"00"
        else
                dt_c=$dt_h"30"
        fi
        echo $dt_h
}

function send_temp(){
        dt="$(date)"
        punix="$(date +%s)"
        let unix=punix-3600
        avg=$(sqlite3 ~/datalogger.db "select avg(temp_freezer) from records where time > $unix;")
        tavg="Temperatura media dell'ultima ora $avg"
        tt="$dt $tavg"
        gammu sendsms TEXT "$NUM" -text "$tt"
}

function selector(){
        case $1 in
        "Fanculo") echo "Swarewords found !";;
        "temp") send_temp;;
        *) echo "Clean...";;
        esac
}

interval=$(date_selector)
for i in $(ls -t $SMS_DIR | grep "IN"$interval |grep $NUM ) ;do
#       echo "Messaggio : "
#       cat $SMS_DIR$i
        TEXT=$(cat $SMS_DIR$i)
        selector $TEXT
        echo
        done

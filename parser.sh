
#!/bin/bash
#Alberto Pinardi

SMS_DIR="/var/spool/gammu/inbox/"
NUM="3406694374"

function send_temp(){
    dt="$(date)"
    unix="$(date +%s)"
    let unix-3600
    avg=$(sqlite3 /root/datalogger.db "select avg(temp_freezer) from records where time > $unix;")
    tavg="Temperatura media dell'ultima ora $avg"
    tt="$dt $tavg"
    gammu sendsms TEXT "+393406694374" -text "$tt"
}


function selector(){
        case $1 in
        "Fanculo") echo "Swarewords found !";;
        "temp") send_temp;;
        *) echo "Clean...";;
        esac
        
}

for i in $(ls -t $SMS_DIR | grep $NUM ) ;do
        printf "Messaggio : "
        cat $SMS_DIR$i
        TEXT=$(cat $SMS_DIR$i)
        selector $TEXT
        echo
        done

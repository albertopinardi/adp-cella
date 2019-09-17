#!/bin/bash
#Alberto Pinardi

TXT= $(dmesg | awk '$0 ~ "GSM modem (1-port) converter now attached to ttyUSB.+$" { dev[$NF] = 1 } $0 ~ "GSM modem (1-port) converter now disconnected from ttyUSB.+$" { delete dev[$NF] } END { for(i in dev) print i }')
echo "Copy this to your .gammurc file"
echo
echo "[gammu]"
echo ""
echo "port = \"/dev/$TXT\""
echo "model ="
echo "connection = at115200"
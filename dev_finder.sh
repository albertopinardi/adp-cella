[gammu]

port = "/dev/$(dmesg | awk '$0 ~ "GSM modem \(1-port\) converter now attached to ttyUSB.+$" { dev[$NF] = 1 } $0 ~ "GSM modem \(1-port\) converter now disconnected from ttyUSB.+$" { delete dev[$NF] } END { for(i in dev) print i }')"
model =
connection = at115200
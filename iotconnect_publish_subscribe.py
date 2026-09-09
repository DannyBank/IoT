{
    'commandId': 'cmtua7t1c0xr1v87rhj4qy5a8',
    'parameters': {
        'value': True
    },
    'issuedAt': '2026-09-09T15:57:23.521Z',
    'expiresAt': '2026-09-09T15:58:23.520Z',
    'component': 'traffic_light_1',
    'action': 'green'
}

mosquitto_pub -d -h mqtt.iotworkshop.africa -p 8883 -t "dev_leohiCc-bnwe0sbM/cmd" --cafile "C:\Projects\Academic\Internet-Of-Things\esp32\IoT\mqtt-ca.crt" -u "device_dev_leohiCc-bnwe0sbM" -P "pN_zNVwovV3-XJrXJRnatvYr-Wv7WrdJkjshy0iiWrE" -m "{'commandId': 'cmtua7t1c0xr1v87rhj4qy5a8', 'parameters': {'value': True}, 'issuedAt': '2026-09-09T17:01:56.704Z', 'expiresAt': '2026-09-09T17:05:56.703Z', 'component': 'traffic_light_1', 'action': 'red'}" -i "my_computer_#"
mosquitto_sub -d -h mqtt.iotworkshop.africa -p 8883 -t "dev_leohiCc-bnwe0sbM/cmd" --cafile "C:\Projects\Academic\Internet-Of-Things\esp32\IoT\mqtt-ca.crt" -u "device_dev_leohiCc-bnwe0sbM" -P "pN_zNVwovV3-XJrXJRnatvYr-Wv7WrdJkjshy0iiWrE" 
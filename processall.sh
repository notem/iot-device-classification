#!/usr/bin/env bash

# Configurable parameters
# NOTE: use full paths
PCAPS_DIR=/media/nate/wf-research/IoTDataset            # dataset
OUTPUT_DIR=/media/nate/wf-research/IoTDatasetProcessed  # output root
SIM_PATH=/home/nate/PycharmProjects/joy/bin/joy         # sim binary
EXTRACT_PATH=/home/nate/PycharmProjects/joy/extractfeatures.py

# option arguments for CISCO Joy
OPTIONS="dns=1 tls=1 bidir=1 verbosity=2 logfile=joy.log"

# Device MAC addresses
# https://iotanalytics.unsw.edu.au/resources/List_Of_Devices.txt
MAC[0]="d0:52:a8:00:67:5e"  # smart things
MAC[1]="44:65:0d:56:cc:d3"  # amazon echo
MAC[2]="70:ee:50:18:34:43"  # netatmo welcome
MAC[3]="f4:f2:6d:93:51:f1"  # TP-Link camera
MAC[4]="00:16:6c:ab:6b:88"  # Samsung smartcam
MAC[5]="30:8c:fb:2f:e4:b2"  # Dropcam
MAC[6]="00:62:6e:51:27:2e"  # Insteon camera (wired)
MAC[7]="e8:ab:fa:19:de:4f"  # Insteon camera (wireless)
MAC[8]="00:24:e4:11:18:a8"  # Withings monitor
MAC[9]="ec:1a:59:79:f4:89"  # Belkin Wemo switch
MAC[10]="50:c7:bf:00:56:39" # TP-Link smart plug
MAC[11]="74:c6:3b:29:d7:1d" # iHome
MAC[12]="ec:1a:59:83:28:11" # Belkin wemo motion sensor
MAC[13]="18:b4:30:25:be:e4" # NEST smoke alarm
MAC[14]="70:ee:50:03:b8:ac" # Netatmo weather station
MAC[15]="00:24:e4:1b:6f:96" # Withings smart scale
MAC[16]="74:6a:89:00:2e:25" # Blipcare blood pressure meter
MAC[17]="00:24:e4:20:28:c6" # Withings sleep sensor
MAC[18]="d0:73:d5:01:83:08" # LiFX smartbulb
MAC[19]="18:b7:9e:02:20:44" # Triby speaker
MAC[20]="e0:76:d0:33:bb:85" # PIX-STAR photo-frame
MAC[21]="70:5a:0f:e4:9b:c0" # HP printer
MAC[22]="08:21:ef:3b:fc:e3" # Samsung galaxy tab
MAC[23]="30:8c:fb:b6:ea:45" # Nest Dropcam
MAC[24]="40:f3:08:ff:1e:da" # Android phone
MAC[25]="74:2f:68:81:69:42" # Laptop
MAC[26]="ac:bc:32:d4:6f:2f" # Macbook
MAC[27]="b4:ce:f6:a7:a3:c2" # Android phone
MAC[28]="d0:a6:37:df:a1:e1" # Iphone
MAC[29]="f4:5c:89:93:cc:85" # Macbook/Iphone
MAC[31]="14:cc:20:51:33:ea" # TPLink router

# Begin script
mkdir ${OUTPUT_DIR}
for pcap_file in ${PCAPS_DIR}/*.pcap; do
    sleep 1
    echo "----------------------------------"
    echo "=> $(date)"

    pcap_file=$(basename "${pcap_file}")
    echo "=> Processing ${pcap_file}"

    dir_name=(${pcap_file//.pcap/ })
    rm -rf ${OUTPUT_DIR}/${dir_name}
    mkdir ${OUTPUT_DIR}/${dir_name}

    # do processing for each device
    for mac in ${MAC[@]}; do
        cur_dir=${OUTPUT_DIR}/${dir_name}/${mac}
        mkdir ${cur_dir}
        cd ${cur_dir}

        echo -ne "--> Filtering for ${mac} ... "
        tshark -r ${PCAPS_DIR}/${pcap_file} -2 -R "eth.addr==$mac" -w ${pcap_file}
        echo "done"

        echo -ne "--> Extracting flow information     ... "
        ${SIM_PATH} ${OPTIONS} "${cur_dir}/${dir_name}.pcap" 2>/dev/null | gunzip > "flows.json"
        if hash jq 2>/dev/null; then
            jq . < "flows.json" > "flows.json.pretty"
            mv "flows.json.pretty" "flows.json"
        fi
        echo "done"

        echo -ne "--> Extracting features from flows  ... "
        ${EXTRACT_PATH} --file "${cur_dir}/flows.json" #2>&1 > extract.log
        echo "done"
    done
done
echo "----------------------------------"

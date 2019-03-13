#!/bin/bash
DIR="./data"
mkdir ${DIR}
cd ${DIR}
wget https://iotanalytics.unsw.edu.au/iottestbed/pcap/filelist.txt -O filelist.txt --no-check-certificate
cat filelist.txt | egrep -v "(^#.*|^$)" | xargs -n 1 wget --no-check-certificate
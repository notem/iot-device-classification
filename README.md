
This project is a reimplementation of the IoT device classification experiments as seen in [Classifying IoT Devices in Smart Environments Using Network Traffic Characteristics](https://ieeexplore.ieee.org/document/8440758).
0. Install requirements
    * ``pip -r requirements.txt``
    * ``sudo apt-get install -y build-essential libssl-dev libpcap-dev libcurl4-openssl-dev tshark``
0. Download the dataset
    * ``./getdata.sh``
1. Build the Joy application
    * ``git submodule update --recursive --remote``
    * ``cd ./Joy``
    * ```./configure --enable-gzip```
    * ``make clean; make``
2. Configure and run ``processall.sh``
    * Change ``PCAPS_DIR`` to the full path to your dataset
    * Change ``OUTPUT_DIR`` to hte full path to the directory in which to save features.
    * Change ``SIM_PATH`` to point to the Joy binary
    * Change ``EXTRACT_PATH`` to point ``extractfeatures.py``
3. Run ``classify.py``
    * Use ``--root`` to set the features path.
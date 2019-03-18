
This project is a reimplementation of the IoT device classification experiments as seen in [Classifying IoT Devices in Smart Environments Using Network Traffic Characteristics](https://ieeexplore.ieee.org/document/8440758).
At present, this implementation achieves a 98% accuracy on the two-week dataset provided by the authors.


### Usage

0. Install requirements
    * ``pip -r requirements.txt``
    * ``sudo apt-get install -y build-essential libssl-dev libpcap-dev libcurl4-openssl-dev tshark``
1. Download the dataset
    * ``./getdata.sh``
2. Build the Joy application
    * ``git submodule update --recursive --remote``
    * ``cd ./Joy``
    * ```./configure --enable-gzip```
    * ``make clean; make``
3. Configure and run ``processall.sh``
    * Change ``PCAPS_DIR`` to the full path to your dataset
    * Change ``OUTPUT_DIR`` to the full path to the directory in which to save features.
    * Change ``SIM_PATH`` to point to the Joy binary
    * Change ``EXTRACT_PATH`` to point to ``extractfeatures.py``
4. Run ``classify.py``
    * Use ``--root`` to set the features path.
    * (Optionally) Use ``--split`` to set the train:test split.
    * ex. ``./classify.py --root ./IoTDatasetProcessed --split 0.7``
    
### Results

Latest results achieve a testing accuracy of 98.42%. 
The device-by-device breakdown is shown below. 
Note: the human-readable name for each device MAC can be found by either visiting the [author's device list](https://iotanalytics.unsw.edu.au/resources/List_Of_Devices.txt) or examining the comments in the ``processall.sh`` script.

|                   | precision |    recall | f1-score | support   |
|------------------:|:---------:|:---------:|:--------:|:---------:|
| 00:16:6c:ab:6b:88 |      0.99 |      0.97 |     0.98 |       320 |
| 00:24:e4:11:18:a8 |      0.98 |      1.00 |     0.99 |       223 |
| 00:24:e4:1b:6f:96 |      0.96 |      0.96 |     0.96 |        26 |
| 00:24:e4:20:28:c6 |      0.98 |      1.00 |     0.99 |       216 |
| 00:62:6e:51:27:2e |      0.97 |      1.00 |     0.98 |       224 |
| 08:21:ef:3b:fc:e3 |      0.96 |      0.99 |     0.98 |       258 |
| 14:cc:20:51:33:ea |      0.98 |      0.99 |     0.99 |       313 |
| 18:b4:30:25:be:e4 |      0.81 |      0.93 |     0.87 |        14 |
| 18:b7:9e:02:20:44 |      0.98 |      1.00 |     0.99 |       297 |
| 30:8c:fb:2f:e4:b2 |      1.00 |      1.00 |     1.00 |       315 |
| 30:8c:fb:b6:ea:45 |      0.00 |      0.00 |     0.00 |         1 |
| 40:f3:08:ff:1e:da |      0.00 |      0.00 |     0.00 |         3 |
| 44:65:0d:56:cc:d3 |      0.99 |      1.00 |     1.00 |       318 |
| 50:c7:bf:00:56:39 |      1.00 |      1.00 |     1.00 |       236 |
| 70:5a:0f:e4:9b:c0 |      0.99 |      1.00 |     1.00 |       314 |
| 70:ee:50:03:b8:ac |      1.00 |      1.00 |     1.00 |       293 |
| 70:ee:50:18:34:43 |      1.00 |      1.00 |     1.00 |       320 |
| 74:2f:68:81:69:42 |      1.00 |      0.64 |     0.78 |        11 |
| 74:6a:89:00:2e:25 |      0.00 |      0.00 |     0.00 |         4 |
| 74:c6:3b:29:d7:1d |      0.99 |      0.99 |     0.99 |       115 |
| ac:bc:32:d4:6f:2f |      1.00 |      0.50 |     0.67 |        12 |
| b4:ce:f6:a7:a3:c2 |      0.00 |      0.00 |     0.00 |         9 |
| d0:52:a8:00:67:5e |      1.00 |      1.00 |     1.00 |       332 |
| d0:73:d5:01:83:08 |      1.00 |      1.00 |     1.00 |       218 |
| d0:a6:37:df:a1:e1 |      0.00 |      0.00 |     0.00 |         3 |
| e0:76:d0:33:bb:85 |      1.00 |      1.00 |     1.00 |       199 |
| e8:ab:fa:19:de:4f |      0.00 |      0.00 |     0.00 |         1 |
| ec:1a:59:79:f4:89 |      0.95 |      0.96 |     0.96 |       311 |
| ec:1a:59:83:28:11 |      0.96 |      0.95 |     0.96 |       315 |
| f4:5c:89:93:cc:85 |      0.00 |      0.00 |     0.00 |         2 |
| f4:f2:6d:93:51:f1 |      1.00 |      0.99 |     1.00 |       183 |
|                   |           |           |          |           |
|         micro avg |      0.98 |      0.98 |     0.98 |      5406 |
|         macro avg |      0.76 |      0.74 |     0.74 |      5406 |
|      weighted avg |      0.98 |      0.98 |     0.98 |      5406 |

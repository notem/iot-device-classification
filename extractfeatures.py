#!/usr/bin/env python3

import argparse
import datetime
import os
import json
from math import ceil

# some feature values are truncated
#   this is important as the final feature is selected as the
#   mode of all flow values
TRUNC_VOL = 100      # volume
TRUNC_DUR = 10       # duration
TRUNC_RAT = 10       # rate
TRUNC_SLE = 10       # sleep time
TRUNC_DNS = 10       # DNS interval
TRUNC_NTP = 10       # NTP interval


def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser("Extract feature instances from flows.")

    # --file argument only accepts valid files
    def is_valid_file(parser, arg):
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return open(arg, 'r')  # return an open file handle
    parser.add_argument("-f", "--file", required=True, type=lambda x: is_valid_file(parser, x))

    return parser.parse_args()


def iterjsonfile(file):
    """
    Iterate over json objects in a file which contains multiple json objects.
    """
    text = ''.join(file.readlines())
    decoder = json.JSONDecoder()
    while text:
        try:
            json_tuple = decoder.raw_decode(text)
            yield json_tuple[0]
            text = text[json_tuple[1]+1:]
        except ValueError:
            text = text[1:]


def extract_features(flows):
    """
    Extract features from list of flows
    Returns a dictionary of nine elements
    """
    features = {}

    # resort the flows by the time they start
    flows = sorted(flows, key=lambda flow: flow["time_start"])

    # mode of Flow volume
    flow_vols = []
    for flow in flows:
        volume = 0
        if "bytes_out" in flow.keys():
            volume += flow["bytes_out"]
        if "bytes_in" in flow.keys():
            volume += flow["bytes_in"]
        flow_vols.append(volume)
    if len(flow_vols) > 0:
        rounded = [ceil(vol / TRUNC_VOL) * TRUNC_VOL for vol in flow_vols]
        features['flow_volume'] = max(set(rounded), key=rounded.count)
    else:
        features['flow_volume'] = -1

    # mode of Flow duration
    flow_durs = []
    for flow in flows:
        if "time_start" in flow.keys() and "time_end" in flow.keys():
            duration = flow["time_end"] - flow["time_start"]
            flow_durs.append(duration)
    if len(flow_durs) > 0:
        rounded = [ceil(dur / TRUNC_DUR) * TRUNC_DUR for dur in flow_durs]
        features['flow_duration'] = max(set(rounded), key=rounded.count)
    else:
        features['flow_duration'] = -1

    # mode of Flow rate
    flow_rates = []
    for flow in flows:
        if "time_start" in flow.keys() and "time_end" in flow.keys():
            volume = 0
            if "bytes_out" in flow.keys():
                volume += flow["bytes_out"]
            if "bytes_in" in flow.keys():
                volume += flow["bytes_in"]
            duration = flow["time_end"] - flow["time_start"]
            flow_rate = volume / (duration + 0.00001)
            flow_rates.append(flow_rate)
    if len(flow_rates) > 0:
        rounded = [ceil(flow_rate / TRUNC_RAT) * TRUNC_RAT for flow_rate in flow_rates]
        features['flow_rate'] = max(set(rounded), key=rounded.count)
    else:
        features['flow_rate'] = -1

    # mode of Sleep time
    sleep_times = []
    for i in range(1, len(flows)):
        cur_flow = flows[i]
        pre_flow = flows[i-1]
        if "time_start" in cur_flow.keys() and "time_end" in pre_flow.keys():
            sleep_time = cur_flow["time_start"] - pre_flow["time_end"]
            sleep_times.append(sleep_time)
    if len(sleep_times) > 0:
        rounded = [ceil(sleep_time / TRUNC_SLE) * TRUNC_SLE for sleep_time in sleep_times]
        features['sleep_time'] = max(set(rounded), key=rounded.count)
    else:
        features['sleep_time'] = -1

    # mode of DNS interval
    dns_filter = lambda flow: flow.get('sp', 0) == 53 or flow.get('dp', 0) == 53
    dns_flows = list(filter(dns_filter, flows))
    dns_inters = []
    for i in range(1, len(dns_flows)):
        cur_flow = flows[i]
        pre_flow = flows[i-1]
        interval = cur_flow["time_start"] - pre_flow["time_end"]
        dns_inters.append(interval)
    if len(dns_inters) > 0:
        rounded = [ceil(interval / TRUNC_DNS) * TRUNC_DNS for interval in dns_inters]
        features['dns_interval'] = max(set(rounded), key=rounded.count)
    else:
        features['dns_interval'] = -1

    # mode of NTP interval
    ntp_filter = lambda flow: flow.get('pr', 0) == 17 and \
                              (flow.get('sp', 0) == 123 or flow.get('dp', 0) == 123)
    ntp_flows = list(filter(ntp_filter, flows))
    ntp_inters = []
    for i in range(1, len(ntp_flows)):
        cur_flow = flows[i]
        pre_flow = flows[i-1]
        interval = cur_flow["time_start"] - pre_flow["time_end"]
        ntp_inters.append(interval)
    if len(ntp_inters) > 0:
        rounded = [ceil(interval / TRUNC_NTP) * TRUNC_NTP for interval in ntp_inters]
        features['ntp_interval'] = max(set(rounded), key=rounded.count)
    else:
        features['ntp_interval'] = -1

    # remote ports
    ports = {}
    for flow in flows:
        if "dp" in flow.keys():
            ports[flow["dp"]] = ports.get(flow["dp"], 0) + 1
        #if "sp" in flow.keys():
        #    ports[flow["sp"]] = ports.get(flow["sp"], 0) + 1
    features['ports'] = ports

    # domain names
    domains = {}
    for flow in flows:
        if "dns" in flow.keys():
            for rq in flow["dns"]:
                if "qn" in rq.keys():
                    domains[rq["qn"]] = domains.get(rq["qn"], 0) + 1
    features['domains'] = domains

    # cipher suites
    ciphers = {}
    for flow in flows:
        if "tls" in flow.keys() and "cs" in flow["tls"].keys():
            cs_bag = json.dumps(flow["tls"]["cs"])
            ciphers[cs_bag] = ciphers.get(cs_bag, 0) + 1
    features['ciphers'] = ciphers

    return features


def main(args):
    """
    Read in flows from json file.
    Organize flows into hourly slices.
    Extract and save features for hourly slices.
    """
    json_list = [j for j in iterjsonfile(args.file)]

    times = [datetime.time(i, 0, 0) for i in range(1, 24)] + [datetime.time.max]
    flows = [[] for _ in range(24)]

    # sort flows into hourly time slices
    for json_object in json_list:
        if "time_start" in json_object.keys():
            start = datetime.datetime.fromtimestamp(json_object["time_start"]).time()
            index = next((i for i, time in enumerate(times) if start <= time))
            flows[index].append(json_object)

    # extract features from flows
    for index, flow_list in enumerate(flows):
        if len(flow_list) > 0:
            features = extract_features(flow_list)
            with open('features_{}.json'.format(index), "w") as fi:
                json.dump(features, fi, indent=4)


if __name__ == "__main__":
    args = parse_args()
    main(args)
    args.file.close()


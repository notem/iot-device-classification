#!/usr/bin/env python3

import json
import argparse
import os
import numpy as np

# Supress sklearn warnings
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# seed value
# (ensures consistent dataset splitting between runs)
SEED = 0


def parse_args():
    """
    Parse arguments.
    """
    parser = argparse.ArgumentParser()

    def check_path(parser, x):
        if not os.path.exists(x):
            parser.error("That directory {} does not exist!".format(x))
        else:
            return x
    parser.add_argument('-r', '--root', type=lambda x: check_path(parser, x))
    parser.add_argument('-s', '--split', type=float, default=0.7)

    return parser.parse_args()


def load_data(root):
    """
    Load json feature files produced from feature extraction.
    The device label (MAC) is identified from the directory in which the feature file was found.
    Returns X and Y as separate multidimensional arrays.
    The instances in X contain only the first 6 features.
    The ports, domain, and cipher features are stored in separate arrays for easier process in stage 0.
    """
    X = []
    X_p = []
    X_d = []
    X_c = []
    Y = []

    port_set = set()
    domain_set = set()
    cipher_set = set()

    for rt, dirs, files in os.walk(root):
        for file in files:
            file = os.path.join(rt, file)
            label = os.path.basename(os.path.dirname(file))
            name = os.path.basename(file)
            if name.startswith("features") and name.endswith(".json"):
                with open(file, "r") as fp:
                    features = json.load(fp)
                    instance = [features["flow_volume"],
                                features["flow_duration"],
                                features["flow_rate"],
                                features["sleep_time"],
                                features["dns_interval"],
                                features["ntp_interval"]]
                    X.append(instance)
                    X_p.append(list(features["ports"]))
                    X_d.append(list(features["domains"]))
                    X_c.append(list(features["ciphers"]))
                    Y.append(label)
                    port_set.update(list(features["ports"]))
                    domain_set.update(list(features["domains"]))
                    cipher_set.update(list(features["ciphers"]))

    for i in range(len(Y)):
        X_p[i] = list(map(lambda x: X_p[i].count(x), port_set))
        X_d[i] = list(map(lambda x: X_d[i].count(x), domain_set))
        X_c[i] = list(map(lambda x: X_c[i].count(x), cipher_set))

    return np.array(X).astype(float), np.array(X_p), np.array(X_d), np.array(X_c), np.array(Y)


def classify_bayes(X_tr, Y_tr, X_ts, Y_ts):
    """
    Use a multinomial naive bayes classifier to analyze the 'bag of words' seen in the ports/domain/ciphers features.
    Returns the prediction results for the training and testing datasets as an array of tuples in which each row
      represents a data instance and each tuple is composed as the predicted class and the confidence of prediction.
    """
    classifier = MultinomialNB()
    classifier.fit(X_tr, Y_tr)

    # produce class and confidence for training samples
    C_tr = classifier.predict_proba(X_tr)
    C_tr = [(np.argmax(instance), max(instance)) for instance in C_tr]

    # produce class and confidence for testing samples
    C_ts = classifier.predict_proba(X_ts)
    C_ts = [(np.argmax(instance), max(instance)) for instance in C_ts]

    return C_tr, C_ts


def do_stage_0(Xp_tr, Xp_ts, Xd_tr, Xd_ts, Xc_tr, Xc_ts, Y_tr, Y_ts):
    """
    Perform stage 0 of the classification procedure:
        process each multinomial feature using naive bayes
        return the class prediction and confidence score for each instance feature
    """
    # perform multinomial classification on bag of ports
    resp_tr, resp_ts = classify_bayes(Xp_tr, Y_tr, Xp_ts, Y_ts)

    # perform multinomial classification on domain names
    resd_tr, resd_ts = classify_bayes(Xd_tr, Y_tr, Xd_ts, Y_ts)

    # perform multinomial classification on cipher suites
    resc_tr, resc_ts = classify_bayes(Xc_tr, Y_tr, Xc_ts, Y_ts)

    return resp_tr, resp_ts, resd_tr, resd_ts, resc_tr, resc_ts


def do_stage_1(X_tr, X_ts, Y_tr, Y_ts):
    """
    Perform stage 0 of the classification procedure:
        process each multinomial feature using naive bayes
        return the class prediction and confidence score for each instance feature
    """
    model = RandomForestClassifier(n_jobs=-1, n_estimators=10, oob_score=True)
    model.fit(X_tr, Y_tr)
    return model


def main(args):
    """
    Perform main logic of program
    """

    # load dataset
    print("Loading dataset ... ")
    X, X_p, X_d, X_c, Y = load_data(args.root)

    # encode labels
    print("Encoding labels ... ")
    le = LabelEncoder()
    le.fit(Y)
    Y = le.transform(Y)

    # shuffle
    print("Shuffling dataset using seed {} ... ".format(SEED))
    s = np.arange(Y.shape[0])
    np.random.seed(SEED)
    np.random.shuffle(s)
    X, X_p, X_d, X_c, Y = X[s], X_p[s], X_d[s], X_c[s], Y[s]

    # split
    print("Splitting dataset using train:test ratio of {}:{} ... ".format(int(args.split*10), int((1-args.split)*10)))
    cut = int(len(Y) * args.split)
    X_tr, Xp_tr, Xd_tr, Xc_tr, Y_tr = X[cut:], X_p[cut:], X_d[cut:], X_c[cut:], Y[cut:]
    X_ts, Xp_ts, Xd_ts, Xc_ts, Y_ts = X[:cut], X_p[:cut], X_d[:cut], X_c[:cut], Y[:cut]

    # perform stage 0
    print("Performing Stage 0 classification ... ")
    p_tr, p_ts, d_tr, d_ts, c_tr, c_ts = \
        do_stage_0(Xp_tr, Xp_ts, Xd_tr, Xd_ts, Xc_tr, Xc_ts, Y_tr, Y_ts)

    # build stage 1 dataset using stage 0 results
    X_tr_full = []
    X_ts_full = []
    for i in range(len(Y_tr)):
        l = X_tr[i].tolist()
        l.extend([p_tr[i][0],
                  p_tr[i][1],
                  d_tr[i][0],
                  d_tr[i][1],
                  c_tr[i][0],
                  c_tr[i][1]])
        X_tr_full.append(l)
    for i in range(len(Y_ts)):
        l = X_ts[i].tolist()
        l.extend([p_ts[i][0],
                  p_ts[i][1],
                  d_ts[i][0],
                  d_ts[i][1],
                  c_ts[i][0],
                  c_ts[i][1]])
        X_ts_full.append(l)

    # convert to numpy arrays
    X_tr_full, X_ts_full = np.array(X_tr_full), np.array(X_ts_full)

    print("Performing Stage 1 classification ... ")
    # perform final classification

    model = do_stage_1(X_tr_full, X_ts_full, Y_tr, Y_ts)
    print("RF accuracy = {}".format(model.score(X_ts_full, Y_ts)))

    pred = model.predict(X_ts_full)
    print(classification_report(Y_ts, pred, target_names=le.classes_))


if __name__ == "__main__":
    # parse cmdline args
    args = parse_args()
    main(args)

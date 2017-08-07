import sys

import os
import pandas as pd

# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')


def main(args):
    df = pd.DataFrame.from_csv(args.csv)
    from geopy.geocoders import Nominatim
    print df
    for k, r in df.iterrows():
        geolocator = Nominatim()
        s = "{}, {}".format(r['current_latitude'], r['current_longitude'])
        location = geolocator.reverse(s)
        print(location.address)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=int, default=10000)
    main(parser.parse_args())

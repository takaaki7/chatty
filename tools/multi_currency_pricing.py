import requests


def main(args):
    """
    {
  "success":true,
  "terms":"https:\/\/currencylayer.com\/terms",
  "privacy":"https:\/\/currencylayer.com\/privacy",
  "timestamp":1495636746,
  "source":"USD",
  "quotes":{
    "USDUSD":1,
    "USDAUD":1.339094,
    "USDCAD":1.344704,
    "USDPLN":3.739503,
    "USDMXN":18.587299
  }
}
    """
    currencies = ["USD", "EGP", "NPR", "DZD"]
    prices = [495, 1188, 1485]
    url = "http://apilayer.net/api/live?access_key={}&format=1&source=USD&currencies={}".format(
        args.key, ",".join(currencies))
    j = requests.get(url).json()
    print j
    print_prices(currencies, j, prices)


def print_prices(currencies, j, prices):
    for c in currencies:
        rate = j["quotes"]["USD" + c]
        for price in prices:
            print c + ", " + rate + ",  "(price * rate) / 100


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    main(parser.parse_args())

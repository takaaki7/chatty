import requests


def main(args):
    # test user must be added with pages_messaging,manage_page permissions
    j = requests.get(
        "https://graph.facebook.com/v2.8/me/accounts?access_token={}".format(
            args.token)).json()
    if len(j['data']) > 1:
        print "watch out, there are multi page "
    # raise Exception(
    #         "this user has 2 pages. i don't know which one should be handled {}".format(
    #             j))
    tmptoken = j['data'][0]['access_token']

    requests.get(
        "https://graph.facebook.com/v2.8/me/subscribed_apps?method=POST&access_token={}".format(
            tmptoken))
    longtoken = requests.get(
        "https://graph.facebook.com/v2.8/oauth/access_token?grant_type=fb_exchange_token&client_id={appid}&client_secret={secret}&fb_exchange_token={token}".format(
            appid=args.appid, secret=args.secret, token=tmptoken)).json()[
        'access_token']
    print "longtoken:", longtoken
    apptoken = requests.get(
        "https://graph.facebook.com/v2.8/oauth/access_token?client_id={appid}&client_secret={secret}&grant_type=client_credentials".format(
            appid=args.appid, secret=args.secret)).json()['access_token']
    print "apptoken", apptoken


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--appid")
    parser.add_argument("--secret")
    parser.add_argument("--token")
    main(parser.parse_args())

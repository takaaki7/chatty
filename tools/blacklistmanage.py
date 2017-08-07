import redis

from chatty import config


def list():
    cli = redis.from_url(config.REDIS_URL)
    for k in cli.scan_iter("ban:*"):
        print k


def activate(args):
    cli = redis.from_url(config.REDIS_URL)
    cli.delete("ban:{}".format(args.target))


def activateall(args):
    cli = redis.from_url(config.REDIS_URL)
    for k in cli.scan_iter("ban:*"):
        print k
        cli.delete(k)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=False)
    parser.add_argument("--command")
    args = parser.parse_args()
    if args.command == "list":
        list()
    elif args.command == "activate":
        activate(args)
    elif args.command == "activateall":
        activateall(args)

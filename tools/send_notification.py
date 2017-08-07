import datetime
import time
from logging import getLogger

from chatty import Session
from chatty.domain.user_state import UserContext
from chatty.util import fb

logger = getLogger(__name__)


def main(args):
    text = "A lot of people are using Chatty.\n" \
           "Let's talk with them!"
    if args.test_to is None:
        from chatty.domain.model import match, notification
        now = datetime.datetime.utcnow()
        session = Session()
        for u in match.User.inactive_user(now, args.limit, args.gender):
            if u.locale != args.locale:
                continue
            print"candidate", u.id
            uc = UserContext(u)
            if not notification.Notification.notified_thesedays(now, u.id):
                try:
                    uc.send_btn(uc._(text), [uc.langb(), uc.new_chat()],
                                "NOTIFICATION1")
                except Exception as e:
                    notification.Notification.create(
                        u.id, "A lot of people are using Chatty", False)
                    logger.error(e)
                else:
                    notification.Notification.create(
                        u.id, "A lot of people are using Chatty", True)
                time.sleep(2)
        session.commit()
        session.close()
    else:
        fb.send_data(
            fb.button_data(
                args.test_to, text, "NOTIFICATION"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=10)
    parser.add_argument("--gender", default="female")
    parser.add_argument("--locale", default="en_US")
    parser.add_argument("--test_to", default=None)
    main(parser.parse_args())

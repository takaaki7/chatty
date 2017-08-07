import base64

from Crypto.Cipher import AES

from chatty import config

UID_CRYPTO = AES.new(config.CRYPTO_SECRET_KEY)


def encryptuid(uid):
    id = str(uid).rjust(32, 'C')
    # '=' should not be in url so replace with other words
    return base64.urlsafe_b64encode(UID_CRYPTO.encrypt(id)).replace("=",
                                                                    "YoavnG3pdcdGWKmoas8Hi")


def decryptuid(encuid):
    dec = UID_CRYPTO.decrypt(
        base64.urlsafe_b64decode(str(encuid).replace("YoavnG3pdcdGWKmoas8Hi", "=")))
    return dec.replace("C", "")

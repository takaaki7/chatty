from chatty.libs import uidcrypt


def test_crypt():
    enc = uidcrypt.encryptuid("12345")
    assert enc != "12345"
    assert isinstance(enc, str)
    dec = uidcrypt.decryptuid(enc)
    assert dec == "12345"

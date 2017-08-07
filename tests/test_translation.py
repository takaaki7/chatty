# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from chatty import i18n
from chatty.domain.model.match import User
from chatty.domain.user_state import UserContext


def test_translate_for_user():
    user = User("testtest")
    user.locale = "en_US"
    uc = UserContext(user)
    assert uc._("New Chat") == "New Chat"
    user.locale = "fr_FR"
    assert uc._("New Chat") == "Nouveau chat"
    user.locale = "ar_AR"
    assert uc._("New Chat") == "دردشة جديدة"


def test_translate_many():
    fr = i18n.gettext_getfunc("fr_FR")
    ar = i18n.gettext_getfunc("ar_AR")
    t1 = "Not enough points, please purchase more.\n" \
         "Selecting a gender preference require points.(10 points per use)"
    assert "des points. (10 points par utilisation)" in fr(t1)
    assert "فضل يتطلب نقاطاً.(10 نقاط لكل مستخدم)" in ar(t1)
    t2 = "Purchase Points"
    assert "Acheter des points" in fr(t2)
    assert "شراء نقاط" in ar(t2)

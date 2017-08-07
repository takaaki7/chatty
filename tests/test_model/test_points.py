# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

"""
test models.
"""

import pytest

from chatty.domain.model.points import MenuPrice


@pytest.mark.usefixtures('my_init_db')
def test_menu_for_currency():
    menus = MenuPrice.menu_for_currency("USD")
    assert len(menus) == 3
    assert menus[0].price == 495
    assert menus[0].points == 500


@pytest.mark.usefixtures('my_init_db')
def test_menu_is_valid():
    assert MenuPrice.is_valid(500, 495, "USD")
    assert not MenuPrice.is_valid(500, 4, "USD")
    assert not MenuPrice.is_valid(400, 495, "USD")
    assert not MenuPrice.is_valid(400, 495, "NPR")
    assert not MenuPrice.is_valid(400, 495, "JJJ")


@pytest.mark.usefixtures('my_init_db')
def test_get_for_country():
    menu, code = MenuPrice.menu_for_country("Egypt")
    assert code == "EGP"
    assert len(menu) == 3
    assert menu[0].points == 500
    assert menu[0].price == 8909
    assert menu[1].points == 1500
    assert menu[1].currency == "EGP"

    menu2, code2 = MenuPrice.menu_for_country("United States")
    assert code2 == "USD"
    assert len(menu) == 3
    assert menu2[0].points == 500
    assert menu2[0].price == 495
    assert menu2[1].points == 1500
    assert menu2[1].currency == "USD"

    menu3, _ = MenuPrice.menu_for_country("other")
    assert len(menu) == 3
    assert menu3[0].points == 500
    assert menu3[0].price == 495
    assert menu3[1].points == 1500
    assert menu3[1].currency == "USD"

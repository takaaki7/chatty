# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

"""
test models.
"""

import pytest
from chatty.libs import tokener


@pytest.mark.usefixtures('my_init_db')
def test_tokener():
    token0 = tokener.gen_token("samplekey0", "samplens", 1)
    token1 = tokener.gen_token("samplekey1", "samplens", 1)
    token2 = tokener.gen_token("samplekey2", "samplens", 1)
    assert token0 != token1
    assert token1 != token2
    assert tokener.check("samplekey0", token0, "samplens", delete=False)
    assert tokener.check("samplekey1", token1, "samplens", delete=False)
    assert tokener.check("samplekey2", token2, "samplens", delete=False)
    assert tokener.check("samplekey0", token0, "samplens")
    assert tokener.check("samplekey1", token1, "samplens")
    assert tokener.check("samplekey2", token2, "samplens")
    assert not tokener.check("samplekey0", token0, "samplens")
    assert not tokener.check("samplekey1", token1, "samplens")
    assert not tokener.check("samplekey2", token2, "samplens")

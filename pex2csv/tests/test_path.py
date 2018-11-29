import pytest
from path import *
import numpy as np

@pytest.fixture
def basic_bend():
    x0 = 0.0
    y0 = 0.0
    a = 0.0
    da = np.pi / 2
    r = 10.0
    return Bend(x0, y0, a, da, r)

@pytest.fixture
def basic_straight():
    x0 = 0.0
    y0 = 0.0
    h = 0.0
    l = 10.0
    return Straight(x0, y0, h, l)

@pytest.fixture
def basic_path():
    dt = 1.0
    t1 = 10.0
    return Path(dt, t1)

class TestPath(object):
    def test_path_created(self, basic_path):
        dt = 1.0
        t1 = 10.0
        assert basic_path.dt == dt
        assert basic_path.t1 == t1

class TestBend(object):
    def test_created(self, basic_bend):
        new_a = 0.0 - np.sign(np.pi / 2) * np.pi / 2
        new_x0 = 0.0 - 10.0 * np.cos(new_a)
        new_y0 = 0.0 - 10.0 * np.sin(new_a)
        assert basic_bend.a0 == new_a
        assert basic_bend.x0 == new_x0
        assert basic_bend.y0 == new_y0
        assert basic_bend.da == np.pi / 2
        assert basic_bend.r == 10.0

class TestStraight(object):
    def test_straight_created(self, basic_straight):
        assert basic_straight.x0 == 0.0
        assert basic_straight.y0 == 0.0
        assert basic_straight.h == 0.0

import pytest
import numpy as np
from road import *

@pytest.fixture
def basic_xcross_road():
    id = 'XCrossing_1'
    x = 0.0
    y = 0.0
    h = 0.0
    r = 18.0
    lw = 3.5
    chs = [0.0, np.pi / 2, np.pi, 3 / 2 * np.pi]
    len_till_stop = 12.0
    nbr_of_lanes = 2
    return XCrossRoad(id, x, y, h, r, lw, chs, len_till_stop, nbr_of_lanes)

@pytest.fixture
def basic_straight_road():
    id = 'StraightRoad_1'
    x = 0.0
    y = 0.0
    h = 0.0
    l = 20.0
    lw = 3.5
    nbr_of_lanes = 2
    return StraightRoad(id, x, y, h, l, lw, nbr_of_lanes)

@pytest.fixture
def basic_bend_road():
    id = 'BendRoad_1'
    x = 0.0
    y = 0.0
    h = 0.0
    rh = np.pi / 2
    clr = 5.0
    lw = 3.5
    nbr_of_lanes = 2
    return BendRoad(id, x, y, h, rh, clr, lw, nbr_of_lanes)

@pytest.fixture
def basic_curved_road():
    id = 'CurvedRoad_1'
    x = 0.0
    y = 0.0
    h = 0
    rh = np.pi / 2
    cp1 = 20.0
    cp2 = 20.0
    dx = 30.0
    dy = 30.0
    lw = 3.5
    nbr_of_lanes = 2
    return CurvedRoad(id, x, y, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes)

@pytest.fixture
def basic_roundabout_road():
    id = 'Roundabout_1'
    x = 0.0
    y = 0.0
    r = 18.0
    lw = 3.5
    chs = [0, np.pi / 2, np.pi, 3 / 2 *np.pi]
    nbr_of_lanes = 2
    return RoundaboutRoad(id, x, y, r, lw, chs, nbr_of_lanes)

class TestBendRoad(object):
    def test_firstedge_created(self, basic_bend_road):
        assert len(basic_bend_road.e1) == 1

    def test_secondedge_created(self, basic_bend_road):
        assert len(basic_bend_road.e2) == 1

    def test_center_created(self, basic_bend_road):
        assert len(basic_bend_road.c) == 1

    def test_lanes_created(self, basic_bend_road):
        assert len(basic_bend_road.l) == 2

class TestCurvedRoad(object):
    def test_firstedge_created(self, basic_curved_road):
        assert len(basic_curved_road.e1) == 1

    def test_secondedge_created(self, basic_curved_road):
        assert len(basic_curved_road.e2) == 1

    def test_center_created(self, basic_curved_road):
        assert len(basic_curved_road.c) == 1

    def test_lanes_created(self, basic_curved_road):
        assert len(basic_curved_road.l) == 2

class TestRoundaboutRoad(object):
    def test_firstedge_created(self, basic_roundabout_road):
        assert len(basic_roundabout_road.e1) == 4

    def test_secondedge_created(self, basic_roundabout_road):
        assert len(basic_roundabout_road.e2) == 1

    def test_center_created(self, basic_roundabout_road):
        assert len(basic_roundabout_road.c) == 1

    def test_lanes_created(self, basic_roundabout_road):
        assert len(basic_roundabout_road.l) == 2

    def test_exitlanes_created(self, basic_roundabout_road):
        assert len(basic_roundabout_road.exit_lanes) == 4

    def test_exitlane_firstedge_created(self,basic_roundabout_road):
        edge1_length = len(basic_roundabout_road.exit_lanes[0].e1)
        edge2_length = len(basic_roundabout_road.exit_lanes[1].e1)
        edge3_length = len(basic_roundabout_road.exit_lanes[2].e1)
        edge4_length = len(basic_roundabout_road.exit_lanes[3].e1)
        assert edge1_length == 1
        assert edge2_length == 1
        assert edge3_length == 1
        assert edge4_length == 1

    def test_exitlane_secondedge_created(self,basic_roundabout_road):
        edge1_length = len(basic_roundabout_road.exit_lanes[0].e2)
        edge2_length = len(basic_roundabout_road.exit_lanes[1].e2)
        edge3_length = len(basic_roundabout_road.exit_lanes[2].e2)
        edge4_length = len(basic_roundabout_road.exit_lanes[3].e2)
        assert edge1_length == 1
        assert edge2_length == 1
        assert edge3_length == 1
        assert edge4_length == 1

    def test_exitlane_lanes_created(self,basic_roundabout_road):
        lanes1_length = len(basic_roundabout_road.exit_lanes[0].l)
        lanes2_length = len(basic_roundabout_road.exit_lanes[1].l)
        lanes3_length = len(basic_roundabout_road.exit_lanes[2].l)
        lanes4_length = len(basic_roundabout_road.exit_lanes[3].l)
        assert lanes1_length == 2
        assert lanes2_length == 2
        assert lanes3_length == 2
        assert lanes4_length == 2

class TestStraightRoad(object):
    def test_firstedge_created(self, basic_straight_road):
        assert len(basic_straight_road.e1) == 1

    def test_secondedge_created(self, basic_straight_road):
        assert len(basic_straight_road.e2) == 1

    def test_center_created(self, basic_straight_road):
        assert len(basic_straight_road.c) == 1

    def test_lanes_created(self, basic_straight_road):
        assert len(basic_straight_road.l) == 2

class TestXCrossRoad(object):
    def test_segment1_created(self, basic_xcross_road):
        segment = basic_xcross_road.segments[0]
        assert len(segment.l) == 2
        assert len(segment.e1) == 2
        assert len(segment.e2) == 1
        assert len(segment.c) == 1
        assert len(segment.lturn) == 1
        assert len(segment.rturn) == 1

    def test_segment2_created(self, basic_xcross_road):
        segment = basic_xcross_road.segments[1]
        assert len(segment.l) == 2
        assert len(segment.e1) == 2
        assert len(segment.e2) == 1
        assert len(segment.c) == 1
        assert len(segment.lturn) == 1
        assert len(segment.rturn) == 1

    def test_segment3_created(self, basic_xcross_road):
        segment = basic_xcross_road.segments[2]
        assert len(segment.l) == 2
        assert len(segment.e1) == 2
        assert len(segment.e2) == 1
        assert len(segment.c) == 1
        assert len(segment.lturn) == 1
        assert len(segment.rturn) == 1

    def test_segment4_created(self, basic_xcross_road):
        segment = basic_xcross_road.segments[3]
        assert len(segment.l) == 2
        assert len(segment.e1) == 2
        assert len(segment.e2) == 1
        assert len(segment.c) == 1
        assert len(segment.lturn) == 1
        assert len(segment.rturn) == 1

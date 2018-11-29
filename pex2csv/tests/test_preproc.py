#import sys, os
#myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')
import pytest
from preproc import RoadProcessor

class TestRoadProcessor(object):
    def test_set_order(self):
        x = "this"
        assert 'h' in x

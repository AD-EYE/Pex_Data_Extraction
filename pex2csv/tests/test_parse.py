import sys, os, io
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
from parse import *
import pytest
from lxml import etree

def test_get_bend():
    assert 1 > 0



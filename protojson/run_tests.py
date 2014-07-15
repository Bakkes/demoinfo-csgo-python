#!/usr/bin/env python

import os
import sys
import unittest


def getSuite():
	suite = unittest.TestLoader().loadTestsFromNames([
		'protojson.test_pbliteserializer.PbLiteSerializeTests',
		'protojson.test_pbliteserializer.PbLiteDeserializeTests',
	])
	return suite


def main():
	runner = unittest.TextTestRunner()
	suite = getSuite()
	runner.run(suite)


def _parent(path):
	return os.path.dirname(path)


if __name__ == '__main__':
	packageParentDir = _parent(_parent(os.path.abspath(__file__)))
	sys.path.insert(0, packageParentDir)
	print "sys.path[0] is now", repr(sys.path[0])
	print
	print "Note that unittest swallows import-time exceptions.  If you see below"
	print "\"AttributeError: 'module' object has no attribute 'test_pbliteserializer'\","
	print "make sure that google.protobuf is in your PYTHONPATH."
	print "=" * 78
	main()

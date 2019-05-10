#!/usr/bin/python

# Beamweight status check (check_bw_status.py) - tool to see status of current beamweights
# V.A. Moss 10/05/2019 (vmoss.astro@gmail.com)
__author__ = "V.A. Moss"
__date__ = "$10-may-2019 17:00:00$"
__version__ = "1.0"

import os
import sys

current = False
tid = 90510001
count = False

telescopes = ['2','3','4','5','6','7','8','9','a','b','c','d']

for i in range(0,len(telescopes)):

	scope = telescopes[i]

	if current == True:
		print('#########################################\nCurrent status for RT%s:' % scope.upper())
		cmd = 'ssh -t apertif@lcu-rt%s.apertif "ls -ltr /opt/apertif/var/run/calibration/ | tail -3"' % scope
		results = os.system(cmd)
		print('#########################################\n')
	
	elif tid != None and count == False:
		print('#########################################\nCurrent status for RT%s (TID = %s):' % (scope.upper(),tid))
		cmd = 'ssh -t apertif@lcu-rt%s.apertif "ls -ltr /opt/apertif/var/run/calibration/*%s*"' % (scope,tid)
		results = os.system(cmd)
		print('#########################################\n')

	elif tid != None and count == True:
		print('#########################################\nCurrent files for RT%s (TID = %s):' % (scope.upper(),tid))
		cmd = 'ssh -t apertif@lcu-rt%s.apertif "ls -ltr /opt/apertif/var/run/calibration/*%s* | wc -l"' % (scope,tid)
		results = os.system(cmd)
		print('#########################################\n')



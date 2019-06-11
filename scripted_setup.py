#!/usr/bin/python

# Automated Apertif setup (scripted_setup.py) - imaging version
# V.A. Moss 05/05/2019 (vmoss.astro@gmail.com)
__author__ = "V.A. Moss"
__date__ = "$11-jun-2019 17:00:00$"
__version__ = "1.0"

import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
import json

# variables
com_desp = '/home/apertif/UniBoard_FP7/RadioHDL/trunk/applications/apertif/commissioning/'
radio_hdl = '/home/apertif/UniBoard_FP7/RadioHDL/trunk/'
#rts = '2,3,4,5,6,7,8,9,a,b,c,d'
#rts = '23456789abcd'
#sw_version = 'APERTIF-Release-190225_4-opt-Ubuntu14'
#sw_version = 'APERTIF-Release-190507_5-opt-Ubuntu14'
# sw_version_corr = 'ARTS-BusyWeek-May2019-opt-r10168-Ubuntu14'
# #sw_version_rt = 'ARTS-BusyWeek-May2019-opt-r10129-Ubuntu14'
# sw_version = 'Task_3055-opt-r10239-Ubuntu14'
# warm_start = True
# dryrun = True
ub7_bad = False
ub5_bad = False
# executor = False

# Get software
try:
	sw = json.load(open('./aperops/sw.json'))
except:
	sw = json.load(open('sw.json'))
print(sw)
# print(sw['imaging']['sw_corr'])
# sys.exit()

# Load the software versions
sw_version_corr = sw['imaging']['sw_corr']
sw_version_rt = sw['imaging']['sw_rt']
sw_version_wcu = sw['imaging']['sw_wcu']

# Argument parsing
parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--telescopes',
	default='2,3,4,5,6,7,8,9,a,b,c,d',
	help='Specify which telescopes to include (default: %(default)s)')
parser.add_argument('-m', '--mode',
	default='warm',
	help='Specify whether to warm start or cold start (default: %(default)s)')
parser.add_argument('-f', '--firmware',
	default='main',
	help='Specify whether to use main or executor setup (default: %(default)s)')
parser.add_argument('-d', '--dryrun',
	default=False,
	action='store_true',
	help='Specify whether to execute a dry-run (default: %(default)s)')
args = parser.parse_args()

# Parse the arguments
if args.mode == 'warm':
	warm_start = True
elif args.mode == 'cold': 
	warm_start = False
else: 
	print("Unknown mode specified: %s... exiting!" % args.mode)
	sys.exit()

# Main.py vs. executor.py
if args.firmware == 'main':
	executor = False
elif args.firmware == 'executor': 
	executor = True
else: 
	print("Unknown firmware mode specified: %s... exiting!" % args.firmware)
	sys.exit()

# Dry run
if args.dryrun:
	dryrun = True
else:
	dryrun = False

# Specify telescopes
rts = args.telescopes

print('\n################################################################################\nRUNNING IN DRYRUN MODE!!!\n################################################################################')

print('\n################################################################################\nSUMMARY OF COMMANDS SUBMITTED:')

# Turn off telescopes
cmd = """ ssh -t apertif@lcu-head.apertif "clush -g mac 'supervisorctl -p 123 -u user stop all ' | sort" """
print(cmd)
if not dryrun:
	os.system(cmd)

# Turn off datawriter+ATDB
cmd = """ ssh -t apertif@lcu-head.apertif "clush -w wcudata1 'supervisorctl -p 123 -u user stop WCUData: atdb_services_executors:'" """
print(cmd)
if not dryrun:
	os.system(cmd)

# Check it is turned off
cmd = """ ssh -t apertif@lcu-head.apertif "clush --all 'supervisorctl -p 123 -u user status' | sort" """
print(cmd)
if not dryrun:
	os.system(cmd)

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-LCU-RT -s LCU-RT -g lcu-rt[2-13] -a" <<< "y" """ % (sw_version_rt)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-CCU-Corr -s CCU-Corr -g ccu-corr -a" <<< "y" """ % (sw_version_corr)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-DataWriter -s DataWriter -g wcudata[1] -a" <<< "y" """ % (sw_version_wcu)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

if warm_start:

	if executor:

		cmd = """ ssh -t apertif@ccu-corr.apertif "executor --run warm --ccu ccu-corr --telescopes %s --application apertif-dev" """ % (rts)
	else:
		cmd = """ ssh -t apertif@ccu-corr.apertif  "python %s/main.py --app apertif-dev --tel %s --unb 0:15 --pol 0:1 --rerun" """ % (com_desp,rts)
else:
	if executor:
		cmd = """ ssh -t apertif@ccu-corr.apertif "executor --run cold --ccu ccu-corr --telescopes %s --application apertif-dev" """ % (rts)
	else:
		cmd = """ ssh -t apertif@ccu-corr.apertif  "python %s/main.py --app apertif-dev --tel %s --unb 0:15 --pol 0:1" """ % (com_desp,rts)
print(cmd)
if not dryrun:
	os.system(cmd)

if ub7_bad or ub5_bad:

	# Read layout of firmware
	cmd = """ ssh -t apertif@ccu-corr.apertif 'python /home/apertif/UniBoard_FP7/UniBoard/trunk/Software/python/peripherals/util_system_info.py --unb 0:15 --fn 0:3 --bn 0:3 -n 4' """
	print(cmd)	
	if not dryrun:
		os.system(cmd)

		if ub7_bad:
				# Disable link
				cmd = """ ssh -t apertif@ccu-corr.apertif 'python $UPE/peripherals/util_dp_bsn_aligner.py --unb 7 --bn 1 -n 2 -r 0 -s INPUT' """
				print(cmd)	
				if not dryrun:
						os.system(cmd)

		if ub5_bad:
				# Disable link                                                                                                                                                                                                         
				cmd = """ ssh -t apertif@ccu-corr.apertif 'python $UPE/peripherals/util_dp_bsn_aligner.py --unb 5 --bn 1 -n 2 -r 0 -s INPUT' """
				print(cmd)
				if not dryrun:
						os.system(cmd)

	cmd = """ ssh -t apertif@ccu-corr.apertif '%s/applications/apertif/commissioning/central_status.sh apertif-dev %s 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 postcheck 0,1' """ % (radio_hdl,rts)
	print(cmd)	
	if not dryrun:
		os.system(cmd)

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-LCU-RT -s LCU-RT -g lcu-rt[2-13] -a" <<< "y" """ % (sw_version_rt)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-CCU-Corr -s CCU-Corr -g ccu-corr -a" <<< "y" """ % (sw_version_corr)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-DataWriter -s DataWriter -g wcudata[1] -a" <<< "y" """ % (sw_version_wcu)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -c -g all" """
print(cmd)
if not dryrun:
	os.system(cmd)

cmd = """ ssh -t apertif@lcu-head.apertif "clush --all 'supervisorctl -p 123 -u user status' | sort" """
print(cmd)
if not dryrun:
	os.system(cmd)

cmd = """ ssh -t apertif@wcudata1.apertif "./packet_rate.sh" """
print(cmd)
if not dryrun:
	os.system(cmd)

print('################################################################################\n')

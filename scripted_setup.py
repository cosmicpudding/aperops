#!/usr/bin/python

# Automated Apertif setup (scripted_setup.py) - now with ARTS?
# V.A. Moss 05/05/2019 (vmoss.astro@gmail.com)
__author__ = "V.A. Moss & L.C. Oostrum"
__date__ = "$27-jun-2019 17:00:00$"
__version__ = "1.2"

import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
import json

# variables
com_desp = '/home/apertif/UniBoard_FP7/RadioHDL/trunk/applications/apertif/commissioning/'
radio_hdl = '/home/apertif/UniBoard_FP7/RadioHDL/trunk/'
ub7_bad = False
ub5_bad = False

# Get software
try:
	sw = json.load(open('./aperops/sw.json'))
except:
	sw = json.load(open('sw.json'))
print(sw)

# Argument parsing
parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--telescopes',
	default='2,3,4,5,6,7,8,9,a,b,c,d',
	help='Specify which telescopes to include (default: %(default)s)')
parser.add_argument('-m', '--mode',
	default='warm',
	choices=['cold', 'warm'],
	help='Specify whether to warm start or cold start (default: %(default)s)')
parser.add_argument('-f', '--firmware',
	default='main',
	choices=['main', 'executor'],
	help='Specify whether to use main/executor setup (default: %(default)s)')
parser.add_argument('-d', '--dryrun',
	default=False,
	action='store_true',
	help='Specify whether to execute a dry-run (default: %(default)s)')
parser.add_argument('-s', '--science',
	default='imaging',
	choices=['imaging', 'sc1','sc4'],
	help='Specify which science mode of imaging/sc1/sc4 (default: %(default)s)')
parser.add_argument('-a', '--artsmode',
	default='tab',
	choices=['tab', 'iab'],
	help='Specify which ARTS science mode of tab/iab (default: %(default)s)')
args = parser.parse_args()

# Input handler: https://stackoverflow.com/questions/4915361/whats-the-difference-between-raw-input-and-input-in-python3-x
from sys import version_info
if version_info.major == 3:
    pass
elif version_info.major == 2:
    try:
        input = raw_input
    except NameError:
        pass
else:
    print("Unknown python version - input function not safe")

# Specify telescopes
rts = args.telescopes
smode = args.science

# Parse the arguments
if args.mode == 'warm':
	warm_start = True
elif args.mode == 'cold': 
	# Check to make sure a cold start should be run (only responds to 'y')
	sanitycheck = str(input('Are you sure you want to COLD START? (y/n) '))
	if sanitycheck.lower() == 'y':
		warm_start = False
	else:
		warm_start = True
		print('Please check if you want a cold or warm start and rerun the script!)
		sys.exit()
else: 
	print("Unknown mode specified: %s... exiting!" % args.mode)
	sys.exit()

# Main.py vs. executor.py
if args.firmware == 'main':
	executor = False
elif args.firmware == 'executor': 
	executor = True

	# Modify the telescope argument
	rts = ''.join(rts.split(','))

else: 
	print("Unknown firmware mode specified: %s... exiting!" % args.firmware)
	sys.exit()

# Dry run
if args.dryrun:
	dryrun = True
else:
	dryrun = False

# Main.py names
if args.firmware == 'main':
	if smode == 'imaging':
		fwmode = 'apertif-ag'
	elif smode == 'sc4':
		if args.artsmode == 'iab':
			fwmode = 'arts_sc4-iab'
		elif args.artsmode == 'tab':
			fwmode = 'arts_sc4'
	elif smode == 'sc1':
		fwmode = 'arts_sc1'
# Executor names
elif args.firmware == 'executor':
	if smode == 'imaging':
		fwmode = 'imaging'
	elif smode == 'sc4':
		if args.artsmode == 'iab':
			fwmode = 'arts_sc4_survey'
		elif args.artsmode == 'tab':
			fwmode = 'arts_sc4_survey'
	elif smode == 'sc1':
		fwmode = 'arts_sc1_timing'

# Load the software versions
sw_version_corr = sw[args.science]['sw_corr']
sw_version_rt = sw[args.science]['sw_rt']
sw_version_dw = sw[args.science]['sw_dw']

if dryrun:
	print('\n################################################################################\nRUNNING IN DRYRUN MODE!!!\n################################################################################')

print('\n################################################################################\nSUMMARY OF COMMANDS SUBMITTED:')

# Turn off telescopes
cmd = """ ssh -t apertif@lcu-head.apertif "clush -g mac 'supervisorctl -p 123 -u user stop all ' | sort" """
print(cmd)
if not dryrun:
	os.system(cmd)

# Turn off datawriter+ATDB (depending on science mode)
if smode == 'imaging':
	# ATDB executors no longer stopped here
	cmd = """ ssh -t apertif@lcu-head.apertif "clush -w wcudata1 'supervisorctl -p 123 -u user stop WCUData:'" """
elif smode == 'sc1':
	cmd = """ ssh -t apertif@lcu-head.apertif "clush -w arts-sc1 'supervisorctl -p 123 -u user stop all'" """
elif smode == 'sc4':
	# Master node
	cmd = """ ssh arts@arts041.apertif "sudo systemctl stop arts-survey.service" """
	print(cmd)
	if not dryrun:
		os.system(cmd)
	# cluster nodes
	cmd = """ ssh arts@arts041.apertif "ansible -f 10 artscluster_nodes -a 'sudo systemctl stop arts-nodes.service'" """
print(cmd)
if not dryrun:
	os.system(cmd)

# Check it is turned off
if smode == 'sc4':
	# Master node
	cmd = """ ssh arts@arts041.apertif "sudo systemctl status arts-survey.service" """
	print(cmd)
	if not dryrun:
		os.system(cmd)
	# cluster nodes
	cmd = """ ssh arts@arts041.apertif "ansible -f 10 artscluster_nodes -a 'sudo systemctl status arts-nodes.service'" """
else:
	cmd = """ ssh -t apertif@lcu-head.apertif "clush --all 'supervisorctl -p 123 -u user status' | sort" """
print(cmd)
if not dryrun:
	os.system(cmd)

# Install software on telescopes (pass 1)
cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-LCU-RT -s LCU-RT -g lcu-rt[2-13] -a" <<< "y" """ % (sw_version_rt)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

# Install software on correlator (pass 1)
cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-CCU-Corr -s CCU-Corr -g ccu-corr -a" <<< "y" """ % (sw_version_corr)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

# Install software on datawriter/ARTS depending on science mode (pass 1)
if smode == 'imaging':
	cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-DataWriter -s DataWriter -g wcudata[1] -a" <<< "y" """ % (sw_version_dw)
elif smode == 'sc1':
	cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-ARTS -s ARTS -g arts -a" <<< "y" """ % (sw_version_dw)
elif smode == 'sc4':
	cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-ARTSCLUSTER -s ARTSCLUSTER -g artscluster -a" <<< "y" """ % (sw_version_dw)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))


# UNIBOARD LAND BEGINS HERE
if warm_start:
	if executor:
		cmd = """ ssh -t apertif@ccu-corr.apertif "executor --run warm --telescopes %s --application %s --forward" """ % (rts,fwmode)
	else:
		cmd = """ ssh -t apertif@ccu-corr.apertif  "python %s/main.py --app %s --tel %s --unb 0:15 --pol 0:1 --rerun" """ % (com_desp,fwmode,rts)
else:
	if executor:
		cmd = """ ssh -t apertif@ccu-corr.apertif "executor --run cold --telescopes %s --application %s --forward" """ % (rts,fwmode)
	else:
		cmd = """ ssh -t apertif@ccu-corr.apertif  "python %s/main.py --app %s --tel %s --unb 0:15 --pol 0:1" """ % (com_desp,fwmode,rts)
print(cmd)
if not dryrun:
	os.system(cmd)


# These can go long term, only here temporarily while issues are seen
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
	cmd = """ ssh -t apertif@ccu-corr.apertif '%s/applications/apertif/commissioning/central_status.sh %s %s 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 postcheck 0,1' """ % (fwmode,radio_hdl,rts)
	print(cmd)	
	if not dryrun:
		os.system(cmd)

# Install software on telescopes (pass 2)
cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-LCU-RT -s LCU-RT -g lcu-rt[2-13] -a" <<< "y" """ % (sw_version_rt)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

# Install software on correlator (pass 2)
cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-CCU-Corr -s CCU-Corr -g ccu-corr -a" <<< "y" """ % (sw_version_corr)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

# Install software on datawriter/ARTS depending on science mode (pass 2)
if smode == 'imaging':
	cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-DataWriter -s DataWriter -g wcudata[1] -a" <<< "y" """ % (sw_version_dw)
elif smode == 'sc1':
	cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-ARTS -s ARTS -g arts -a" <<< "y" """ % (sw_version_dw)
elif smode == 'sc4':
	cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-ARTSCLUSTER -s ARTSCLUSTER -g artscluster -a" <<< "y" """ % (sw_version_dw)
print(cmd)
if not dryrun:
	os.system("bash -c '{}'".format(cmd))

# Check installation
cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -c -g all" """
print(cmd)
if not dryrun:
	os.system(cmd)

# Check that it is running
if smode == 'sc4':
	# Master node
	cmd = """ ssh arts@arts041.apertif "sudo systemctl status arts-survey.service" """
	print(cmd)
	if not dryrun:
		os.system(cmd)
	# cluster nodes
	cmd = """ ssh arts@arts041.apertif "ansible -f 10 artscluster_nodes -a 'sudo systemctl status arts-nodes.service'" """
else:
	cmd = """ ssh -t apertif@lcu-head.apertif "clush --all 'supervisorctl -p 123 -u user status' | sort" """
print(cmd)
if not dryrun:
	os.system(cmd)

# If imaging mode, check packet rate
if smode == 'imaging':
	cmd = """ ssh -t apertif@wcudata1.apertif "./packet_rate.sh" """
elif smode == 'sc1':
	cmd = """ ssh arts@arts0.apertif "python scripts/packet_rate.py" """
elif smode == 'sc4':
	cmd = """ ssh arts@arts001.apertif "packet_rate" """
print(cmd)
if not dryrun and smode == 'imaging':
	os.system(cmd)

print('################################################################################\n')

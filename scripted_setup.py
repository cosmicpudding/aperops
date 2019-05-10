#!/usr/bin/python

# Automated Apertif setup (scripted_setup.py) - imaging version
# V.A. Moss 05/05/2019 (vmoss.astro@gmail.com)
__author__ = "V.A. Moss"
__date__ = "$05-may-2019 17:00:00$"
__version__ = "1.0"

import os
import sys

# variables
com_desp = '/home/apertif/UniBoard_FP7/RadioHDL/trunk/applications/apertif/commissioning/'
radio_hdl = '/home/apertif/UniBoard_FP7/RadioHDL/trunk/'
rts = '2,3,4,5,6,7,8,9,a,b,c,d'
#sw_version = 'APERTIF-Release-190225_4-opt-Ubuntu14'
sw_version = 'APERTIF-Release-190507_5-opt-Ubuntu14'
warm_start = True
dryrun = False
ub7_bad = True

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

if warm_start:
	cmd = """ ssh -t apertif@ccu-corr.apertif  "python %s/main.py --app apertif-dev --tel %s --unb 0:15 --pol 0:1 --rerun" """ % (com_desp,rts)
else:
	cmd = """ ssh -t apertif@ccu-corr.apertif  "python %s/main.py --app apertif-dev --tel %s --unb 0:15 --pol 0:1" """ % (com_desp,rts)
print(cmd)
if not dryrun:
	os.system(cmd)

if ub7_bad:

	cmd = """ ssh -t apertif@ccu-corr.apertif 'python $UPE/peripherals/util_dp_bsn_aligner.py --unb 7 --bn 1 -n 2 -r 0 -s INPUT' """
	print(cmd)	
	if not dryrun:
		os.system(cmd)

	cmd = """ ssh -t apertif@ccu-corr.apertif '%s/applications/apertif/commissioning/central_status.sh apertif-dev %s 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 postcheck 0,1' """ % (radio_hdl,rts)
	print(cmd)	
	if not dryrun:
		os.system(cmd)

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-LCU-RT -s LCU-RT -g lcu-rt[2-13] -a" <<< "y" """ % (sw_version)
print(cmd)
if not dryrun:
	os.system(cmd)

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-CCU-Corr -s CCU-Corr -g ccu-corr -a" <<< "y" """ % (sw_version)
print(cmd)
if not dryrun:
	os.system(cmd)

cmd = """ ssh -t apertif@lcu-head.apertif "Apertif_install.sh -b %s-DataWriter -s DataWriter -g wcudata[1] -a" <<< "y" """ % (sw_version)
print(cmd)
if not dryrun:
	os.system(cmd)

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

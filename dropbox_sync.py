#!/usr/bin/env python
import os
import sys
import dropbox
import glob
import logging
import time

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

# List contents of specified dropbox folder
def dropbox_listfiles(dbkey,path):
	client = dropbox.Dropbox(dbkey)
	response = client.files_list_folder('%s' % path)
	return response

def dropbox_download(dbkey,path,fname,sname):
	client = dropbox.Dropbox(dbkey)
	metadata, f = client.files_download('%s/%s' % (path,fname))
	out = open(sname, 'wb')
	out.write(f.content)
	out.close()

# List the files
# Note: dbkey should be in a file next to the repo
dbkey = open('.dbkey.txt').read()
path = '/Surveys'
outpath = '/home/apertif/operations/surveys/'

while True:
	logging.info("Starting dropbox sync")
	response = dropbox_listfiles(dbkey,path)
	# Loop over the files that are found
	for file in response.entries:

		# only consider CSV files
		if '.csv' in file.name:

			# Check for existence
			sname = outpath+''.join(file.name.split())
			check = glob.glob('%s' % sname)
	
			# If it doesn't exist locally
			if len(check) == 0:
				#sname = file.name.split(' - ')[1].split('.csv')[0]+'-'+''.join(file.name.split('-')[0].split())+'.csv'
     	                	logging.info("Retrieving file: %s to: %s " % (file.name, sname))
				dropbox_download(dbkey,path,file.name,sname)
        time.sleep(60)
			

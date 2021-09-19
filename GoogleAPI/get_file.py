
import os
from .global_path import *
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


# Download a file if able to be downloaded in a folder
# Returns the path of that downloaded file
def get_file(drive, folder_id, filename):
	
	# Store dictionary of file mimetypes that are able to be downloaded
	mimetypes = {
	    # Drive Document files as PDF
	    'application/vnd.google-apps.document': 'application/pdf',
	    # Drive Sheets files as MS Excel files.
	    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	# see https://developers.google.com/drive/v3/web/mime-types
	}
	
	# Get list of all files in folder and downloaded filename
	folder_file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
	
	for i, file1 in enumerate(sorted(folder_file_list, key = lambda x: x['title']), start=1):
	    
	    if filename not in file1['title']: continue
	    print('Downloading {} from GDrive.'.format(file1['title']))
	    # this should tell you which mimetype the file you're trying to download 
	    
	    if file1['mimeType'] in mimetypes:
	        
	        file1.GetContentFile(file1['title'], mimetype=mimetypes[file1['mimeType']])
	        # get whole file name and add the correct file extension to it
	        whole_filename = [x for x in os.listdir() if filename in x][0]
	        path = os.path.splitext(whole_filename)[0]
	        extension = '.pdf' if 'pdf' in mimetypes[file1['mimeType']] else '.xlsx'
	        new_path = resource_path('Data\\Files\\') + whole_filename + extension
	        
	        if os.path.exists(new_path): os.remove(new_path) # remove old copy of file
	        os.rename(whole_filename, new_path)
	        
	        return new_path

	    else: raise ValueError('File type {} unable to be downloaded.'.format(file1['mimeType']))

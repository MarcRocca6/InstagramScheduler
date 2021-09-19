from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Passes through authorisations into GoogleDrive API
def login():
	gauth = GoogleAuth()
	# Try to load saved client credentials
	gauth.LoadClientConfigFile('Creds\\client_secrets.json')
	gauth.LoadCredentialsFile('Creds\\mycreds.txt')

	if gauth.credentials is None:
	    # Authenticate if they're not there
	    gauth.LocalWebserverAuth()
	    # Will stop refresh error by setting access_type offline
	    gauth.GetFlow()
	    gauth.flow.params.update({'access_type': 'offline'})
	    gauth.flow.params.update({'approval_prompt': 'force'})
	elif gauth.access_token_expired:
	    # Refresh them if expired
	    gauth.Refresh()
	else:
	    # Initialize the saved creds
	    gauth.Authorize()
	# Save the current credentials to a file
	gauth.SaveCredentialsFile('Creds\\mycreds.txt')
	return GoogleDrive(gauth)

login()
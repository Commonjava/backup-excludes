# backup-excludes

The script aims to identify the temporary builds and remote repositories that do not need to be backed up.
In order to get the temporary builds, we need to query them from PNC service, while to access Indy service
to grab the remote repositories. 

## Environment Variables (TODO)

* `INDY_HOST`: The hostname of Indy service 
* `PNC_HOST` : The hostname of PNC service
* `SSO_HOST` : The hostname of SSO service



import requests
import os
import sys, getopt
import json
import getpass  

def handle_call(url, headers=None):
    resp = None
    try:
        if headers == None:
            resp = requests.get(url)
        else:
            resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            raise Exception('GET url {}'.format(resp.status_code))  

    except Exception as e:
        print("Oops!", e.__class__, "occurred.")

    return resp.json()
    
'''
    Create nobackup file under dir
'''
def create_nobackup(dir):
    if os.path.exists(dir):
        open('{}/.nobackup'.format(dir), 'w').close()
    else:
        print("No such directory: {}".format(dir))

'''
    Remove the .nobackup file from the dir
'''
def remove_nobackup(dir):
    nobackup_path = '{}/.nobackup'.format(dir)
    if os.path.exists(nobackup_path):
        os.remove(nobackup_path)
    else:
        print('Cannot delete the file {} as it does not exists.'.format(nobackup_path))

'''
    Handle the remote repo 
'''
def handle_remote_repo():
    for root, dirs, files in os.walk(root_dir):
        for repo_dir_name in dirs:
            if repo_dir_name.startswith('remote-'):
                
                repo_dir = os.path.join(root,repo_dir_name)
                print('Remote repo dir: {}'.format(repo_dir))

                repo_name = repo_dir_name[7:]
                '''
                    The following remote repos are still needed in backup, like MRRC and repository.jboss.org
                '''
                listOfExcludeRepos = ['mrrc','mrrc-ga', 'mrrc-ga-rh', 'release.jboss.org', 'repository.jboss.org']

                '''
                    Check if the repo is NOT in the listOfExcludeRepos
                '''
                if repo_name in listOfExcludeRepos:
                    remove_nobackup(repo_dir)
                else:
                    create_nobackup(repo_dir)
        
'''
    Handle the temporary builds
'''
def handle_temporary_build():
    pnc_instance = os.environ.get('PNC_HOST')

    print('PNC instance: {}'.format(pnc_instance))

    pnc_url = 'http://{}/pnc-rest/rest/build-records?q=status==SUCCESS;temporaryBuild==true&pageIndex={}'

    pnc_data = handle_call(pnc_url.format(pnc_instance,0))

    print('Total pages: {}'.format(pnc_data['totalPages']))
    handle_builds(pnc_data['content'])

    pages = pnc_data['totalPages']
    for page in range(1, pages):
        print('Request page: {}/{}'.format(page, pages))
        pnc_data = handle_call(pnc_url.format(pnc_instance,page))
        handle_builds(pnc_data['content'])

def handle_pnc_temp_build(build):
    store_dir = '{}/hosted-build-{}'.format(root_dir, build['id'])
    print('Hosted temporary dir: {}'.format(store_dir))
    create_nobackup(store_dir)  

def handle_builds(builds):
    for pnc_build in builds:
        handle_pnc_temp_build(pnc_build)

'''
    [Deprecated]
'''
def getAccessToken():
    user = input('Username : ')
    passwd = getpass.getpass('Password : ')

    sso_instance = os.environ.get('SSO_HOST')

    print('SSO instance: {}'.format(sso_instance))

    url = 'https://{}/auth/realms/pncredhat/protocol/openid-connect/token'.format(sso_instance)
    sso_info = {'client_id':'pncindyui', 'username':user, 'password':passwd,'grant_type':"password"}
    resp = requests.post(url, data=sso_info, verify=False)

    print(resp.json()['access_token'])
    return resp.json()['access_token']

def run():

    ''' 
        Global variables
    '''
    global root_dir

    root_dir = os.environ.get('REPO_DIR')
    
    handle_remote_repo()
    handle_temporary_build()

if __name__ == '__main__':
    run()

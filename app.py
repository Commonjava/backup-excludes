import requests
import os
import sys, getopt
import json
import getpass  
import argparse

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
    Query the remote repos from Indy
'''
def query_remote_repo():
    indy_instance = os.environ.get('INDY_HOST')

    print('Indy instance: {}'.format(indy_instance))

    indy_url = 'http://{}/api/admin/remote'.format(indy_instance)
    indy_token = getAccessToken()
    
    indy_data = handle_call(indy_url, {"Authorization":"Bearer " + indy_token})

    if (len(output_file)!=0):
        f = open(output_file,"a+")

    for repo in indy_data['items']:
        if f is None:
            handle_remote_repo(repo)
        else:
            f.write(repo['name'] + '\r\n')

    if f is None:
        f.close()

'''
    Handle the remote repo 
'''
def handle_remote_repo(repo):

    repo_dir = "{}/remote-{}".format(root_dir, repo['name'])
    print('Remote repo dir: {}'.format(repo_dir))

    '''
        The following remote repos are still needed in backup, like MRRC and repository.jboss.org
    '''
    listOfExcludeRepos = ['mrrc','mrrc-ga', 'mrrc-ga-rh', 'release.jboss.org', 'repository.jboss.org']

    '''
        Check if the repo is NOT in the listOfExcludeRepos
    '''
    if repo['name'] in listOfExcludeRepos:
        remove_nobackup(repo_dir)
    else:
        create_nobackup(repo_dir)
        

'''
    Query the temporary builds from PNC
'''
def query_temporary_build():
    pnc_instance = os.environ.get('PNC_HOST')

    print('PNC instance: {}'.format(pnc_instance))

    pnc_url = 'http://{}/pnc-rest/rest/build-records?q=status==SUCCESS;temporaryBuild==true&pageIndex={}'

    pnc_data = handle_call(pnc_url.format(pnc_instance,0))

    if (len(output_file)!=0):
        f = open(output_file,"w+")

    print('Total pages: {}'.format(pnc_data['totalPages']))
    handle_builds(f, pnc_data['content'])

    pages = pnc_data['totalPages']

    for page in range(1, pages):
        print('Request page: {}/{}'.format(page, pages))
        pnc_data = handle_call(pnc_url.format(pnc_instance,page))
        handle_builds(f, pnc_data['content'])

    if f is not None:
        f.close()

'''
    Handle the temporary build 
'''
def handle_pnc_temp_build(build):
    store_dir = '{}/hosted-build-{}'.format(root_dir, build['id'])
    print('Hosted temporary dir: {}'.format(store_dir))
    create_nobackup(store_dir)  

def handle_builds(f, builds):
    
    for pnc_build in builds:
        if f is None:
            handle_pnc_temp_build(pnc_build)
        else:
            f.write(str(pnc_build['id']) + '\r\n')

'''
    Load the temporary builds from the local file
'''
def handle_local_temporary_build():
    if os.path.exists(input_file):
        f = open(input_file, 'r')
        for line in f.readlines():
            handle_pnc_temp_build(json.loads('{"id":"' + line.strip() + '"}'))

        f.close()

'''
    Load the remote repo from the local file
'''
def handle_local_remote_repo():
    if os.path.exists(input_file):
        f = open(input_file, 'r')
        for line in f.readlines():
            handle_remote_repo(json.loads('{"name":"' + line.strip() + '"}'))

        f.close()

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

def main(argv):

    ''' 
        Global variables
    '''
    global output_file
    global input_file
    global root_dir
    global store_type
    global env

    input_file = None      

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", choices=['devel', 'stage', 'prod'])
    parser.add_argument("-t", "--type", choices=['remote', 'temporary'])
    parser.add_argument("-d", "--directory", help='the root directory of the store repository, this is required when -i is specified')
    parser.add_argument("-i", "--inputfile", help='the local file conatining the temporary build id and remote repository name')
    parser.add_argument("-o", "--outputfile", help='the file that will keep the temporary build IDs from PNC and remote repository name from Indy')
    args = parser.parse_args()

    print(args)
    #TODO validate(args)

    store_type  = args.type
    root_dir    = args.directory
    input_file  = args.inputfile
    output_file = args.outputfile
    env         = args.env
    
    if store_type == 'remote':
        if(input_file is not None):
            handle_local_remote_repo()
        else:
            query_remote_repo()
    elif store_type == 'temporary':
        if(input_file is not None):
            handle_local_temporary_build()
        else:
            query_temporary_build()

if __name__ == '__main__':
    main(sys.argv[1:])

# backup-excludes

As the [doc](https://docs.bareos.org/Configuration/Director.html#config-Dir_Fileset_Include) from bareos, if the specified filename (filename-string) is found on the Client in any directory to be backed up, the whole directory will be ignored (not backed up). They recommend to use the filename .nobackup, as it is a hidden file on unix systems, and explains what is the purpose of the file.

Example: exlude Directories containing the file .nobackup
```
# List of files to be backed up
FileSet {
    Name = "MyFileSet"
    Include {
        Options {
            signature = MD5
        }
        File = /home
        Exclude Dir Containing = .nobackup
    }
}
```

The script aims to identify the temporary builds and remote repositories that do not need to be backed up,
and create the file .nobackup in the directories.  In order to do that, we need to query PNC service to get
the temporary builds and to access Indy volume to go through the remote repositories. 

## Environment Variables (TODO)

* `PNC_HOST` : The hostname of PNC service
* `REPO_DIR` : The directory of the repository, e.g.: `/var/lib/backup/indy/storage/maven`



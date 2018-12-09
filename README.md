# GDSyncer
Keep a folder in sync with Google drive.

Using GDsyncer you can easily sync files with your Google Drive. It will fetch all the files which are not present in the local directory and upload all the files which are in the local directory but not in the cloud. Currently syncing of nested folders are not supported. 

## Instructions
1. Go to https://console.cloud.google.com/ and obtain a client_id.json file with Drive API enabled.
2. Save that file in the folder where the script resides.
3. Install the requirements by pip3 install -r requirements.txt
4. Execute the script syncer.py in the folder GDsyncer

![terminal](screenshot.png)
4. That's it! Simple as that!


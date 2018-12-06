from Drive import GoogleDrive
import os
import hashlib

path = "/home/athul/s3"
local_file_list = os.listdir(path)

my_drive = GoogleDrive('../data/client_id.json')
my_drive.authenticate('../data/credentials.dat')
folder_id = my_drive.get_directory_id('s3')
drive_file_list = my_drive.list_files(folder_id)
print(drive_file_list)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


for file in local_file_list:
    file_path = os.path.join(path, file)
    if drive_file_list.get(file) is None:
        x = input("Do you wish to upload %s - %s" % (file, file_size(file_path))).lower()
        if x == 'yes':
            my_drive.upload_file(os.path.join(path, file), folder_id)

    else:
        if md5(file_path) == drive_file_list[file]:
            print("Already in the cloud : %s" %file)
        else:
            x = input("The file %s seemed to be changed. Do you want to push the local change to cloud?" %file).lower()
            if x == 'yes':
                my_drive.upload_file(os.path.join(path, file), folder_id)




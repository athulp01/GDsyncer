from Drive import GoogleDrive, Watcher
import os
import hashlib


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

#
# for file in local_file_list:
#     file_path = os.path.join(path, file)
#     if drive_file_list.get(file) is None:
#         x = input("Do you want to upload %s - %s\n" % (file, file_size(file_path))).lower()
#         if x == 'yes' or x == 'y':
#             my_drive.upload_file(os.path.join(path, file), folder_id)
#             print("Upload complete")
#
#     else:
#         if md5(file_path) != drive_file_list[file]:
#             x = input("The file %s seemed to be changed. Do you want to push the local change to cloud?\n" %file).lower()
#             if x == 'yes' or x == 'y':
#                 my_drive.upload_file(os.path.join(path, file), folder_id)
#                 print("Upload complete")
#


def main():
    my_drive = GoogleDrive('../data/client_id.json')
    my_drive.authenticate('../data/credentials.dat')
    path = "/home/athul/s3"
    s3_watcher = Watcher(path, my_drive)
    s3_watcher.pull()


if __name__ == "__main__":
    main()

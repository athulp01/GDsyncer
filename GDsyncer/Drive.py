from apiclient import discovery, http
from oauth2client import file, tools, client

import httplib2
import mimetypes
import os
import io
import hashlib


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class GoogleDrive:

    scopes = "https://www.googleapis.com/auth/drive"
    app_name = "GDsycncer"
    secret_file = ""
    credentials = None
    service = None

    def __init__(self, secret_file):
        """
        Set the secret_file variable
        :param string secret_file: path to the client_id.json
        """
        self.secret_file = secret_file

    def authenticate(self, credentials_path='credentials.dat'):
        """
        Redirect the user to a web authentication portal if not authenticated and then build the drive service.
        :param string credentials_path: Path to the file containing the user credentials
        :return: None
        """
        flow = client.flow_from_clientsecrets(self.secret_file, self.scopes)
        storage = file.Storage(credentials_path)
        cred = storage.get()
        if cred is None or cred.invalid:
            flow.user_agent = self.app_name
            cred = tools.run_flow(flow,storage)
        self.credentials = cred
        httpobj = httplib2.Http()
        httpobj = cred.authorize(httpobj)
        self.service = discovery.build('drive', 'v3', http=httpobj)

    def get_directory_id(self, name):
        """
        Get the id matching to the given name argument
        :param name: Exact name of the directory to be searched.
        :type name : String
        :return: ID(String) of the matching directory if it exists or else None
        """
        query = "mimeType = 'application/vnd.google-apps.folder' and name = '%s'" % name
        directory = self.service.files().list(q=query).execute()
        return directory.get('files')[0].get('id')

    def list_files(self, directory_id):
        """
        Get a list of all files in directory in the form of dict
        :param directory_id: Alphanumerical id of the parent directory
        :return: A dict with key as file name and value as file id
        """
        response = self.service.files().list(q="'%s' in parents" % directory_id, fields='files').execute()
        return response.get('files')

    def upload_file(self, file_path, folder_id=''):
        """
        Upload a file to a specified directory.
        :param file_path: Absolute or relative path to the file
        :param folder_id: The id of the directory to which the file is to be uploaded
        :return:
        """
        (directory, filename) = os.path.split(file_path)
        (mime, encoding) = mimetypes.guess_type(file_path)
        if mime is None:
            mime = "application/octet-stream"

        media = http.MediaFileUpload(file_path, mimetype=mime, resumable=True)
        body = {
            'name': filename,
            'parents': [folder_id]
        }
        self.service.files().create(body=body, media_body=media).execute()

    def create_folder(self, folder_name, parent_folder_id = ''):
        """
        Create a folder
        :param folder_name: Name of the folder to be created.
        :param parent_folder_id: Id of the parent folder. Created in the root folder by default.
        :return: ID of the created folder.
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': parent_folder_id
        }

        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def download_file(self, file_id):
        """
        Download a file given it's file id.
        :param file_id: File ID of the file to be downloaded.
        :return: ByteIO object of the file which can be saved to a file in the local system.
        """
        request = self.service.files().get_media(fileId=file_id)
        file_handler = io.BytesIO()
        downloader = http.MediaIoBaseDownload(file_handler, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return file_handler


class Watcher:

    def __init__(self, fold_name, root_dir, drive_object):
        self.root_dir = os.path.abspath(root_dir)
        self.drive_object = drive_object
        self.current_id = self.drive_object.get_directory_id(fold_name)
        contents = os.listdir(self.root_dir)
        self.local_files = set()
        self.local_folders = set()
        self.cloud_files = dict()
        self.cloud_folders = dict()
        md5 = lambda path : hashlib.md5(open(path,'rb').read()).hexdigest()
        for content in contents:
            path = os.path.join(root_dir, content)
            if os.path.isfile(path):
                self.local_files.add(content)
            else:
                self.local_folders.add(content)

        response = drive_object.list_files(self.current_id)
        # TODO 1: check for hashsum
        for file in response:
            if file.get("mimeType") == "application/vnd.google-apps.folder":
                if file.get('name') not in self.local_folders:
                    self.cloud_folders[file.get('name')] = file.get('id')
            else:
                if file.get('name') not in self.local_files:
                    self.cloud_files[file.get('name')] = file.get('id')
                else:
                    self.local_files.remove(file.get('name'))

    def push(self):
        # TODO 2: recursively upload(folder within a folder)
        for file in self.local_files:
                path = os.path.join(self.root_dir, file)
                print(bcolors.OKBLUE+"Uploading %s" % file + bcolors.ENDC)
                self.drive_object.upload_file(path, self.current_id)

    def pull(self):
        for name, id in self.cloud_files.items():
            file = open(os.path.join(self.root_dir, name), 'wb')
            print(bcolors.OKGREEN+"Downloading %s" % name + bcolors.ENDC)
            file.write(self.drive_object.download_file(id).getvalue())


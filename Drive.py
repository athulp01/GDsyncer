from apiclient import discovery, http
import httplib2
from oauth2client import file,tools,client


class Drive:

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

    def authenticate(self, credentials_path=None):
        """
        Redirect the user to a web authentication portal if not authenticated and then build the drive service.
        :param string credentials_path: Path to the file containing the user credentials
        :return: None
        """
        storage = file.Storage(credentials_path)
        cred = storage.get()
        if cred is None or cred.invalid:
            flow = client.flow_from_clientsecrets(self.secret_file, self.scopes)
            flow.user_agent = self.app_name
            cred = tools.run_flow(flow, storage)
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
        directory = self.service.files().list(q="mimeType = 'application/vnd.google-apps.folder' and name = %s" % name)
        return directory.get('id')

    def list_files(self, directory_id):
        """
        Get a list of all files in directory in the form of dict
        :param directory_id: Alphanumerical id of the parent directory
        :return: A dict with key as file name and value as file id
        """
        response = self.service.files().list(q="'%s' in parents" % directory_id).execute()
        files = {}
        for info in response.get('files'):
            files[info.get('name')] = info.get('id')
        return files

    def upload_file(self, file_path, folder_id):
        file_metadata = { 'name':'name.pdf', 'parents': [folder_id]}
        media = http.MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()


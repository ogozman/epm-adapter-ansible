import paramiko
import tempfile

class SSHExecutor():

    def __init__(self,
                 ip_address,
                 username="ubuntu",
                 password="",
                 key=None,
                 key_file_path=None):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.key = key
        self.key_file_path = key_file_path


    def _get_client(self):

        if self.key != None:
            return self._get_client_with_string()
        elif self.key_file_path != None:
            return self._get_client_with_file()
        else:
            raise Exception("No private key for authentication provided. Please provide a key as a string or file path.")


    def _get_client_with_file(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.ip_address, username=self.username, password=self.password,
                              key_filename=self.key_file_path)
        return client


    def _get_client_with_string(self):
        client = paramiko.SSHClient()
        client.get_host_keys().add(self.ip_address, 'ssh-rsa', self.key)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.ip_address, username=self.username, password=self.password)
        return client


    def execute_command(self, command):

        client = self._get_client()
        stdin, stdout, stderr = client.exec_command(command)
        output = ""
        for line in stdout:
            output += ' ' + line.strip('\n') + " "
        client.close()
        return output

    def download_file_from_container(self, path):
        f = tempfile.NamedTemporaryFile()

        client = self._get_client()
        sftp = client.open_sftp()
        sftp.getfo(path, f)
        sftp.close()
        client.close()
        f.seek(0)

        output = f.read()
        f.close()

        return output

    def upload_file(self, path, bytes):
        f = tempfile.NamedTemporaryFile()
        f.write(bytes)
        f.seek(0)

        client = self._get_client()
        sftp = client.open_sftp()
        sftp.putfo(f, remotepath=path)
        sftp.close()
        client.close()
        f.close()

    def upload_file_from_path(self, hostPath, remotePath):
        client = self._get_client()
        sftp = client.open_sftp()
        sftp.put(hostPath, remotePath)
        sftp.close()
        client.close()


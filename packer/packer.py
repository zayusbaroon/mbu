import os
import tarfile
import tomllib
from hashlib import blake2b

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC





class Packer:
    def __init__(self, config_path, watchee, pwd):

        with open(config_path, 'rb') as t:
            config = tomllib.load(t)
        self.bufsize = config['storage']['buffer_size']

        self.watchee = watchee
        self.watchee_name = os.path.basename(self.watchee.strip('/'))

        self.package_dir = config['packer']['package_directory']
        self.outfile = os.path.join(self.package_dir, self.watchee_name)
        self.restore_dir = config['packer']['restore_directory']
        self.send_dir = config['packer']['pigeon_upload_directory']
        self.recv_dir = config['packer']['pigeon_download_directory']



        salt = os.urandom(16)
        times = config['hash_iterations']
        self.kdf = PBKDF2HMAC(algorithm=hashes.BLAKE2s(32), length=32, salt=salt, iterations=times)

        self.key = self.kdf.derive(pwd)





    def make_package(self):
        tmp = 'temp.tar.gz'
        for i in [tmp, self.outfile]:
            if os.path.exists(i):
                os.remove(i)
        if not os.path.isdir(self.package_dir):
            os.mkdir(self.package_dir)

        with tarfile.open(tmp, 'w:gz') as tar:
                tar.add(self.watchee, arcname=self.watchee_name)

        iv = os.urandom(16)
        gcm = Cipher(algorithms.AES(self.key), modes.GCM(iv))
        encryptor = gcm.encryptor()
        with open(tmp, 'rb') as f:
            np = open(self.outfile, 'wb')
            while True:
                if (chunk := f.read(self.bufsize)) == b'':
                    np.write(encryptor.finalize())
                    np.write(iv)
                    np.write(encryptor.tag) #IV: EOF - 32; tag: EOF - 16
                    np.close()
                    break
                else:
                    np.write(encryptor.update(chunk))
        os.remove(tmp)
        return

    def pull(self):
        d = os.path.join(self.recv_dir, self.watchee_name)
        os.rename(d, self.outfile)
        return

    def push(self):
        d = os.path.join(self.send_dir, self.watchee_name)
        os.rename(self.outfile, d)
        return


    def depackage(self):
        src = self.outfile
        dest = self.outfile + '.tar.gz'

        with open(src, 'rb+') as f:
            f.seek(-32, 2)
            iv = f.read(16)
            tag = f.read(16)
            f.seek(-32, 2)
            f.truncate()
            f.seek(0)
            decryptor = Cipher(algorithms.AES(self.key), modes.GCM(iv, tag)).decryptor()
            g = open(dest, 'wb')
            while True:
                if (chunk := f.read(self.bufsize)) == b'':
                    g.write(decryptor.finalize())
                    g.close()
                    break
                else:
                    g.write(decryptor.update(chunk))

        with tarfile.open(dest, 'r:gz') as tar:
            tar.extractall(path=self.restore_dir)
        os.remove(dest)
        return



















    """'''def update_package(self, p, changes):
        new = os.path.join(self.packdir, 'new')
        files = []
        for i in changes:
            #should utilize transactions here

            files.append(self.db[1].execute('''SELECT * FROM file_data WHERE fname=?;''', changes[i]).fetchone())
        with open(self.outfile, 'rb') as f:
            g = open(new, 'w')
            for i in range(len(files)):
                try:
                    length = files[i+1]['offset'] - files[i]['offset']
                    wholes = length//self.bufsize
                    rsize =  length%self.bufsize
                    for ct in wholes:
                        g.write(f.read(self.bufsize))
                    g.write(f.read(rsize))

                except IndexError:
                    while True:
                       if (chunk := f.read(self.bufsize)) == '':
                           break
                       else:
                           g.write(chunk)
            g.close()

            os.remove(self.outfile)
            os.rename(new, self.outfile)










    def depackage(self):
        with open(self.outfile, 'rb') as f:
            g = open(self.restore)"""






from cryptography.fernet import Fernet

class PasswordManager:

    def __init__(self):
        self.key = None
        self.passwordFile = None
        self.passwordDict = {}

    def createKey(self, path):
        self.key = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(self.key)

    def loadKey(self, path):
        with open(path, 'rb') as f:
            self.key = f.read()

    def createPasswordFile(self, path, initialValues=None):
        self.passwordFile = path

        if initialValues != None:
            for key, value in initialValues.items():
                self.addPassword(key, value)
    
    def loadPasswordFile(self, path):
        self.passwordFile = path

        with open(path, 'r') as f:
            for line in f:
                site, encrypted = line.split(":")
                self.passwordDict[site] = Fernet(self.key).decrypt(encrypted.encode()).decode()
    
    def addPassword(self, site, password):
        self.passwordDict[site] = password

        if self.passwordFile != None:
            with open(self.passwordFile, 'a+') as f:
                encrypted = Fernet(self.key).encrypt(password.encode())
                f.write(site + ":" + encrypted.decode() + "\n")

    def getPassword(self, site):
        return self.passwordDict[site]

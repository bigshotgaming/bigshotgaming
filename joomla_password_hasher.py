import hashlib
from django.contrib.auth.hashers import BasePasswordHasher

class JoomlaPasswordHasher(BasePasswordHasher):
    algorithm = "joomla_md5"

    def encode(self, password, salt):
        hash = hashlib.md5(force_bytes(password + salt)).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        self.encode(password,)
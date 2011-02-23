from django.contrib.auth.models import User, check_password
from django.contrib.auth.backends import ModelBackend
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor, sha_constructor


def _new_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    
    This function does raw_password + salt instead of salt + raw_password
    in order to support legacy Joomla users.
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        print md5_constructor(raw_password + salt).hexdigest()
        return md5_constructor(raw_password + salt).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(raw_password + salt).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")


def _check_password(raw_password, enc_password):
    algo, salt, hsh = enc_password.split('$')
    return hsh == _new_hexdigest(algo, salt, raw_password)


def _user_check_password(self, raw_password):
    if '$' not in self.password:
        is_correct = (self.password == get_hexdigest('md5', '', raw_password))
        if is_correct:
            # Convert the password to the new, more secure format.
            self.set_password(raw_password)
            self.save()
        return is_correct
    return check_password(raw_password, self.password) or _check_password(raw_password, self.password)

User.check_password = _user_check_password

class LegacyPasswordBackend(ModelBackend):
    pass

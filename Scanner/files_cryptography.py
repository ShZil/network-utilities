from import_handler import ImportDefence
with ImportDefence():
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA256
    from Crypto.Util.Padding import pad, unpad



def password_encrypt(message: bytes, password: str) -> bytes:
    return Cipher_CBC(password=password).encrypt(message)


def password_decrypt(token: bytes, password: str) -> bytes:
    return Cipher_CBC(password=password).decrypt(token)


class Cipher_CBC:
    def _init_(self, password: str):
        """This function initializes the encryptor.

        Args:
            password (str): The password used to encrypt and decrypt the data.
        """
        password = SHA256.new(password.encode()).digest()
        key, iv = password[:128], password[128:]

        self._encryptor = AES.new(key, AES.MODE_CBC, iv)
        self._decryptor = AES.new(key, AES.MODE_CBC, iv)
    

    def encrypt(self, msg: bytes) -> bytes:
        """This function encrypts the message.

        Args:
            msg (bytes): The message to encrypt.

        Returns:
            bytes: The encrypted message.
        """
        return self._encryptor.encrypt(pad(msg, AES.block_size))
    

    def decrypt(self, ciphertext: bytes) -> bytes:
        """This function decrypts the message.

        Args:
            ciphertext (bytes): The ciphertext to decrypt.

        Returns:
            bytes: The decrypted message.
        """
        return unpad(self._decryptor.decrypt(ciphertext), AES.block_size)

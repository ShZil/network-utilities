from import_handler import ImportDefence
with ImportDefence():
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA256
    from Crypto.Random import get_random_bytes


def password_encrypt(message: bytes, password: str) -> bytes:
    return Cipher_EAX(password=password).encrypt(message)


def password_decrypt(token: bytes, password: str) -> bytes:
    return Cipher_EAX(password=password).decrypt(token)


class Cipher_EAX:
    def __init__(self, key=None, bytes=32, password=None):
        """This function initializes the encryptor.

        Args:
            key (bytes): The key used to encrypt and decrypt the data.
        """
        if key == None:
            if password != None:
                key = SHA256.new(password.encode()).digest()
            else:
                key = get_random_bytes(bytes)
        
        self.__key = key
        self._encryptor = AES.new(self._key, AES.MODE_EAX)
    
    def encrypt(self, msg):
        """This function encrypts the message.

        Args:
            msg (bytes): The message to encrypt.

        Returns:
            bytes: The encrypted message.
        """
        self._encryptor = AES.new(self._key, AES.MODE_EAX)
        ciphertext, tag = self.__encryptor.encrypt_and_digest(msg)
        return ciphertext, tag, self.__encryptor.nonce
    
    def decrypt(self, ciphertext, tag, nonce):
        """This function decrypts the message.

        Args:
            ciphertext (bytes): The ciphertext to decrypt.
            tag (bytes): The tag used to verify the ciphertext.
            nonce (bytes): The nonce used to decrypt the ciphertext.

        Returns:
            bytes: The decrypted message.
        """
        self._decryptor = AES.new(self._key, AES.MODE_EAX, nonce)
        plaintext = self.__decryptor.decrypt_and_verify(ciphertext, tag)
        return plaintext

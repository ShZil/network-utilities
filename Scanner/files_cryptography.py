from import_handler import ImportDefence
with ImportDefence():
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA256
    from Crypto.Util.Padding import pad, unpad



def password_encrypt(message: bytes, password: str) -> bytes:
    return Cipher_CBC(password=password).encrypt(message)


def password_decrypt(token: bytes, password: str) -> bytes:
    try:
        return Cipher_CBC(password=password).decrypt(token)
    except ValueError as e:
        print(e)
        return b''


class Cipher_CBC:
    def __init__(self, password: str):
        """This function initializes the encryptor.

        Args:
            password (str): The password used to encrypt and decrypt the data.
        """
        hashed = SHA256.new(password.encode()).digest()
        key, iv = hashed[:16], hashed[16:]

        self._encryptor = self._decryptor = AES.new(key, AES.MODE_CBC, iv)
    

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


if __name__ == '__main__':
    print("This is a module extending `files.py` with encryption.")
    print("It supplies `files.py` with two methods: password_encrypt and password_decrypt.")
    print("The internal implementation is irrelevant for `files.py`, and abstracted away.")
    print("\n\nExample: message=\"Hello, world!\", password=\"A123\", then:")
    message = "Hello, world!"
    password = "A123"
    encrypted = password_encrypt(message.encode(), password)
    print("Encrypted (HEX):", ' '.join(format(x, '02x').upper() for x in encrypted))
    decrypted = password_decrypt(encrypted, password)
    print("Decrypted:", decrypted)
    print("Example: enter file path:")
    try:
        with open(input(), 'rb') as f:
            print("Decrypted:", password_decrypt(f.read(), input("Password: ")))
    except Exception as e:
        print(e)
    input()

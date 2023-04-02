from import_handler import ImportDefence
with ImportDefence():
    from aes_cipher import DataEncrypter, DataDecrypter

def password_encrypt(message: bytes, password: str) -> bytes:
    data_encrypter = DataEncrypter()
    data_encrypter.Encrypt(message, password)
    return data_encrypter.GetEncryptedData()


def password_decrypt(message: bytes, password: str) -> bytes:
    data_decrypter = DataDecrypter()
    data_decrypter.Decrypt(message, password)
    return data_decrypter.GetDecryptedData()


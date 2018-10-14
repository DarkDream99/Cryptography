import rsa


def crypt(public_key: int, message: str) -> bytes:
    message = message.encode('utf-8')
    crypted_message = rsa.encrypt(message, public_key)
    return crypted_message


def decrypt(private_key: int, message: str) -> str:
    decrypted_message = rsa.decrypt(message, private_key)
    decrypted_message = decrypted_message.decode('utf-8')
    return decrypted_message


def create_keys():
    public_key, private_key = rsa.newkeys(512)
    return public_key, private_key



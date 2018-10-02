from cryptodes import des
from bitarray import bitarray


def test_des():
    bitdata = bitarray()
    bitkey = bitarray()

    text = "Hello, Denys. You are the best!!!"
    key = "arima san"
    code, entropies = des.encrypt(text, key)
    print(code)
    print(code.tobytes().decode("utf-8", 'replace'))

    print(entropies)

    decode = des.decrypt(code, key)
    print(decode)
    print(decode.tobytes().decode("utf-8", "replace"))


test_des()

from tables import initial_permutation
from bitarray import bitarray


def create_keys(key_bytes: bitarray) -> list:
    key_bytes = key_bytes[:56]
    while len(key_bytes) < 56:
        key_bytes.append(0)

    round_keys = list()

    return round_keys


def encrypt(data_bits: bitarray, key_bits: bitarray) -> bitarray:
    while len(data_bits) < 64:
        data_bits.append(0)

    print(data_bits.tostring())
    print(data_bits)
    for ind in range(1, len(data_bits) + 1):
        data_bits[ind - 1], data_bits[initial_permutation[ind] - 1] = \
            data_bits[initial_permutation[ind] - 1], data_bits[ind - 1]

    print(data_bits)
    # print(data_bits.tostring())

    # raise NotImplementedError()


def decrypt(code_bytes: bytearray, key_bytes: bytearray) -> bytearray:
    raise NotImplementedError()


if __name__ == "__main__":
    # bits = bitarray(endian="little")
    # bits.fromstring("A")
    # print(bits)

    bitdata = bitarray(endian='big')
    bitkey = bitarray()

    bitdata.fromstring("Hello, Denys")
    bitkey.fromstring("key")
    encrypt(bitdata[:64], bitkey)

    # encrypt(bytearray("Hello Denys. I'm fine", encoding="utf-8"), bytearray("key", encoding="utf-8"))
    # text = "hello "
    #
    # bits = bytearray(text, encoding="utf-8")
    # print(bits)

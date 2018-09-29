from tables import initial_permutation
from tables import extend_key_permutation_c
from tables import extend_key_permutation_d
from tables import cyclic_shift
from bitarray import bitarray


def shift_left(data: bitarray, size) -> bitarray:
    res = bitarray(len(data))
    for ind in range(0, len(data) - size):
        res[ind] = data[ind + size]

    for ind in range(len(data) - size):
        res[ind] = 0

    return res


def create_keys(key_bytes: bitarray) -> list:
    while len(key_bytes) < 56:
        key_bytes.append(0)

    key_bytes.insert(7, 1)
    key_bytes.insert(15, 1)
    key_bytes.insert(23, 1)
    key_bytes.insert(31, 1)
    key_bytes.insert(39, 1)
    key_bytes.insert(47, 1)
    key_bytes.insert(55, 1)
    key_bytes.insert(63, 1)

    round_keys = list()
    c0 = bitarray(28)
    d0 = bitarray(28)

    for ind in range(1, 28 + 1):
        c0[ind - 1] = extend_key_permutation_c[ind]
        d0[ind - 1] = extend_key_permutation_d[ind]

    for shift_ind in range(1, 16 + 1):
        ci = c0 << cyclic_shift[shift_ind]
        di = d0 << cyclic_shift[shift_ind]
        round_keys.append(ci.append(di))
        print(round_keys[shift_ind - 1])

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
    # encrypt(bitdata[:64], bitkey)
    create_keys(bitkey)

    # encrypt(bytearray("Hello Denys. I'm fine", encoding="utf-8"), bytearray("key", encoding="utf-8"))
    # text = "hello "
    #
    # bits = bytearray(text, encoding="utf-8")
    # print(bits)

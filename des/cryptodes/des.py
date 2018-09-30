from tables import initial_permutation
from tables import extend_key_permutation_c
from tables import extend_key_permutation_d
from tables import cyclic_shift
from tables import key_bits_positions
from bitarray import bitarray


def shift_left(data: bitarray, size) -> bitarray:
    res = bitarray(len(data))
    for ind in range(0, len(data) - size):
        res[ind] = data[ind + size]

    for ind in range(len(data) - size, len(data)):
        res[ind] = 0

    return res


def create_keys(key_bits: bitarray) -> list:
    while len(key_bits) < 56:
        key_bits.append(0)

    key_bits.insert(7, 1)
    key_bits.insert(15, 1)
    key_bits.insert(23, 1)
    key_bits.insert(31, 1)
    key_bits.insert(39, 1)
    key_bits.insert(47, 1)
    key_bits.insert(55, 1)
    key_bits.insert(63, 1)

    round_keys = list()
    c0 = bitarray(28)
    c0.setall(False)
    d0 = bitarray(28)
    d0.setall(False)

    for ind in range(1, 28 + 1):
        c0[ind - 1] = key_bits[extend_key_permutation_c[ind]]
        d0[ind - 1] = key_bits[extend_key_permutation_d[ind]]

    for shift_ind in range(1, 16 + 1):
        ci = shift_left(c0, cyclic_shift[shift_ind])
        di = shift_left(d0, cyclic_shift[shift_ind])
        c0 = ci.copy()
        d0 = di.copy()
        ci.extend(di)
        ki = bitarray(48)
        for ind in range(1, 48 + 1):
            ki[ind - 1] = ci[key_bits_positions[ind] - 1]
        round_keys.append(ki)
        # print(round_keys[shift_ind - 1])
        # print(round_keys[shift_ind - 1].tobytes())
        # print(round_keys[shift_ind - 1].tobytes().decode('utf-8', 'replace'))

    return round_keys


def encrypt(data_bits: bitarray, key_bits: bitarray) -> bitarray:
    while len(data_bits) < 64:
        data_bits.append(0)

    print(data_bits)
    print(data_bits.tobytes().decode('utf-8', 'replace'))
    for ind in range(1, len(data_bits) + 1):
        data_bits[ind - 1], data_bits[initial_permutation[ind] - 1] = \
            data_bits[initial_permutation[ind] - 1], data_bits[ind - 1]

    keys = create_keys(key_bits)

    print(data_bits)
    print(data_bits.tobytes().decode('utf-8', 'replace'))


def decrypt(code_bytes: bytearray, key_bytes: bytearray) -> bytearray:
    raise NotImplementedError()


if __name__ == "__main__":
    # bits = bitarray(endian="little")
    # bits.fromstring("A")
    # print(bits)

    bitdata = bitarray()
    bitkey = bitarray()

    bitdata.fromstring("Hello, Denys")
    bitkey.fromstring("arima san")
    encrypt(bitdata[:64], bitkey)
    # create_keys(bitkey)
    # bitdata.tobytes()

    # encrypt(bytearray("Hello Denys. I'm fine", encoding="utf-8"), bytearray("key", encoding="utf-8"))
    # text = "hello "
    #
    # bits = bytearray(text, encoding="utf-8")
    # print(bits)

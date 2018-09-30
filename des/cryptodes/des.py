from tables import initial_permutation
from tables import extend_key_permutation_c
from tables import extend_key_permutation_d
from tables import cyclic_shift
from tables import key_bits_positions
from tables import extension_E
from tables import transformation_S
from tables import permutation_p
from tables import last_permutation
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

    for shift_ind in range(16):
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


def extension_e(part_r: bitarray) -> bitarray:
    extension_r = bitarray()
    for ind in range(48):
        extension_r.append(part_r[extension_E[ind]])

    return extension_r


def _convert_to_string(bits: bitarray) -> str:
    res = ""
    for ind in range(len(bits)):
        if bits[ind]:
            res += '1'
        else:
            res += '0'

    return res


def _convert_to_bits(value: int) -> str:
    res = ""
    while value != 0:
        if value % 2 != 0:
            res = '1' + res
        else:
            res = '0' + res
        value //= 2

    return res.zfill(4)


def transform_s(data: bitarray) -> bitarray:
    def make_index(bits: bitarray) -> int:
        bin_a = bitarray()
        bin_a.append(bits[0])
        bin_a.append(bits[5])

        bin_b = bitarray()
        bin_b.append(bits[1])
        bin_b.append(bits[2])
        bin_b.append(bits[3])
        bin_b.append(bits[4])

        key_a = int(_convert_to_string(bin_a), 2)
        key_b = int(_convert_to_string(bin_b), 2)

        index = key_a * 16 + key_b
        return index

    blocks = []
    block = bitarray()
    for ind in range(len(data)):
        if ind % 6 == 0 and ind != 0:
            blocks.append(block)
            block = bitarray()
        block.append(data[ind])
    blocks.append(block)

    res = bitarray()
    for block_id in range(8):
        index = make_index(blocks[block_id])
        block = transformation_S[block_id][index]
        str_bits = _convert_to_bits(block)
        res.extend(str_bits)

    return res


def do_permutation_p(data: bitarray) -> bitarray:
    res = bitarray()
    for index in range(32):
        res.append(data[permutation_p[index]])

    return res


def do_func_feistel(part_r: bitarray, key: bitarray) -> bitarray:
    extend_part_r = extension_E(part_r)
    extend_part_r = extend_part_r ^ key
    extend_part_r = transform_s(extend_part_r)
    extend_part_r = do_permutation_p(extend_part_r)

    return extend_part_r


def do_last_permutation(data: bitarray) -> bitarray:
    res = bitarray()
    for ind in range(64):
        res.append(data[last_permutation[ind]])

    return res


def encrypt(data_bits: bitarray, key_bits: bitarray) -> bitarray:
    while len(data_bits) < 64:
        data_bits.append(0)

    print(data_bits)
    print(data_bits.tobytes().decode('utf-8', 'replace'))
    for ind in range(1, len(data_bits)):
        data_bits[ind - 1], data_bits[initial_permutation[ind]] = \
            data_bits[initial_permutation[ind]], data_bits[ind - 1]

    keys = create_keys(key_bits)
    part_l = data_bits[:32]
    part_r = data_bits[32:]
    for counter in range(16):
        li = part_r
        ri = part_l ^ do_func_feistel(part_r, keys[counter])
        part_l, part_r = li, ri

    one_part = part_l.extend(part_r)
    res = do_last_permutation(one_part)

    print(res)
    print(res.tobytes().decode('utf-8', 'replace'))

    return res


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
    # encrypt(bitdata[:64], bitkey)
    transform_s(bitdata[:48])
    # create_keys(bitkey)
    # bitdata.tobytes()

    # encrypt(bytearray("Hello Denys. I'm fine", encoding="utf-8"), bytearray("key", encoding="utf-8"))
    # text = "hello "
    #
    # bits = bytearray(text, encoding="utf-8")
    # print(bits)

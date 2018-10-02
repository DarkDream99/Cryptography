from bitarray import bitarray
from . import tables


_KEY_SIZE = 56
_BLOCK_SIZE = 64


def _shift_left(data: bitarray, size) -> bitarray:
    res = bitarray(len(data))
    for ind in range(0, len(data) - size):
        res[ind] = data[ind + size]

    for ind in range(len(data) - size, len(data)):
        res[ind] = 0

    return res


def is_low_key(key: str) -> bool:
    bit_key = bitarray()
    bit_key.fromstring(key)
    bit_key = bit_key[:56]
    while len(bit_key) < 56:
        bit_key.append(0)

    part_l = bit_key[:28]
    part_r = bit_key[28:]
    zeros_l = 0
    zeros_r = 0

    for ind in range(len(part_l)):
        if not part_l[ind]:
            zeros_l += 1
        if not part_r[ind]:
            zeros_r += 1

    return zeros_l == 28 or zeros_r == 28


def _find_entropy(bit_block_l: bitarray, bit_block_r: bitarray) -> float:
    count_bits = len(bit_block_l) + len(bit_block_r)
    count_ones = 0

    for bit in bit_block_l:
        if bit:
            count_ones += 1

    for bit in bit_block_r:
        if bit:
            count_ones += 1

    from math import log2
    p1 = count_ones / count_bits
    p0 = 1 - p1
    entropy = -(p1 * log2(p1) + p0 * log2(p0))

    return entropy


def _create_keys(key_bits: bitarray) -> list:
    while len(key_bits) < 56:
        key_bits.append(0)

    key_bits.insert(7,  1)
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

    for ind in range(28):
        c0[ind] = key_bits[tables.extend_key_permutation_c[ind]]
        d0[ind] = key_bits[tables.extend_key_permutation_d[ind]]

    for shift_ind in range(16):
        ci = _shift_left(c0, tables.cyclic_shift[shift_ind])
        di = _shift_left(d0, tables.cyclic_shift[shift_ind])
        c0 = ci.copy()
        d0 = di.copy()
        ci.extend(di)
        ki = bitarray(48)
        for ind in range(0, 48):
            ki[ind] = ci[tables.key_bits_positions[ind]]
        round_keys.append(ki)

    return round_keys


def _extension_e(part_r: bitarray) -> bitarray:
    extension_r = bitarray()
    for ind in range(48):
        extension_r.append(part_r[tables.extension_E[ind]])

    return extension_r


def convert_to_string(bits: bitarray) -> str:
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


def _transform_s(data: bitarray) -> bitarray:
    def make_index(bits: bitarray) -> int:
        bin_a = bitarray()
        bin_a.append(bits[0])
        bin_a.append(bits[5])

        bin_b = bitarray()
        bin_b.append(bits[1])
        bin_b.append(bits[2])
        bin_b.append(bits[3])
        bin_b.append(bits[4])

        key_a = int(convert_to_string(bin_a), 2)
        key_b = int(convert_to_string(bin_b), 2)

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
        block = tables.transformation_S[block_id][index]
        str_bits = _convert_to_bits(block)
        res.extend(str_bits)

    return res


def _do_permutation_p(data: bitarray) -> bitarray:
    res = bitarray()
    for index in range(32):
        res.append(data[tables.permutation_p[index]])

    return res


def _do_func_feistel(part_r: bitarray, key: bitarray) -> bitarray:
    extend_part_r = _extension_e(part_r)
    extend_part_r = extend_part_r ^ key
    extend_part_r = _transform_s(extend_part_r)
    extend_part_r = _do_permutation_p(extend_part_r)

    return extend_part_r


def _do_last_permutation(data: bitarray) -> bitarray:
    res = bitarray()
    for ind in range(64):
        res.append(data[tables.last_permutation[ind]])

    return res


def _encrypt(data_bits: bitarray, key_bits: bitarray) -> list:
    while len(data_bits) < 64:
        data_bits.append(0)

    permutation_data = bitarray()
    for ind in range(0, len(data_bits)):
        permutation_data.append(data_bits[tables.initial_permutation[ind]])

    entropies = list()
    keys = _create_keys(key_bits)
    part_l = permutation_data[:32]
    part_r = permutation_data[32:]
    entropies.append(_find_entropy(part_l, part_r))
    for counter in range(16):
        li = part_r
        ri = part_l ^ _do_func_feistel(part_r, keys[counter])
        part_l, part_r = li, ri
        entropies.append(_find_entropy(part_l, part_r))

    one_part = part_l
    one_part.extend(part_r)
    res = _do_last_permutation(one_part)

    return [res, entropies]


def _decrypt(code_bits: bitarray, key_bits: bitarray) -> bitarray:
    permutation_code = bitarray()
    for ind in range(0, len(code_bits)):
        permutation_code.append(code_bits[tables.initial_permutation[ind]])

    keys = _create_keys(key_bits)
    part_l = permutation_code[:32]
    part_r = permutation_code[32:]
    for counter in range(15, 0 - 1, -1):
        ri = part_l
        li = part_r ^ _do_func_feistel(part_l, keys[counter])
        part_l, part_r = li, ri

    one_part = part_l
    one_part.extend(part_r)
    res = _do_last_permutation(one_part)

    # print(res)
    # print(res.tobytes().decode('utf-8', 'replace'))

    return res


def _cut_key(key: bitarray) -> list:
    keys = list()
    key_block = bitarray()

    for bit in key:
        if len(key_block) != 0 and len(key_block) % _KEY_SIZE == 0:
            keys.append(key_block)
            key_block = bitarray()
        key_block.append(bit)

    if len(key_block) > 0:
        while len(key_block) < _KEY_SIZE:
            key_block.append(0)

        keys.append(key_block)

    return keys


def encrypt(text: str, key: str) -> tuple:
    bit_text = bitarray()
    bit_key = bitarray()

    bit_text.fromstring(text)
    bit_key.fromstring(key)

    # bit_key = bit_key[:_KEY_SIZE]
    bit_keys = _cut_key(bit_key)
    code = bitarray()
    block = bitarray()

    key_index = 0
    entropies = list()
    for ind in range(len(bit_text)):
        if ind != 0 and ind % _BLOCK_SIZE == 0:
            code_block, entropy = _encrypt(block, bit_keys[key_index])
            key_index = (key_index + 1) % len(bit_keys)
            entropies.append([convert_to_string(block), entropy])
            code.extend(code_block)
            block = bitarray(0)
        block.append(bit_text[ind])

    code_block, entropy = _encrypt(block, bit_keys[key_index])
    entropies.append([convert_to_string(block), entropy])
    code.extend(code_block)

    return code, entropies


def decrypt(code: bitarray, key: str) -> bitarray:
    bit_key = bitarray()
    bit_key.fromstring(key)

    # bit_key = bit_key[:_KEY_SIZE]
    bit_keys = _cut_key(bit_key)
    decode = bitarray()
    block = bitarray()

    key_index = 0
    for ind in range(len(code)):
        if ind != 0 and ind % _BLOCK_SIZE == 0:
            decode_block = _decrypt(block, bit_keys[key_index])
            key_index = (key_index + 1) % len(bit_keys)
            decode.extend(decode_block)
            block = bitarray(0)
        block.append(code[ind])

    decode_block = _decrypt(block, bit_keys[key_index])
    decode.extend(decode_block)

    return decode

from tables import initial_permutation


def encrypt(data_bytes: bytearray, key_bytes: bytearray) -> bytearray:
    while len(data_bytes) < 64:
        data_bytes.append(0)

    print(data_bytes.decode("utf-8"))
    for ind in range(1, len(data_bytes) + 1):
        data_bytes[ind - 1], data_bytes[initial_permutation[ind] - 1] = \
            data_bytes[initial_permutation[ind] - 1], data_bytes[ind - 1]

    print(data_bytes.decode("utf-8"))

    # raise NotImplementedError()


def decrypt(code_bytes: bytearray, key_bytes: bytearray) -> bytearray:
    raise NotImplementedError()


if __name__ == "__main__":
    encrypt(bytearray("Hello Denys. I'm fine", encoding="utf-8"), bytearray("key", encoding="utf-8"))
    # text = "hello "
    #
    # bits = bytearray(text, encoding="utf-8")
    # print(bits)

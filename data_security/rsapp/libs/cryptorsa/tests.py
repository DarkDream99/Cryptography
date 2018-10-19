from random import random
from math import gcd


def find_primes(n):
    """ Returns  a list of primes < n """
    sieve = [True] * n
    for i in range(3, int(n**0.5)+1, 2):
        if sieve[i]:
            sieve[i*i::2*i] = [False]*((n-i*i-1) // (2*i) + 1)
    return [2] + [i for i in range(3, n, 2) if sieve[i]]


primes = find_primes(999999)


def two_primes_not_equal_numbers():
    i, j = 1, 1

    while i == j:
        i = int(random() * 100)
        j = int(random() * 100)

    return primes[i], primes[j]


def find_middle_number(max_number):
    num = 5
    while gcd(num, max_number) > 1:
        num = int(2 + random() * max_number)

    return num


class PublicKey(object):
    def __init__(self, e=None, n=1024):
        self.e = e
        self.n = n


class PrivateKey(object):
    def __init__(self, d=None, n=1024):
        self.d = d
        self.n = n


def create_keys():
    p, q = two_primes_not_equal_numbers()
    n = p * q
    fi = (p-1) * (q-1)
    e = find_middle_number(fi)
    d = (1 / e) % fi

    pub_key = PublicKey(e, n)
    priv_key = PrivateKey(d, n)

    return pub_key, priv_key


def crypt(bmessage: bytes, pub_key: PublicKey):
    C = list()

    for bt in bmessage:
        cbt = pow(bt, pub_key.e, pub_key.n)
        C.append(cbt)

    return C


def decrypt(cbytes: list, priv_key: PrivateKey):
    P = list()

    for cbt in cbytes:
        bt = pow(int(cbt), priv_key.d) % priv_key.n
        P.append(bt)

    return P


pub_key, priv_key = create_keys()
message = b"hello"
print(list(bytes(message)))
crypt_message = crypt(message, pub_key)
print(crypt_message)

decrypt_message = decrypt(crypt_message, priv_key)
print(decrypt_message)




import random
import string

import rc5

key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))  # random 256-bit key

W = 64  # половина длины блока (рекомендуется т.к. 64 бита система)
R = 20  # количество раундов, по рекомендации RSA Security Inc.
cipher = rc5.RC5(64, 20, key.encode())

cipher.encrypt_file("resources/plaintext.txt", "resources/cyphertext.txt")
cipher.decrypt_file("resources/cyphertext.txt", "resources/decyphertext.txt")

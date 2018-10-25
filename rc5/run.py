import random
import string
import os

import rc5
import hash_function

from config import *


def generate_random_file(file_name, file_size):
    """
    Generate new random file from /dev/urandom
    :param file_name: name of file
    :param file_size: file size in bytes
    :return:
    """
    os.system(f'rm {file_name}')
    os.system(f'touch {file_name}')
    os.system(f'head -c {file_size} </dev/urandom > {file_name}')


if __name__ == '__main__':
    cipher = rc5.RC5(W, R, ('\x00' * 32).encode())
    hash_fun = hash_function.HashFunction()

    all_tests_correct = True
    for i in range(1, number_of_tests + 1):
        generate_random_file(plaintext_file_name, plaintext_file_size)
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))  # random 256-bit _key
        cipher.update_key(key.encode())

        cipher.encrypt_file(plaintext_file_name, cyphertext_file_name)
        cipher.decrypt_file(cyphertext_file_name, decypertext_file_name)

        plain_hash = hash_fun.get_file_hash_hex(plaintext_file_name)
        cypher_hash = hash_fun.get_file_hash_hex(cyphertext_file_name)
        decypher_hash = hash_fun.get_file_hash_hex(decypertext_file_name)

        print(f'\n******************************** TEST {i} ********************************', end='\n\n')

        print('Key:', key)
        print(f'File size: {plaintext_file_size} Bytes', end='\n\n')

        print('Plaintext file hash:', plain_hash, end='\n\n')
        print('Ciphered file hash:', cypher_hash, end='\n\n')
        print('Deciphered file hash:', decypher_hash, end='\n\n')

        if plain_hash != decypher_hash:
            all_tests_correct = False
            print('Test failed!!! ')
            break

        print('Plaintext == Deciphered text:', plain_hash == decypher_hash)

    print('\n************************************************************************', end='\n\n')

    if all_tests_correct:
        print('All tests correct!!!')

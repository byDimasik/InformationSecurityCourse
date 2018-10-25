plaintext_file_name = 'resources/plaintext.txt'
cyphertext_file_name = 'resources/cyphertext.txt'
decypertext_file_name = 'resources/decyphertext.txt'

number_of_tests = 1
plaintext_file_size = 10 * 1024  # 10 KB

W = 64  # half of block length (recommended for 64-bit systems)
R = 20  # number of rounds, recommended by RSA Security Inc.

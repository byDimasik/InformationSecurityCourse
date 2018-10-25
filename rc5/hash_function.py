import rc5


class HashFunction(rc5.RC5):
    """
    Hash function based on RC5 block-cipher algorithm
    Hash formula: h[i] = RC5.encrypt_block(data_block[i], key=h[i-1]) ^ data_block[i]
    """
    def __init__(self):
        self._key = '\x00' * 32
        rc5.RC5.__init__(self, 64, 20, self._key.encode())

    def __reset_key(self):
        self.update_key(('\x00' * 32).encode())

    def calculate_file_hash(self, input_file_name):
        """
        Calculate file hash
        :param input_file_name: name of file for hashing
        :return: list with file hash bytes
        """
        result_hash = None

        with open(input_file_name, 'rb') as input_file:
            run = True
            while run:
                text = input_file.read(self._W4)
                if not text:
                    break

                if len(text) != self._W4:
                    text = text.ljust(self._W4, b'\x00')
                    run = False

                cipher_text = self._encrypt_block(text)

                result_hash = [x ^ y for x, y in zip(cipher_text, text)]
                self.update_key(result_hash)

        self.__reset_key()
        return result_hash

    def get_file_hash_hex(self, file_name):
        """
        Get file hash in HEX form
        :param file_name: name of file for hashing
        :return: string with file hash in HEX form
        """
        list_hash = self.calculate_file_hash(file_name)
        return ''.join(["%02X " % x for x in list_hash])

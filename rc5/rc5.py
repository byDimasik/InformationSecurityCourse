import struct


class RC5:
    def __init__(self, w, r, key):
        self._W = w
        self._R = r
        self._key = key

        self._T = 2 * (self._R + 1)
        self._W4 = self._W // 4
        self._W8 = self._W // 8
        self._mod = 2 ** self._W
        self._mask = self._mod - 1

        self._b = len(key)

        self._L = []
        self._S = []
        self._c = 1

        self._key_align()
        self._key_extend()
        self._shuffle()

    def __lshift(self, val, n):
        n %= self._W
        return ((val << n) & self._mask) | ((val & self._mask) >> (self._W - n))

    def __rshift(self, val, n):
        n %= self._W
        return ((val & self._mask) >> n) | (val << (self._W - n) & self._mask)

    def __const(self):
        """
        Constants generation

        :return: P, Q values
        """

        if 16 == self._W:
            return 0xB7E1, 0x9E37
        elif 32 == self._W:
            return 0xB7E15163, 0x9E3779B9
        elif 64 == self._W:
            return 0xB7E151628AED2A6B, 0x9E3779B97F4A7C15

    def _key_align(self):
        if 0 == self._b:
            self._c = 1
        elif 0 == self._b % self._W8:
            self._c = self._b // self._W8
        else:
            self._key += b'\x00' * (self._W8 - self._b % self._W8)
            self._b = len(self._key)
            self._c = self._b // self._W8

        l = [0] * self._c
        for i in range(self._b - 1, -1, -1):
            l[i // self._W8] = (l[i // self._W8] << 8) + self._key[i]
        self._L = l

    def _key_extend(self):
        P, Q = self.__const()
        self._S = [(P + i * Q) % self._mod for i in range(self._T)]

    def _shuffle(self):
        i, j, A, B = 0, 0, 0, 0

        for k in range(3 * max(self._c, self._T)):
            A = self._S[i] = self.__lshift((self._S[i] + A + B), 3)
            B = self._L[j] = self.__lshift((self._L[j] + A + B), A + B)
            i = (i + 1) % self._T
            j = (j + 1) % self._c

    def _encrypt_block(self, data):
        A = int.from_bytes(data[:self._W8], byteorder='little')
        B = int.from_bytes(data[self._W8:], byteorder='little')
        A = (A + self._S[0]) % self._mod
        B = (B + self._S[1]) % self._mod

        for i in range(1, self._R + 1):
            A = (self.__lshift((A ^ B), B) + self._S[2 * i]) % self._mod
            B = (self.__lshift((A ^ B), A) + self._S[2 * i + 1]) % self._mod

        return (A.to_bytes(self._W8, byteorder='little')
                + B.to_bytes(self._W8, byteorder='little'))

    def __decrypt_block(self, data):
        A = int.from_bytes(data[:self._W8], byteorder='little')
        B = int.from_bytes(data[self._W8:], byteorder='little')

        for i in range(self._R, 0, -1):
            B = self.__rshift(B - self._S[2 * i + 1], A) ^ A
            A = self.__rshift(A - self._S[2 * i], B) ^ B

        B = (B - self._S[1]) % self._mod
        A = (A - self._S[0]) % self._mod

        return (A.to_bytes(self._W8, byteorder='little')
                + B.to_bytes(self._W8, byteorder='little'))

    def __encrypt_bytes(self, data):
        res, run = b'', True
        while run:
            temp = data[:self._W4]
            if len(temp) != self._W4:
                data = data.ljust(self._W4, b'\x00')
                run = False

            res += self._encrypt_block(temp)
            data = data[self._W4:]

            if not data:
                break

        return res

    def encrypt_file(self, input_file_name, output_file_name):
        with open(input_file_name, 'rb') as input_file, open(output_file_name, 'wb') as output_file:

            from os import stat
            file_size = stat(input_file_name).st_size
            size_bytes = struct.pack('i', file_size)
            output_file.write(self._encrypt_block(size_bytes.ljust(self._W4)))

            run = True
            while run:
                text = input_file.read(self._W4)
                if not text:
                    break

                if len(text) != self._W4:
                    text = text.ljust(self._W4, b'\x00')
                    run = False

                text = self._encrypt_block(text)
                output_file.write(text)

    def decrypt_file(self, input_file_name, output_file_name):
        with open(input_file_name, 'rb') as input_file, open(output_file_name, 'wb') as output_file:
            size_bytes = input_file.read(self._W4)
            if not size_bytes or len(size_bytes) < self._W4:
                return

            size_bytes = self.__decrypt_block(size_bytes)
            file_size = struct.unpack('i', size_bytes[:4])[0]

            run = True
            while run:
                text = input_file.read(self._W4)
                if not text:
                    break

                text = self.__decrypt_block(text)

                if file_size >= self._W4:
                    file_size -= output_file.write(text)
                else:
                    output_file.write(text[:file_size])

    def update_key(self, new_key):
        self._key = new_key
        self._b = len(new_key)

        self._L = []
        self._S = []
        self._c = 1

        self._key_align()
        self._key_extend()
        self._shuffle()

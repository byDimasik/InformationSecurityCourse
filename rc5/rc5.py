import struct


class RC5:
    def __init__(self, w, r, key):
        self.W = w
        self.R = r
        self.key = key

        self.T = 2 * (self.R + 1)
        self.W4 = self.W // 4
        self.W8 = self.W // 8
        self.mod = 2 ** self.W
        self.mask = self.mod - 1
        self.b = len(key)

        self.__key_align()
        self.__key_extend()
        self.__shuffle()

    def __lshift(self, val, n):
        n %= self.W
        return ((val << n) & self.mask) | ((val & self.mask) >> (self.W - n))

    def __rshift(self, val, n):
        n %= self.W
        return ((val & self.mask) >> n) | (val << (self.W - n) & self.mask)

    def __const(self):
        """
        Constants generation

        :return: P, Q values
        """

        if 16 == self.W:
            return 0xB7E1, 0x9E37
        elif 32 == self.W:
            return 0xB7E15163, 0x9E3779B9
        elif 64 == self.W:
            return 0xB7E151628AED2A6B, 0x9E3779B97F4A7C15

    def __key_align(self):
        if 0 == self.b:
            self.c = 1
        elif 0 == self.b % self.W8:
            self.c = self.b // self.W8
        else:
            self.key += b'\x00' * (self.W8 - self.b % self.W8)
            self.b = len(self.key)
            self.c = self.b // self.W8

        l = [0] * self.c
        for i in range(self.b - 1, -1, -1):
            l[i // self.W8] = (l[i // self.W8] << 8) + self.key[i]
        self.L = l

    def __key_extend(self):
        P, Q = self.__const()
        self.S = [(P + i * Q) % self.mod for i in range(self.T)]

    def __shuffle(self):
        i, j, A, B = 0, 0, 0, 0

        for k in range(3 * max(self.c, self.T)):
            A = self.S[i] = self.__lshift((self.S[i] + A + B), 3)
            B = self.L[j] = self.__lshift((self.L[j] + A + B), A + B)
            i = (i + 1) % self.T
            j = (j + 1) % self.c

    def __encrypt_block(self, data):
        A = int.from_bytes(data[:self.W8], byteorder='little')
        B = int.from_bytes(data[self.W8:], byteorder='little')
        A = (A + self.S[0]) % self.mod
        B = (B + self.S[1]) % self.mod

        for i in range(1, self.R + 1):
            A = (self.__lshift((A ^ B), B) + self.S[2 * i]) % self.mod
            B = (self.__lshift((A ^ B), A) + self.S[2 * i + 1]) % self.mod

        return (A.to_bytes(self.W8, byteorder='little')
                + B.to_bytes(self.W8, byteorder='little'))

    def __decrypt_block(self, data):
        A = int.from_bytes(data[:self.W8], byteorder='little')
        B = int.from_bytes(data[self.W8:], byteorder='little')

        for i in range(self.R, 0, -1):
            B = self.__rshift(B - self.S[2 * i + 1], A) ^ A
            A = self.__rshift(A - self.S[2 * i], B) ^ B

        B = (B - self.S[1]) % self.mod
        A = (A - self.S[0]) % self.mod

        return (A.to_bytes(self.W8, byteorder='little')
                + B.to_bytes(self.W8, byteorder='little'))

    def encrypt_file(self, input_file_name, output_file_name):
        with open(input_file_name, 'rb') as input_file, open(output_file_name, 'wb') as output_file:

            from os import stat
            file_size = stat(input_file_name).st_size
            size_bytes = struct.pack('i', file_size)
            output_file.write(self.__encrypt_block(size_bytes.ljust(self.W4)))

            run = True
            while run:
                text = input_file.read(self.W4)
                if not text:
                    break

                if len(text) != self.W4:
                    text = text.ljust(self.W4, b'\x00')
                    run = False

                text = self.__encrypt_block(text)
                output_file.write(text)

    def decrypt_file(self, input_file_name, output_file_name):
        with open(input_file_name, 'rb') as input_file, open(output_file_name, 'wb') as output_file:
            size_bytes = input_file.read(self.W4)
            if not size_bytes or len(size_bytes) < self.W4:
                return

            size_bytes = self.__decrypt_block(size_bytes)
            file_size = struct.unpack('i', size_bytes[:4])[0]

            run = True
            while run:
                text = input_file.read(self.W4)
                if not text:
                    break

                text = self.__decrypt_block(text)

                if file_size >= self.W4:
                    file_size -= output_file.write(text)
                else:
                    output_file.write(text[:file_size])

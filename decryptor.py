#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : decrypt.py
# Author        : bssthu
# Project       : pysqlsimplecipher
# Creation date : 2016-06-03
# Description   :
#


import sys
from pysqlsimplecipher import decryptor


def usage():
    print('Usage: python decrypt.py encrypted.db password output.db')


def main(p = '9bf9c6ed9d537c399a6c4513e92ab24717e1a488381e3338593abd923fc8a13b'): 
    filename_in = 'dataenc.db'
    password = bytearray(p.encode('utf8'))
    filename_out = 'database.db'

    decryptor.decrypt_file(filename_in, password, filename_out)


if __name__ == '__main__':
    main()

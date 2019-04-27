#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : encryptor.py
# Author        : bssthu
# Project       : pysqlsimplecipher
# Creation date : 2016-06-03
# Description   :
#


import hashlib
import hmac
from pysqlsimplecipher import config
from pysqlsimplecipher import util


def check_database_header(header):
    if not util.is_valid_database_header(header):
        raise RuntimeError('invalid database header.')

    page_sz = util.get_page_size_from_database_header(header)
    if not util.is_valid_page_size(page_sz):
        raise RuntimeError('invalid page size %d.' % page_sz)

    reserve_sz = util.get_reserved_size_from_database_header(header)
    if reserve_sz == 0:
        raise RuntimeError('needs reserved space at the end of each page.')

    return page_sz, reserve_sz


def encrypt_file(filename_in, password, filename_out):
    if not isinstance(filename_in, str):
        raise RuntimeError('filename_in must be a str.')
    if not isinstance(password, bytearray):
        raise RuntimeError('password must be a bytearray.')
    if not isinstance(filename_out, str):
        raise RuntimeError('filename_out must be a str.')

    # read
    with open(filename_in, 'rb') as fp:
        raw = fp.read()

    # check header
    page_sz, reserve_sz = check_database_header(raw[:100])

    # encrypt
    dec = encrypt_default(raw, password, page_sz, reserve_sz)

    # write
    with open(filename_out, 'wb') as fp:
        fp.write(dec)


def encrypt_default(raw, password, page_sz, reserve_sz):
    # configs
    salt_mask = config.salt_mask
    key_sz = config.key_sz
    key_iter = config.key_iter
    hmac_key_sz = config.hmac_key_sz
    hmac_key_iter = config.hmac_key_iter
    iv_sz = config.iv_sz
    hmac_sz = config.hmac_sz

    if reserve_sz < iv_sz + hmac_sz:
        raise RuntimeError('reserved space at the end of each page is %d, needs %d.' % (reserve_sz, iv_sz + hmac_sz))

    return encrypt(raw, password, salt_mask, key_sz, key_iter, hmac_key_sz, hmac_key_iter, page_sz, iv_sz, reserve_sz, hmac_sz)


def encrypt(raw, password, salt_mask, key_sz, key_iter, hmac_key_sz, hmac_key_iter, page_sz, iv_sz, reserve_sz, hmac_sz):
    salt_sz = 16
    salt = util.random_bytes(salt_sz)
    enc = salt

    # derive key
    key, hmac_key = util.key_derive(salt, password, salt_mask, key_sz, key_iter, hmac_key_sz, hmac_key_iter)

    # encrypt pages
    for i in range(0, int(len(raw) / 1024)):
        page = util.get_page(raw, page_sz, i + 1)
        if i == 0:
            # skip header string
            page = page[salt_sz:]
        page_content = page[:-reserve_sz]
        iv = util.random_bytes(iv_sz)
        # encrypt content
        page_enc = util.encrypt(page_content, key, iv)
        # generate hmac
        hmac_new = util.generate_hmac(hmac_key, page_enc + iv, i + 1)
        enc += page_enc + iv + hmac_new
        if reserve_sz > iv_sz + hmac_sz:
            enc += util.random_bytes(reserve_sz - iv_sz - hmac_sz)

    return enc

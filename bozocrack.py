#!/usr/bin/env python

from collections import defaultdict
import hashlib
import os
import re
import sys
import time
import urllib.request as request

from typing import List

class BozoCrack:

    MD5_HASH_PATTERN = r'\b([a-fA-F0-9]{32})\b'
    MD5_HASH_PASSWORD_PATTERN = r'^([a-fA-F0-9]{32}):(.*)$'
    MD5_HASH_PASSWORD_CACHE_FILENAME = 'bozocrack.cache'
    GOOGLE_URL = 'http://www.google.com/search?q={hash}'

    def __init__(self, filename: str) -> None:
        self.hashes = set()
        self.cache = defaultdict(str)

        if not os.path.exists(filename):
            print(f'{filename} does not exist!')
            sys.exit(1)

        with open(filename, 'r') as file:
            for line in file:
                if result := re.search(BozoCrack.MD5_HASH_PATTERN, line.rstrip('\n')):
                    self.hashes.add(result.group(1))

        print(f'Loaded {len(self.hashes)} unique hashes!')
        self.load_cache()

    def load_cache(self, filename: str = MD5_HASH_PASSWORD_CACHE_FILENAME):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                for line in file:
                    if result := re.search(BozoCrack.MD5_HASH_PASSWORD_PATTERN, line.strip('\n')):
                        self.cache[result.group(1)] = result.group(2)

        print(f'Found {len(self.hashes)} md5 to password entries in cache')

    def crack(self) -> None:
        for hash in self.hashes:
            if plaintext := self.cache[hash]:
                print(f'getting plaintext for {hash} directly from cache')
                print(f'{hash}:{plaintext}')
            else:
                if plaintext := self.crack_single(hash):
                    print(f'{hash}:{plaintext}')
                    self.append_to_cache(hash, plaintext)
                else:
                    print(f'unable to crack {hash} to plaintext password!')
            time.sleep(1)

    def append_to_cache(self, hash: str, plaintext: str, filename: str = MD5_HASH_PASSWORD_CACHE_FILENAME):
        with open(filename, 'a') as file:
            file.write(f'{hash}:{plaintext}\n')

    def crack_single(self, hash: str) -> None:
        url = BozoCrack.GOOGLE_URL.format(hash=hash)
        print(f'calling url: {url}')
        try:
            response = request.urlopen(url)
            response_content = response.read()
            wordlist = re.split(r'\s+', response_content.decode('latin-1'))
            if plaintext := self.dictionary_attach(hash, wordlist):
                return plaintext
            else:
                return None
        except Exception as e:
            print(f'exception occurred: {e}')

    def dictionary_attach(self, hash: str, wordlist: List[str]) -> None:
        for word in wordlist:
            if hashlib.md5(word.lower().encode()).hexdigest() == hash:
                return word
            

if __name__ == '__main__':

    if len(sys.argv) == 2:
        BozoCrack(sys.argv[1]).crack()
    else:
        print('Usage: python bozocrack.py file_with_md5_hashes.txt')
        sys.exit(1)
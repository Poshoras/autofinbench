"""Check that every gt/qNNN.json matches the SHA-256 commitment published before answers were collected."""
import hashlib, os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/..'
salt = open(f'{D}/gt/SALT.txt').read().strip()
com = dict(re.findall(r'\| (q\d+) \| \d+ \| `([0-9a-f]{64})`', open(f'{D}/gt_commitments.md').read()))
ok = all(hashlib.sha256(salt.encode() + open(f'{D}/gt/{q}.json', 'rb').read()).hexdigest() == h for q, h in com.items())
print(len(com), 'commitments', 'ALL MATCH' if ok else 'MISMATCH')

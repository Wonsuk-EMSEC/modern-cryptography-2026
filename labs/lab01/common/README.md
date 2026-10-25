# Lab 01 completion flags

Each Part provides an authenticated encrypted flag in `data/flag_challenge.json`.
Complete the experiment, construct its proof as specified in that Part's README,
and call the provided `unlock_flag(path, proof)` utility. It returns a `FLAG{...}`
string after authentication and raises `ValueError` for an incorrect proof or
invalid envelope. Do not edit the supplied flag artifact.

From a student exercise file in a numbered Part, add the repository root before
importing the shared utilities:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`canonical_account_proof(accounts)` returns compact JSON with account names
sorted lexicographically, no extra whitespace, and Unicode retained as text.
It requires a nonempty mapping of account strings to recovered password strings.
For the public mapping `{"b": "public-two", "a": "public-one"}`, it returns
`{"a":"public-one","b":"public-two"}`. The exact encoding is equivalent to:

```python
json.dumps(accounts, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

Inside any Part, run its `python3 samples/flag_unlock_demo.py` to observe rejection
of an incorrect public proof and success with the explicitly public demo proof.
The demo opens only `common/samples/public_flag_challenge.json`; it uses no
course account, SSH credential, captured-network passphrase, or Part flag.

Expected demo output:

```text
Wrong proof rejected: OK
FLAG{public_demo_only}
This public demo flag is not a Part completion flag.
```

The helper handles AES-256-GCM decryption and authentication. A domain-separated
SHA-256 derivation binds the UTF-8 proof to the envelope's Part identifier, and
the public challenge metadata is authenticated. Implement the actual experiment
yourself; this utility provides no candidate search or password recovery.

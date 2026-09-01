# Lab 01: Password Cracking and Hash Attacks

**Time:** 2–3 hours  
**Environment:** course Docker container  
**Scope:** controlled, offline experiments using only the supplied data

## Learning objectives

By the end of this lab you should be able to:

1. explain why an offline password verifier permits repeated guesses;
2. implement a dictionary attack against unsalted password hashes;
3. describe and experiment with a time–memory tradeoff;
4. explain why salts frustrate reuse of precomputed work;
5. demonstrate an MD5 collision and distinguish collision resistance from
   preimage resistance; and
6. explain, at a high level, how an already-recorded WPA2-Personal key
   confirmation can be checked against password guesses.

## Rules and setup

This lab is only about the files supplied in `data/`. Do not capture traffic,
interact with a wireless network, or test credentials that you do not own and
have explicit permission to audit.

From the repository root, enter the course environment:

```console
docker compose -f docker/compose.yml run --rm course bash
cd /workspace/labs/lab01
```

Use only Python's standard library and OpenSSL. Run the public checks with:

```console
python3 -m unittest discover -s tests -v
```

The starters deliberately contain `TODO` sections, so tests for unfinished
parts will fail until you implement them. Do not change function names or
signatures. Record commands, results, and answers to conceptual questions in
your lab report. Do not submit recovered passwords as part of a public post.

## Part 1 — Dictionary attack (30–40 minutes)

A password hash is a one-way verifier: software hashes a candidate and compares
the digest to a stored value. If an attacker obtains an unsalted hash database,
guesses can be checked offline without contacting the service. Speed and reuse
make fast general-purpose hashes such as SHA-256 unsuitable for password
storage; real systems should use a salted password-hashing/KDF construction.

Open `starter/dictionary_attack.py`. Implement:

- `load_dictionary(path)` to read candidates, ignoring blank lines; and
- `crack_hashes(targets, candidates, algorithm)` to return a mapping from each
  recovered lowercase hexadecimal digest to its candidate password.

Run:

```console
python3 starter/dictionary_attack.py data/passwords.txt data/sha256_targets.txt
python3 -m unittest tests.test_dictionary_attack -v
```

Questions:

1. How many hash computations are needed in the worst case for `D` dictionary
   words and `T` targets if each candidate is hashed only once?
2. Why can an attacker reuse this work across many accounts when hashes have no
   salts?
3. Name two properties a modern password-storage scheme should have beyond
   simply using a cryptographic hash.

## Part 2 — Rainbow-table-like precomputation (40–50 minutes)

A time–memory tradeoff stores chain endpoints rather than every
password/digest pair. A chain alternates a hash function `H` and a reduction
function `R_i` that maps a digest back into the password space:

```text
p0 -> H -> digest0 -> R0 -> p1 -> H -> digest1 -> R1 -> ... -> endpoint
```

This is a small teaching model, not a production rainbow-table format. Its toy
space is all three-character strings over `abcd` (only 64 passwords), so chain
merges and incomplete coverage are visible.

Implement the TODOs in `starter/rainbow_table.py`. The reduction must be
deterministic, depend on its column, and always return a password in the stated
space. Generate chains from the start points in `data/rainbow_config.json`,
store only start/end pairs, and implement lookup by reconstructing candidate
chains. Your program must not silently replace the endpoint table with a full
digest-to-password dictionary.

Use `data/rainbow_targets.txt` for the unsalted experiment. Then compare it with
`data/salted_targets.json`: the latter hashes `salt || password`, with a unique
public salt represented as hexadecimal. Explain why a table built for
`SHA-256(password)` does not directly answer these salted targets and what an
attacker would have to recompute. The supplied chains intentionally do not cover
the entire toy space, so a correct lookup may report `not found` for a target.

```console
python3 starter/rainbow_table.py data/rainbow_config.json data/rainbow_targets.txt
python3 -m unittest tests.test_rainbow_table -v
```

Questions:

1. What is saved in memory, and what extra work is done during lookup?
2. Measure coverage by enumerating the toy space. Why might chains merge?
3. Does a salt need to be secret? Explain precisely what benefit it provides.

## Part 3 — MD5 collision (20–25 minutes)

The two supplied 128-byte files are different messages from the classic Wang
and Yu MD5 collision demonstration. Do not execute them; they are data blocks.

```console
cmp -l data/md5_collision_a.bin data/md5_collision_b.bin
openssl dgst -md5 data/md5_collision_a.bin data/md5_collision_b.bin
openssl dgst -sha256 data/md5_collision_a.bin data/md5_collision_b.bin
```

Include evidence that the files differ, that their MD5 digests match, and that
their SHA-256 digests do not.

Collision resistance asks whether it is feasible to find *any* two distinct
messages with the same digest. Preimage resistance asks, given a particular
digest, whether it is feasible to find a message producing it. An MD5 collision
demonstrates failure of the former; it does not by itself demonstrate an
arbitrary preimage attack.

Questions:

1. Which security property does the sample pair directly disprove?
2. Why is this not the same as recovering a password from a chosen MD5 digest?
3. Give one security application that becomes unsafe when collision resistance
   fails.

Source and attribution: the collision blocks are the published example in
Peter Selinger's “MD5 Collision Demo,” based on work by Xiaoyun Wang and Hongbo
Yu: <https://www.mscs.dal.ca/~selinger/md5collision/>.

## Part 4 — WPA2 offline password guessing (40–50 minutes)

`data/wpa2_capture.json` is a synthetic, intentionally generated teaching
record—not a packet capture. It contains an SSID, two MAC addresses, two nonces,
an EAPOL-like byte string with a zeroed MIC field, and a reference MIC. These
are enough to illustrate password checking without a radio or a real network.

For each candidate in `data/wpa2_passwords.txt`, complete
`starter/wpa2_offline.py` to:

1. derive the 32-byte pairwise master key using
   `PBKDF2-HMAC-SHA1(password, SSID, 4096)`;
2. derive 64 bytes of key material with the supplied WPA2 PRF using the ordered
   MAC addresses and nonces;
3. use the first 16 bytes as the key confirmation key;
4. compute `HMAC-SHA1(KCK, eapol_bytes)` and compare its first 16 bytes to the
   supplied MIC with `hmac.compare_digest`.

The provided record fixes the byte ordering and MIC-zeroing details so the
exercise focuses on dictionary checking rather than packet parsing.

```console
python3 starter/wpa2_offline.py data/wpa2_capture.json data/wpa2_passwords.txt
python3 -m unittest tests.test_wpa2_offline -v
```

Questions:

1. Which values in the record let a guess be checked without the access point?
2. Why does a weak passphrase remain vulnerable even though PBKDF2 performs
   4096 iterations?
3. State the ethical and authorization boundary for this experiment.

## Submission checklist

- completed copies of the four starter programs;
- test output and the requested MD5/OpenSSL evidence;
- answers to all conceptual questions; and
- a brief comparison of unsalted SHA-256, salted password storage, and this
  controlled WPA2 password-verification model.

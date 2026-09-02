# Part 2: Dictionary attacks

**Ethical and authorized use:** run these scripts only against the fictional
accounts and local files supplied with this lab. Do not use leaked wordlists,
real credentials, or external services.

The CSV schemas are `account,sha256` and `account,salt_hex,sha256`. Complete
both starters, then run `python3 compare_cost.py`. Report recovered synthetic
accounts, computation counts, elapsed time, and guesses per second.

## Inspect the local inputs

```console
cd /workspace/labs/lab01/part2_dictionary_attack
head ../data/lab01-small.txt
sed -n '1,5p' ../data/unsalted_hashes.csv
sed -n '1,5p' ../data/salted_hashes.csv
```

The wordlist contains only fictional classroom candidates. In the salted CSV,
decode `salt_hex` with `bytes.fromhex(...)` before concatenating it with the
UTF-8 candidate bytes.

## Implement and run the attacks

Both attack files are student starters. Before implementation, the following
commands intentionally stop at `NotImplementedError`:

```console
python3 crack_unsalted.py ../data/unsalted_hashes.csv ../data/lab01-small.txt
python3 crack_salted.py ../data/salted_hashes.csv ../data/lab01-small.txt
```

After completing `crack()`, each command should print a tuple with this shape:

```text
({'fictional_account': 'recovered_candidate'}, HASH_COUNT, ELAPSED_SECONDS)
```

Do not hard-code account names, candidates, counts, or digests. For the
unsalted attack, hash each candidate once and compare it with every target. For
the salted attack, compute a separate digest for each candidate/account salt
pair.

Then compare the two experiments:

```console
python3 compare_cost.py ../data
```

Expected output format (numbers depend on your implementation and machine):

```text
experiment   found   hashes    seconds     hashes/s
unsalted         N        N   0.000000            N
salted           N        N   0.000000            N
```

## Checkpoint questions

1. Why can one unsalted candidate digest serve all accounts?
2. Why must salted records be checked separately?
3. Which computation count grows faster as the number of accounts increases?
4. Why does salt prevent shared precomputation without making a weak password
   strong?

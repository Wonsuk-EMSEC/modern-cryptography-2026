# Part 2: Controlled online SSH dictionary attack

**Estimated time:** 25 minutes. Use only the fixed
`labstudent@lab01-ssh-target:22` service and supplied 107-entry course wordlist.
Keep attempts sequential, bounded to 120 candidates, with a delay after
failures. Do not add arbitrary target, account, port, external wordlist, or
concurrency options.

This is an online experiment: each guess reaches a server that can log,
delay, or block it. Part 3 contrasts this with local offline verification.

## Learning objectives and files

Implement password-only SSH authentication, close resources in every outcome,
measure bounded sequential attempts, and interpret server-side observations.

| File | Role |
| --- | --- |
| `samples/ssh_api_demo.py` | Complete offline Paramiko, CLI, cleanup, and timing example |
| `ssh_dictionary_attack.py` | Empty student exercise file |
| `data/ssh-lab-wordlist.txt` | Fixed 107-entry fictional wordlist |
| `test_ssh_dictionary_attack.py` | Fixture checks and opt-in implementation checks |
| `samples/flag_unlock_demo.py` | Public helper-usage example; no Part answer |
| `data/flag_challenge.json` | Encrypted completion flag, opened by the experiment result |

Write the whole program, including imports, constants, functions, CLI, and
execution guard. Importing the file must not make network requests.

## 1. Run and inspect the sample

Enter the course container using the repository's Docker instructions, then run:

```console
cd /workspace/labs/lab01/part2_dictionary_attack
python3 samples/ssh_api_demo.py
python3 -m unittest test_ssh_dictionary_attack.py -v
```

The sample prints:

```text
Nonempty lines: 2
Client class: SSHClient
Transport before connect: None
Authentication error type: AuthenticationException
Client closed; no network request sent
Elapsed: <seconds> seconds
```

It needs no SSH target because it never calls `connect()`. Inspect how
`argparse`, optional text input, `perf_counter()`, and `try/finally` fit
together. The optional `--notes` argument counts nonempty lines in a local text
file. Timing varies; the other shown values are fixed. No file is generated.

Before implementation, the fixture test passes and two implementation checks
are skipped. The baseline does not authenticate or reveal a matching candidate.

### Public flag utility sample

```console
python3 samples/flag_unlock_demo.py
```

Expected output:

```text
Wrong proof rejected: OK
FLAG{public_demo_only}
This public demo flag is not a Part completion flag.
```

The sample leaves no file behind. Inspect how the shared utility is imported,
how authentication failure is handled, and how a successful return value is
printed. Your final program will use its own experiment result, not this public
demo proof.

## 2. Write constants and load_candidates(), then check them

In `ssh_dictionary_attack.py`, define these exercise constants:

```text
TARGET_HOST = "lab01-ssh-target"
TARGET_PORT = 22
TARGET_USERNAME = "labstudent"
MAX_CANDIDATES = 120
```

Implement `load_candidates(path: Path) -> list[str]`: read UTF-8 lines,
strip surrounding whitespace, skip blank lines, preserve order, and raise
`ValueError` if more than 120 candidates remain. Use only the supplied wordlist
in the final CLI exercise.

Run this small check before writing network code:

```console
python3 - <<'PY'
import tempfile
from pathlib import Path
from ssh_dictionary_attack import load_candidates
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "public.txt"
    path.write_text(" public-a \n\npublic-b\n", encoding="utf-8")
    assert load_candidates(path) == ["public-a", "public-b"]
    path.write_text("public\n" * 121, encoding="utf-8")
    try:
        load_candidates(path)
    except ValueError:
        pass
    else:
        raise AssertionError("over-limit list was accepted")
print("Bounded input check: OK")
PY
```

Proceed after `Bounded input check: OK`.

## 3. Write try_candidate(), then check it without a server

Implement `try_candidate(candidate: str) -> bool` using `paramiko`:

1. Create one `SSHClient`; set `AutoAddPolicy` only for this disposable target.
2. Call `connect()` with the fixed host, port, username, and candidate password.
   Set `allow_agent=False` and `look_for_keys=False` so other credentials are
   never tried; set bounded connection, banner, and authentication timeouts.
3. Return `True` after successful authentication and `False` for
   `paramiko.AuthenticationException`.
4. Always call `close()` in `finally`. Other connection errors should surface
   so a stopped target is not confused with an incorrect password.

The following mocks the client; it sends no network traffic:

```console
python3 - <<'PY'
from unittest.mock import Mock, patch
import paramiko
import ssh_dictionary_attack as attack
for failure in (False, True):
    client = Mock()
    if failure:
        client.connect.side_effect = paramiko.AuthenticationException()
    with patch.object(attack.paramiko, "SSHClient", return_value=client):
        assert attack.try_candidate("public-fixture") is (not failure)
    client.close.assert_called_once()
    args, kwargs = client.connect.call_args
    host = kwargs.get("hostname", args[0] if args else None)
    assert host == "lab01-ssh-target"
    assert kwargs["port"] == 22 and kwargs["username"] == "labstudent"
    assert kwargs["password"] == "public-fixture"
    assert kwargs["allow_agent"] is False and kwargs["look_for_keys"] is False
print("One-attempt check: OK")
PY
```

Proceed after `One-attempt check: OK`.

## 4. Write dictionary_attack(), then check its stopping rule

Implement
`dictionary_attack(candidates: list[str], delay: float = 0.25) -> tuple[str | None, int, float]`.
Reject oversized input, try each candidate sequentially through
`try_candidate()`, and count every attempt including a successful one.
Sleep after failures, stop at the first success, and return
`(candidate_or_None, attempts, elapsed_seconds)`. Measure elapsed time with
`time.perf_counter()`. Never print candidates.

```console
python3 - <<'PY'
from unittest.mock import patch
import ssh_dictionary_attack as attack
with patch.object(attack, "try_candidate", side_effect=[False, True]) as attempt:
    found, count, elapsed = attack.dictionary_attack(["public-a", "public-b", "public-c"], delay=0)
    assert found == "public-b" and count == 2 and elapsed >= 0
    assert attempt.call_count == 2
with patch.object(attack, "try_candidate", return_value=False):
    found, count, elapsed = attack.dictionary_attack(["public-a"], delay=0)
    assert found is None and count == 1 and elapsed >= 0
print("Sequential search check: OK")
PY
```

Proceed after `Sequential search check: OK`.

<a id="step-1-build-and-start-the-isolated-target"></a>

## 5. Write the CLI, then start the isolated target

Write `main()` to accept the supplied local wordlist path, load candidates,
call the attack, and print only the fixed target, attempts, elapsed seconds,
and success status. Keep the default failure delay at 0.25 seconds. Add a
`__main__` guard. Run the opt-in checks:

```console
LAB01_GRADE=1 python3 -m unittest test_ssh_dictionary_attack.py -v
```

All three tests should pass. They cover the input and fixed target;
the mocked checks above cover behavior.

Now run the following from the repository root in a **host terminal**:

```console
docker compose -f docker/compose.yml --profile lab01-ssh build
docker compose -f docker/compose.yml --profile lab01-ssh up -d lab01-ssh-target
docker compose -f docker/compose.yml --profile lab01-ssh ps
```

Wait for `healthy`. The internal Compose network has no published SSH port.
Enter a course container on that network:

```console
docker compose -f docker/compose.yml --profile lab01-ssh run --rm course bash
cd /workspace/labs/lab01/part2_dictionary_attack
```

### Shared completion utility

The whole main program is still yours to write. Resolve the envelope relative
to your exercise file, rather than the shell's current directory. To import
the provided shared utility from a numbered Part exercise file, use:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`unlock_flag(path, proof)` returns a `FLAG{...}` string after authenticating
the encrypted envelope. An incorrect proof raises `ValueError`; inspect your
implementation and proof format rather than changing the envelope.
The public demo proof opens only the demo artifact and cannot open this Part's
flag. Submit the computed Part flag through the instructor's designated channel.

### Open the flag after successful authentication

If `dictionary_attack()` returns a matching candidate, use that exact
returned string as the proof for `data/flag_challenge.json`. Call the
provided `unlock_flag(flag_path, match)` and print its returned `FLAG{...}`
as the final line after the status metrics. Keep the candidate itself private.
If no candidate matches, report failure and do not attempt to open the flag.

This flag envelope is local; the SSH target needs no flag file and no new
service endpoint. You must first recover a candidate from the fixed service.

## 6. Run the full exercise and inspect the evidence

```console
python3 ssh_dictionary_attack.py data/ssh-lab-wordlist.txt
```

Output should have this shape:

```text
Target: labstudent@lab01-ssh-target:22
Attempts: <count>
Elapsed: <seconds> seconds
Result: candidate found
FLAG{...}
```

Expect tens of seconds depending on SSH overhead and the host. The count is
between 1 and 107. The matching candidate must not appear in the output or
report. A connection error means the target/network needs checking.

In a second host terminal, inspect this target's logs:

```console
docker compose -f docker/compose.yml --profile lab01-ssh logs --tail 50 lab01-ssh-target
```

Record failed-login observations without candidate values. Exit the course
shell and remove the disposable target from the host:

```console
exit
docker compose -f docker/compose.yml --profile lab01-ssh rm --stop --force lab01-ssh-target
```

## 7. Completion and report

- [ ] All three small checks and all enabled tests pass.
- [ ] The complete program preserves the fixed destination and bounded input.
- [ ] The supplied exercise reports success without printing the candidate.
- [ ] Attempt count, elapsed time, and redacted server observations are recorded.
- [ ] The temporary target is removed.
- [ ] The final program authenticates its own `data/flag_challenge.json` and prints the Part flag.

Submit your Python file and these observations. Explain why this is online,
what the server can observe, how rate limiting changes online cost, why every
resource is closed, and why `AutoAddPolicy` is limited to this disposable
classroom service. Contrast this with offline CSV verification in Part 3.

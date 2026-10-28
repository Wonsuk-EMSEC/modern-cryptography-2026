"""Public feedback, with fresh random tests and a measured relative threshold.

Completion receipts are public, nonsecret feedback, not instructor grading flags.
Run submitted code only in the isolated course/grading environment.
"""
import argparse
import ast
import importlib.util
import inspect
import json
import math
import random
import signal
import statistics
import sys
import textwrap
import time
from pathlib import Path

PART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART / 'starter'))
from prime64 import is_prime64


def load(path):
    spec = importlib.util.spec_from_file_location('student_math', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def instrument(fn, primality=False):
    tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    for node in ast.walk(tree):
        if not primality and isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            raise AssertionError('exponentiation operator is forbidden in modexp')
        if isinstance(node, ast.Call):
            allowed_name = isinstance(node.func, ast.Name) and node.func.id in {
                'bin', 'range', 'len', 'int', 'ValueError', 'enumerate', 'reversed', 'abs',
                'format', 'str', 'list', 'tuple'}
            allowed_name = allowed_name or (primality and isinstance(node.func,ast.Name) and node.func.id=='isqrt')
            allowed_sqrt = primality and isinstance(node.func, ast.Attribute) and node.func.attr == 'isqrt' and (
                isinstance(node.func.value, ast.Name) and node.func.value.id == 'math')
            allowed_bits=isinstance(node.func,ast.Attribute) and node.func.attr in {'bit_length','bit_count'}
            if not allowed_name and not allowed_sqrt and not allowed_bits:
                raise AssertionError('implement arithmetic directly; forbidden helper call')
    counts = {'mul': 0, 'mod': []}

    def mul(a, b):
        counts['mul'] += 1
        return a*b

    def mod(a, b):
        result = a % b
        counts['mod'].append(result)
        return result

    class Transform(ast.NodeTransformer):
        def visit_BinOp(self, node):
            self.generic_visit(node)
            if isinstance(node.op, (ast.Mult, ast.Mod)):
                name = '_checked_mul' if isinstance(node.op, ast.Mult) else '_checked_mod'
                return ast.copy_location(ast.Call(ast.Name(name, ast.Load()), [node.left, node.right], []), node)
            return node

        def visit_AugAssign(self,node):
            self.generic_visit(node)
            if isinstance(node.target,ast.Name) and isinstance(node.op,(ast.Mult,ast.Mod)):
                name = '_checked_mul' if isinstance(node.op,ast.Mult) else '_checked_mod'
                operation=ast.Call(ast.Name(name,ast.Load()),[ast.Name(node.target.id,ast.Load()),node.value],[])
                return ast.copy_location(ast.Assign([node.target],operation),node)
            return node

    tree = ast.fix_missing_locations(Transform().visit(tree))
    namespace = dict(fn.__globals__, _checked_mul=mul, _checked_mod=mod)
    exec(compile(tree, '<instrumented modexp>', 'exec'), namespace)
    return namespace[fn.__name__], counts


def median_call(fn, arguments, repeats=5):
    fn(*arguments)  # warm-up is outside measurement
    durations = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        result = fn(*arguments)
        durations.append(time.perf_counter_ns()-start)
        assert result == pow(*arguments)
    return statistics.median(durations)


def naive_reference(base, exponent, modulus):
    result = 1 % modulus
    for _ in range(exponent):
        result = result*base % modulus
    return result


def grade(solution_path, data_path=None, fresh=False):
    m = load(solution_path)
    data = json.loads(Path(data_path or PART/'data/challenge.json').read_text())
    rng = random.SystemRandom()
    for args in [(0, 0, 1), (0, 0, 19), (0, 17, 19), (-5, 17, 101), (8, 0, 13)]:
        assert m.modular_exponentiation(*args) == pow(*args)
    for _ in range(100):
        args = (rng.randrange(-2**256, 2**256), rng.getrandbits(rng.randrange(1, 512)), rng.randrange(1, 2**256))
        assert m.modular_exponentiation(*args) == pow(*args)
    for args in [(2, -1, 7), (2, 3, 0), (2, 3, -7)]:
        try:
            m.modular_exponentiation(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid modexp parameters must raise ValueError')
    counted, counts = instrument(m.modular_exponentiation)
    for bits in (17, 61, 127, 257):
        exponent = rng.getrandbits(bits) | 1 << (bits-1)
        base, modulus = rng.randrange(2, 1000), 1009
        counts.update(mul=0, mod=[])
        assert counted(base, exponent, modulus) == pow(base, exponent, modulus)
        expected, result = [], 1
        for bit in bin(exponent)[2:]:
            result = result*result % modulus
            expected.append(result)
            if bit == '1':
                result = result*base % modulus
                expected.append(result)
        assert counts['mod'][-len(expected):] == expected, 'must process MSB first and reduce every product'
        assert counts['mul'] == bits + exponent.bit_count(), 'incorrect square/multiply count'
    counted_naive, counts_naive = instrument(m.naive_modular_exponentiation)
    for e in (0, 1, 31, 97):
        counts_naive.update(mul=0, mod=[])
        assert counted_naive(17, e, 1009) == pow(17, e, 1009)
        assert counts_naive['mul'] == e
    for n in list(range(-3, 300)) + [561, 1105, 1729, 65537, 65539**2]:
        assert bool(m.is_prime_exact(n)) == (is_prime64(n) if n >= 0 else False)
    exact_counted,division_counts=instrument(m.is_prime_exact,primality=True)
    for prime in (65537,2147483647):
        division_counts.update(mul=0,mod=[])
        assert exact_counted(prime) is True
        assert 1 <= len(division_counts['mod']) <= math.isqrt(prime)+2, 'trial division must stop at the square-root bound'
    prime_report = []
    for group in data['prime_sets']:
        for n in group['values']:
            expected = is_prime64(n)
            assert bool(m.is_prime_exact(n)) == expected
            fermat = m.fermat_test(n, 2)
            assert fermat == (math.gcd(n, 2) == 1 and pow(2, n-1, n) == 1)
            durations = []
            for fn in (m.is_prime_exact, lambda x: m.fermat_test(x,2)):
                fn(n)
                measurements = []
                for _ in range(7):
                    start = time.perf_counter_ns()
                    fn(n)
                    measurements.append(time.perf_counter_ns()-start)
                durations.append(statistics.median(measurements))
            exact_ns,fermat_ns = durations
            prime_report.append({'bits': n.bit_length(), 'n': n, 'exact_ns': exact_ns, 'fermat_ns': fermat_ns})
    # Independently varied small inputs, not only the public benchmark numbers.
    for _ in range(60):
        n, base = rng.randrange(2, 2**22), rng.randrange(1, 200)
        assert bool(m.is_prime_exact(n)) == is_prime64(n)
        assert bool(m.fermat_test(n, base)) == (math.gcd(n, base) == 1 and pow(base, n-1, n) == 1)
    for n,base in [(-5,2),(0,2),(1,2),(2,0),(2,1),(2,2),(2,3)]:
        assert bool(m.fermat_test(n,base)) == (n>=2 and math.gcd(n,base)==1 and pow(base,n-1,n)==1)
    original = m.modular_exponentiation
    called = []
    def observed(*args):
        called.append(args)
        return original(*args)
    m.modular_exponentiation = observed
    assert m.fermat_test(65537, 3)
    m.modular_exponentiation = original
    assert called, 'Fermat test must use the submitted modular exponentiation'
    assert not m.is_prime_exact(561) and m.fermat_test(561, 2), 'must distinguish probable prime from prime'
    windows = data.get('search_windows', [[data['t_min'],data['t_max']]])
    candidates,proofs = [],[]
    for lower,upper in windows:
        candidate = m.generate_pseudoprime(lower,upper)
        t, factors, n = candidate['t'], candidate['factors'], candidate['n']
        assert type(t) is int and lower <= t <= upper
        assert factors == [6*t+1, 12*t+1, 18*t+1]
        assert all(is_prime64(p) for p in factors) and len(set(factors)) == 3
        assert n == math.prod(factors) and n.bit_length() == 128 and pow(2, n-1, n) == 1
        candidates.append(n)
        proofs.append(candidate)
    assert len(set(candidates)) == len(windows), 'search must follow the supplied interval'
    try:
        m.generate_pseudoprime(0,0)
    except ValueError:
        pass
    else:
        raise AssertionError('an empty search must report failure')
    bench = []
    for exponent in (75001, 125003, 200003):
        args = (rng.getrandbits(256), exponent, (1 << 257)-93)
        slow = median_call(naive_reference, args, 3)
        fast = median_call(original, args)
        builtin = median_call(pow, args)
        # Calibrate from this runtime's baseline/reference gap. No fixed ms limit.
        required = min(10.0, max(2.0, slow/builtin/20))
        assert slow/fast >= required, 'insufficient relative speedup'
        bench.append({'exponent': exponent, 'naive_mul': exponent,
                      'square_multiply_mul': exponent.bit_length()+exponent.bit_count(),
                      'naive_ns': slow, 'square_multiply_ns': fast, 'pow_ns': builtin,
                      'speedup': round(slow/fast, 2), 'required_speedup': required})
    return {'status': 'PASS', 'receipt': 'LAB03{part01_local_checks_passed}',
            'performance': bench, 'primality': prime_report, 'candidate_bits': n.bit_length(),
            'proof':proofs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--solution', type=Path, default=PART/'starter/math_challenges.py')
    ap.add_argument('--data', type=Path)
    ap.add_argument('--fresh', action='store_true')
    args = ap.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('30-second budget exceeded')))
    signal.alarm(30)
    try:
        print(json.dumps(grade(args.solution, args.data, args.fresh), indent=2))
    except (Exception,SystemExit) as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    finally:
        signal.alarm(0)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

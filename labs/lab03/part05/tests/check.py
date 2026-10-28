"""Public exact-root feedback. Successful plaintext contains the instance flag."""
import argparse
import hashlib
import json
import random
import signal
import subprocess
import sys
from pathlib import Path

PART = Path(__file__).resolve().parents[1]


def grade(solution_path,data_path=None,fresh=False):
    data=json.loads(Path(data_path or PART/'data/challenge.json').read_text())
    rng=random.SystemRandom()
    root_inputs=list(range(150))+[rng.getrandbits(b) for b in (65,128,255,512,1024,2048) for _ in range(4)]
    for bits in (32,128,256,700):
        root=rng.getrandbits(bits) | 1 << (bits-1)
        root_inputs.extend(root**3+delta for delta in (-1,0,1))
    recovery_inputs=[data['positive'],data['negative']]
    recovery_expected=[]
    for _ in range(20):
        value=rng.getrandbits(128)
        modulus=1 << 1024 | rng.getrandbits(1023) | 1
        recovery_inputs.extend([{'n':str(modulus),'e':'3','c':str(value**3)},
                                {'n':str(modulus),'e':'3','c':str(value**3+2)}])
        recovery_expected.extend([value,None])
    recovery_inputs.extend([{'n':'101','e':'2','c':'8'}, {'n':'101','e':'3','c':'-1'},
                            {'n':'101','e':'3','c':'101'}])
    recovery_expected.extend([None,None,None])
    worker="""import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('student_cube',sys.argv[1])
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
queries=json.load(sys.stdin)
roots=[m.integer_cube_root(n) for n in queries['roots']]
recoveries=[m.recover(c) for c in queries['recoveries']]
negative_error=False
try:
    m.integer_cube_root(-1)
except ValueError:
    negative_error=True
print(json.dumps({'roots':roots,'recoveries':recoveries,'negative_error':negative_error}))
"""
    proc=subprocess.run([sys.executable,'-c',worker,str(Path(solution_path).resolve())],
                        input=json.dumps({'roots':root_inputs,'recoveries':recovery_inputs}),
                        capture_output=True,text=True,timeout=8)
    assert proc.returncode==0, 'submission failed: '+(proc.stderr.strip().splitlines() or ['no diagnostic'])[-1]
    answers=json.loads(proc.stdout)
    assert len(answers['roots'])==len(root_inputs)
    assert len(answers['recoveries'])==len(recovery_inputs)
    assert answers['negative_error'] is True
    for n,(root,exact) in zip(root_inputs,answers['roots']):
        assert type(root) is int and type(exact) is bool
        assert root**3 <= n < (root+1)**3
        assert exact == (root**3 == n)
    m=answers['recoveries'][0]
    assert type(m) is int
    n,e,c=(int(data['positive'][k]) for k in ('n','e','c'))
    assert m**3 == c and m**3 < n and pow(m,e,n) == c
    message=m.to_bytes((m.bit_length()+7)//8,'big')
    assert hashlib.sha256(message).hexdigest() == data['message_sha256']
    assert answers['recoveries'][1] is None, 'negative case must be rejected'
    assert answers['recoveries'][2:]==recovery_expected
    return {'status':'PASS','receipt':'LAB03{part05_local_checks_passed}',
            'proof':{'m':m,'negative_rejected':True}}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--solution',type=Path,default=PART/'starter/recover.py')
    ap.add_argument('--data',type=Path)
    args=ap.parse_args()
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('10-second budget exceeded')))
    signal.alarm(10)
    try:
        print(json.dumps(grade(args.solution,args.data)))
    except (Exception,SystemExit) as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}',file=sys.stderr)
        return 1
    finally:
        signal.alarm(0)
    return 0


if __name__=='__main__':
    raise SystemExit(main())

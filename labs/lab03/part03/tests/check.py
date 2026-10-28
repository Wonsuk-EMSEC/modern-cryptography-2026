"""Compile submitted callbacks against the trusted randomized C driver."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PART=Path(__file__).resolve().parents[1]


def fresh_primes(path,bits):
    from cryptography.hazmat.primitives.asymmetric import rsa
    numbers=rsa.generate_private_key(public_exponent=65537,key_size=bits).private_numbers()
    path.write_text(f'{numbers.p:X}\n{numbers.q:X}\n')


def grade(solution_path,data_path=None,fresh=False):
    solution_path=Path(solution_path).resolve()
    results=[]
    with tempfile.TemporaryDirectory(prefix='lab03-rsa-') as directory:
        tmp=Path(directory)
        binary=tmp/'rsa-check'
        command=[os.environ.get('CC','gcc'),'-std=c11','-O2','-Wall','-Wextra','-Werror',
                 '-I',str(PART/'starter'),str(solution_path),str(PART/'starter/rsa_io.c'),
                 str(PART/'tests/driver.c'),'-Wl,--wrap=BN_mod_exp','-lcrypto','-o',str(binary)]
        build=subprocess.run(command,capture_output=True,text=True,timeout=20)
        if build.returncode:
            raise AssertionError('compilation failed:\n'+build.stderr)
        for bits in (2048,3072):
            fixture=Path(data_path or PART/'data')/f'primes{bits}.txt'
            if fresh:
                fixture=tmp/f'primes{bits}.txt'
                fresh_primes(fixture,bits)
            proc=subprocess.run([str(binary),str(fixture)],capture_output=True,text=True,timeout=45)
            if proc.returncode:
                raise AssertionError(f'{bits}-bit check failed:\n'+proc.stderr)
            report=json.loads(proc.stdout)
            assert abs(report['bits']-bits)<=1 and report['speedup']>=report['required_speedup']-0.002
            results.append(report)
    return {'status':'PASS','receipt':'LAB03{part03_local_checks_passed}','performance':results}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--solution',type=Path,default=PART/'starter/rsa_engine.c')
    ap.add_argument('--data',type=Path,help='directory containing primes2048.txt and primes3072.txt')
    ap.add_argument('--fresh',action='store_true',help='generate independent primes before timing')
    args=ap.parse_args()
    try:
        print(json.dumps(grade(args.solution,args.data,args.fresh),indent=2))
    except (Exception,SystemExit) as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}',file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())

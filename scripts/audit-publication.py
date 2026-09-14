#!/usr/bin/env python3
"""Audit the staged Git tree (default) or all files of a source export (--all).
Reports paths and rule names only, never matching secret contents.
"""
from pathlib import Path
import argparse, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SECRET_RULES=[
 ('private key',re.compile(rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----')),
 ('GitHub token',re.compile(rb'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})')),
 ('Google API key',re.compile(rb'AIza[0-9A-Za-z_-]{35}')),
 ('signing password',re.compile(rb'(?:storePassword|keyPassword)\s*[=:]?\s*[\"\x27][^\"\x27\r\n]+[\"\x27]')),
]
def forbidden(name):
 p=Path(name); parts=[x.lower() for x in p.parts]
 if any(x in {'build','.gradle','save','sdk','ndk','__pycache__'} or x.startswith('device-backup') for x in parts):return 'private/generated directory'
 if p.name.lower() in {'local.properties','paniclog','record','perm','config.log','config.status','nhdat'}:return 'local/generated file'
 if p.suffix.lower() in {'.apk','.aab','.so','.o','.class','.jks','.keystore','.p12','.pfx','.pem','.key','.pk8','.sav','.save'} or '.recovered' in p.name or re.fullmatch(r'\d+[^/]*\.\d+',p.name):return 'binary/private state'
 return None

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 if args.self_test:
  assert forbidden('device-backup-20260913/10220Test.0')
  assert forbidden('sys/android/app/libs/arm64-v8a/libunnethack.so')
  assert forbidden('keys/release.jks')
  assert not forbidden('src/save.c')
  assert not forbidden('sys/android/gradle/wrapper/gradle-wrapper.jar')
  token=b'ghp_'+b'A'*36
  assert any(rule.search(token) for _,rule in SECRET_RULES)
  print('PASS: private paths, native output and token detection; source/wrapper retained.');return
 if args.all:
  entries=[(p.relative_to(ROOT).as_posix(),p.read_bytes()) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts]
 else:
  result=subprocess.run(['git','-C',str(ROOT),'ls-files','--stage','-z'],check=True,stdout=subprocess.PIPE)
  entries=[]
  for raw in result.stdout.split(b'\0'):
   if not raw:continue
   meta,name=raw.split(b'\t',1);mode,oid,stage=meta.split()
   if mode in (b'120000',b'160000') or stage!=b'0':raise SystemExit('Review symbolic links, submodules or conflicts before exporting.')
   entries.append((name.decode(),subprocess.check_output(['git','-C',str(ROOT),'cat-file','blob',oid.decode()])))
 if not entries:raise SystemExit('No files inspected; stage the source or pass --all.')
 failures=[]
 for name,data in entries:
  reason=forbidden(name)
  if reason:failures.append((name,reason))
  if b'\0' not in data:
   for label,rule in SECRET_RULES:
    if rule.search(data):failures.append((name,label))
   if re.search(rb'(?:[A-Za-z]:[/\\]Users[/\\]|/c/[U]sers/|/mnt/c/[U]sers/)',data):failures.append((name,'absolute personal Windows path'))
 for name,reason in failures:print(f'{name}: {reason}',file=sys.stderr)
 if failures:raise SystemExit(1)
 print(f'PASS: {len(entries)} files inspected. Heuristic scan, not proof of absence of all secrets.')
if __name__=='__main__':main()

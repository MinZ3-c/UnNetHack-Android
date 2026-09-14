"""Compare native callback descriptors with the compiled ForkFront class.

Usage: python check-jni.py <javap -s -private output>
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parent
source = (root / 'sys/android/winandroid.c').read_text()
compiled = Path(sys.argv[1]).read_text(encoding='utf-8-sig')
methods = dict(re.findall(r'\b(\w+)\([^;\n]*\);\s+descriptor: (\S+)', compiled))
callbacks = re.findall(r'GetMethodID\(jEnv, jApp, "([^"]+)", "([^"]+)"\)', source)
failures = []
for name, descriptor in callbacks:
    if methods.get(name) != descriptor:
        failures.append(f'{name}: C expects {descriptor}, Java has {methods.get(name)}')
if methods.get('RunNetHack') != '(Ljava/lang/String;)V':
    failures.append('Native entry point RunNetHack must receive one String.')
if failures:
    raise SystemExit('\n'.join(failures))
print(f'PASS: all {len(callbacks)} JNI callbacks and the native entry point match compiled Java descriptors.')

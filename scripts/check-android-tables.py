#!/usr/bin/env python3
"""Check generated IDs against host and Android object/monster tables.

Added 2026-09-14. NetHack may be freely redistributed; see LICENSE.
Runs on Linux/WSL with gcc; temporary files stay in the external build tree.
"""
import argparse
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('build_root', type=Path)
args = parser.parse_args()
build = args.build_root.resolve()
probe = build / 'table-check.c'
probe.write_text(r'''
#include "objects.c"
#include "monst.c"
#include "onames.h"
#include "pm.h"
#include <stdio.h>
#include <string.h>
_Static_assert(sizeof(objects) / sizeof(objects[0]) == NUM_OBJECTS + 1,
               "generated object count does not match compiled objects");
_Static_assert(sizeof(mons) / sizeof(mons[0]) == NUMMONS + 1,
               "generated monster count does not match compiled monsters");
int main(void) {
    int i;
    if (strcmp(obj_descr[GOLD_PIECE].oc_name, "gold piece")) {
        fprintf(stderr, "GOLD_PIECE resolves to %s\n", obj_descr[GOLD_PIECE].oc_name);
        return 1;
    }
    for (i = 0; i < NUM_OBJECTS; ++i)
        printf("object %d %d %s / %s\n", i, objects[i].oc_class,
               obj_descr[i].oc_name ? obj_descr[i].oc_name : "",
               obj_descr[i].oc_descr ? obj_descr[i].oc_descr : "");
    for (i = 0; i < NUMMONS; ++i)
        printf("monster %d %s\n", i, mons[i].mname);
    return 0;
}
''')
results = []
for name, define in [('host', 'ANDROID_HOST_TOOLS'), ('target', 'ANDROID')]:
    source = build / name
    executable = build / ('table-check-' + name)
    subprocess.run(['gcc', '-std=gnu11', '-DAUTOCONF', '-D' + define,
                    '-I' + str(source / 'include'), '-I' + str(source / 'src'),
                    str(probe), '-o', str(executable)], check=True)
    output = subprocess.check_output([str(executable)])
    (build / ('table-check-' + name + '.txt')).write_bytes(output)
    results.append(output)
if results[0] != results[1]:
    raise SystemExit('Host and Android object/monster tables differ.')
print('PASS: generated object/monster counts match both compiled tables; '
      'GOLD_PIECE names gold piece; all host/Android table entries match.')

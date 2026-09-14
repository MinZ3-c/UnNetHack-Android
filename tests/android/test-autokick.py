#!/usr/bin/env python3
"""Test the actual door dispatch with stubbed lock picking and kicking.

Added 2026-09-14. NetHack may be freely redistributed; see LICENSE.
Run with Python and gcc on Linux/WSL. No game or save files are opened.
"""
from pathlib import Path
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[2]
source = (repo / 'src/lock.c').read_text()
start = source.index('        if (locked) {', source.index('doopen_indir(coordxy'))
end = source.index('        return res;', start)
dispatch = source[start:end]
harness = r'''
#include <assert.h>
#include <stddef.h>
#include <string.h>
#define AUTO_OPEN 1
#define TRUE 1
#define SKELETON_KEY 1
#define CREDIT_CARD 2
#define LOCK_PICK 3
struct obj { int unused; } tool;
struct { int autounlock; } flags;
struct { int autokick; } iflags;
static int key, picks, kicks;
static int answer = 'y', prompts;
static const char *ynchars = "yn";
static int yn_function(const char *q, const char *choices, char def) {
    assert(!strcmp(q, "Kick it open?") && def == 'n');
    ++prompts;
    return answer;
}
static struct obj *carrying(int type) { return key == type ? &tool : NULL; }
static int pick_lock(struct obj *o, int x, int y, int a) { ++picks; return 1; }
static int dokick_at(int x, int y) { assert(x == 4 && y == 5); ++kicks; return 1; }
static int run(int locked, int x, int y) {
    struct { int x,y; } cc = {4,5};
    int res = 0;
''' + dispatch + r'''
    return res;
}
int main(void) {
    assert(run(1,4,5)==0 && kicks==0);
    iflags.autokick=1;
    answer='n';
    assert(run(1,4,5)==0 && kicks==0 && prompts==1);
    answer=27;
    assert(run(1,4,5)==0 && kicks==0);
    answer='y';
    assert(run(1,4,5)==1 && kicks==1);
    assert(run(0,4,5)==0 && kicks==1);
    assert(run(1,0,0)==1 && kicks==2);
    kicks=1;
    flags.autounlock=1;
    int previous_prompts = prompts;
    for (key=1; key<=3; ++key) {
        assert(run(1,4,5)==0 && kicks==1);
    }
    assert(picks==3);
    assert(prompts==previous_prompts);
    key=0;
    assert(run(1,4,5)==1 && kicks==2);
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='unnethack-autokick-') as directory:
    path = Path(directory)
    (path / 'test.c').write_text(harness)
    subprocess.run(['gcc', str(path / 'test.c'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
print('PASS: opt-in, one kick, locked doors only, movement and explicit open, unlocking priority.')

#!/usr/bin/env python3
"""Exercise the real Android restore entry point with stubbed save I/O.

Added 2026-09-14. NetHack may be freely redistributed; see LICENSE.
Run on Linux/WSL with gcc. Does not read any actual save files.
"""
from pathlib import Path
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[2]
source = (repo / 'src/files.c').read_text()
start = source.index('NHFILE *\nrestore_saved_game(void)')
end = source.index('\nchar**\nget_saved_games(void)', start)
function = source[start:end]
stubs = r'''
#include <assert.h>
#include <setjmp.h>
#include <stdlib.h>
#define ANDROID 1
#define FALSE 0
#define SAVEPREFIX 0
#define SAVEF "test-save"
typedef struct { int unused; } NHFILE;
static NHFILE save;
static int invalid, closed, deleted, exited, messages;
static jmp_buf checkpoint;
static void set_savefile_name(void) {}
static const char *fqname(const char *s, int a, int b) { return s; }
static void uncompress(const char *s) {}
static NHFILE *open_savefile(void) { return &save; }
static int validate(NHFILE *f, const char *s, int b) { return invalid; }
static void close_nhfile(NHFILE *f) { ++closed; }
static int delete_savefile(void) { ++deleted; return 0; }
static void raw_print(const char *s) { ++messages; }
static void wait_synch(void) {}
static void nethack_exit(int status) { exited = status; longjmp(checkpoint, 1); }
'''
test = r'''
int main(void) {
    assert(restore_saved_game() == &save);
    assert(!closed && !deleted && !exited);
    invalid = 1;
    if (!setjmp(checkpoint)) {
        restore_saved_game();
        abort(); /* must not return and start a replacement game */
    }
    assert(closed == 1 && deleted == 0 && exited == EXIT_FAILURE && messages > 0);
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='unnethack-save-test-') as directory:
    path = Path(directory)
    (path / 'test.c').write_text(stubs + function + test)
    subprocess.run(['gcc', '-std=c11', str(path / 'test.c'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
print('PASS: valid saves proceed; incompatible Android saves are closed, preserved and loading stops.')

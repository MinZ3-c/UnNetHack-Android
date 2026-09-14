/* Android regression test, 2026-09-14. See the NetHack license. */
/* Run with the built libunnethack.so path on an Android device. */
#include "hack.h"
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    void *library;
    struct objclass *table;
    struct objdescr *descriptions;
    struct monst *player;
    struct permonst *monsters;
    char *(*name_object)(struct obj *);
    struct obj gold = {0};
    char *name;
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
    if (argc != 2) return 2;
    printf("Loading %s; GOLD_PIECE=%d\n", argv[1], GOLD_PIECE);
    library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!library) { fprintf(stderr, "%s\n", dlerror()); return 2; }
    table = dlsym(library, "objects");
    descriptions = dlsym(library, "obj_descr");
    name_object = dlsym(library, "xname");
    player = dlsym(library, "youmonst");
    monsters = dlsym(library, "mons");
    if (!table || !descriptions || !name_object || !player || !monsters) return 2;
    /* xname checks whether the player has eyes; no game has initialized it. */
    player->data = &monsters[PM_HUMAN];
    printf("GOLD_PIECE=%d, name=%s, class=%d (expected %d), object-size=%zu\n",
           GOLD_PIECE, descriptions[GOLD_PIECE].oc_name,
           table[GOLD_PIECE].oc_class, COIN_CLASS, sizeof(*table));
    if (strcmp(descriptions[GOLD_PIECE].oc_name, "gold piece")
        || table[GOLD_PIECE].oc_class != COIN_CLASS) return 1;
    table[GOLD_PIECE].oc_name_idx = GOLD_PIECE;
    table[GOLD_PIECE].oc_descr_idx = GOLD_PIECE;
    gold.otyp = GOLD_PIECE;
    gold.oclass = COIN_CLASS;
    gold.dknown = gold.known = 1;
    gold.quan = 1;
    name = name_object(&gold);
    printf("1: %s\n", name);
    if (strcmp(name, "gold piece")) return 1;
    gold.quan = 23;
    name = name_object(&gold);
    printf("23: %s\n", name);
    if (strcmp(name, "gold pieces")) return 1;
    puts("PASS: actual Android library names gold correctly.");
    dlclose(library);
    return 0;
}

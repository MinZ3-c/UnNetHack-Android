/* Android inventory-menu regression test, 2026-09-14. See LICENSE. */
/* Loads the real library; substitutes window callbacks and a tiny inventory. */
#include "hack.h"
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int menus, prompts, cancel_mode, seen[256], expand_menu;
static char chosen = 'J';
static long quantity = -1;
static void noop_window(winid w) { (void)w; }
static void text_window(winid w, int a, const char *s) { (void)w; (void)a; (void)s; }
static void end_test_menu(winid w, const char *s) { (void)w; (void)s; }
static void raw_text(const char *s) { printf("message: %s\n", s); }
static void add_test_item(winid w, int g, int c, const ANY_P *id,
                          char a, char group, int attr, const char *s, unsigned int p)
{
    (void)w; (void)g; (void)c; (void)a; (void)group; (void)attr; (void)s; (void)p;
    if (id->a_char) seen[(unsigned char)id->a_char] = 1;
}
static int pick_test_item(winid w, int how, MENU_ITEM_P **result)
{
    (void)w; (void)how;
    if (++menus > 3) { fputs("menu loop\n", stderr); exit(1); }
    *result = NULL;
    if (cancel_mode) return cancel_mode == 1 ? -1 : 0;
    *result = calloc(1, sizeof(**result));
    (*result)->item.a_char = expand_menu && menus == 1 ? '*' : chosen;
    (*result)->count = quantity;
    return 1;
}
static char letter_prompt(const char *q, const char *choices, char def)
{
    (void)q; (void)choices; (void)def; ++prompts; return chosen;
}
#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #c); return 1; } } while (0)
#define SYMBOL(type, name) type *name = dlsym(library, #name); CHECK(name)
int main(int argc, char **argv)
{
    void *library;
    struct obj helmet = {0}, dagger = {0};
    struct obj *(*choose_object)(const char *, const char *);
    const char armor[] = {ARMOR_CLASS, 0};
    const char drop[] = {ALLOW_COUNT, ALL_CLASSES, 0};
    int i;
    setbuf(stdout, NULL);
    if (argc != 2) return 2;
    library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!library) { fprintf(stderr, "%s\n", dlerror()); return 2; }
    SYMBOL(struct window_procs, windowprocs);
    SYMBOL(struct instance_flags, iflags);
    SYMBOL(struct flag, flags);
    SYMBOL(struct monst, youmonst);
    SYMBOL(struct permonst, mons);
    SYMBOL(struct objclass, objects);
    SYMBOL(struct obj *, invent);
    choose_object = dlsym(library, "getobj"); CHECK(choose_object);
    youmonst->data = &mons[PM_HUMAN];
    for (i = 0; i < NUM_OBJECTS; ++i) objects[i].oc_name_idx = objects[i].oc_descr_idx = i;
    flags->invlet_constant = 1;
    flags->sortpack = 0;
    iflags->force_invmenu = 1;
    helmet.otyp = HELMET; helmet.oclass = ARMOR_CLASS; helmet.invlet = 'J';
    helmet.quan = 1; helmet.known = helmet.dknown = 1; helmet.where = OBJ_INVENT;
    dagger.otyp = DAGGER; dagger.oclass = WEAPON_CLASS; dagger.invlet = 'a';
    dagger.quan = 23; dagger.known = dagger.dknown = 1; dagger.where = OBJ_INVENT;
    helmet.nobj = &dagger; *invent = &helmet;
    windowprocs->win_start_menu = noop_window;
    windowprocs->win_add_menu = add_test_item;
    windowprocs->win_end_menu = end_test_menu;
    windowprocs->win_select_menu = pick_test_item;
    windowprocs->win_putstr = text_window;
    windowprocs->win_raw_print = raw_text;
    windowprocs->win_yn_function = letter_prompt;
    CHECK(choose_object(armor, "wear") == &helmet);
    CHECK(menus == 1 && prompts == 0 && seen['J'] && !seen['a']);
    puts("PASS: wear opens a filtered menu even with one eligible item.");
    memset(seen, 0, sizeof seen); menus = 0; expand_menu = 1;
    CHECK(choose_object(armor, "wear") == &helmet);
    CHECK(menus == 2 && prompts == 0 && seen['a']);
    puts("PASS: list everything expands the selection.");
    menus = 0; expand_menu = 0; chosen = 'a'; quantity = 23;
    CHECK(choose_object(drop, "drop") == &dagger);
    CHECK(menus == 1 && prompts == 0);
    puts("PASS: drop opens the menu and accepts its quantity.");
    for (cancel_mode = 1; cancel_mode <= 2; ++cancel_mode) {
        menus = 0;
        CHECK(choose_object(armor, "wear") == NULL);
        CHECK(menus == 1 && prompts == 0);
    }
    puts("PASS: back and empty selection cancel without reopening.");
    menus = 0; cancel_mode = 0; chosen = 'J'; iflags->force_invmenu = 0;
    CHECK(choose_object(armor, "wear") == &helmet);
    CHECK(menus == 0 && prompts == 1);
    puts("PASS: disabling force_invmenu restores the letter prompt.");
    return 0;
}

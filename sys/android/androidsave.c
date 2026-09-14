/* Android port maintainers: modified for Android integration; publication notice added 2026-09-13. Earlier individual edit dates were not preserved in the uploaded snapshot. */
/* Android save selection and recovery for UnNetHack's struct-level format.
 * NetHack may be freely redistributed. See license for details.
 */
#include "hack.h"
#include <dirent.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

char **android_saved_games(void)
{
    char **result = calloc(257, sizeof *result);
    char prefix[32], path[BUFSZ];
    int count = 0, pass;
    snprintf(prefix, sizeof prefix, "%d", (int) getuid());
    for (pass = 0; pass < 2; ++pass) {
        const char *directory = pass ? "." : "save";
        DIR *dir = opendir(directory);
        struct dirent *entry;
        if (!dir) continue;
        while (count < 256 && (entry = readdir(dir))) {
            char name[PL_NSIZ];
            const char *tail;
            size_t len;
            int i;
            struct stat st;
            if (strncmp(entry->d_name, prefix, strlen(prefix))) continue;
            tail = entry->d_name + strlen(prefix);
            len = strlen(tail);
            if (pass) {
                if (len <= 2 || strcmp(tail + len - 2, ".0")) continue;
                len -= 2;
            }
            if (!len || len >= sizeof name || memchr(tail, '.', len)) continue;
            snprintf(path, sizeof path, "%s/%s", directory, entry->d_name);
            if (stat(path, &st) || !S_ISREG(st.st_mode) || st.st_size <= 4) continue;
            memcpy(name, tail, len);
            name[len] = 0;
            for (i = 0; i < count && strcmp(name, result[i]); ++i) ;
            if (i == count) result[count++] = dupstr(name);
        }
        closedir(dir);
    }
    return result;
}

static boolean copy_fd(int in, int out)
{
    char buf[8192];
    ssize_t n, written;
    while ((n = read(in, buf, sizeof buf)) > 0) {
        ssize_t offset = 0;
        while (offset < n) {
            written = write(out, buf + offset, n - offset);
            if (written <= 0) return FALSE;
            offset += written;
        }
    }
    return n == 0;
}

/* Keep original checkpoint files under a non-game suffix after reconstruction. */
boolean android_recover_checkpoint(void)
{
    char zero[BUFSZ], path[BUFSZ], temp[BUFSZ], destination[BUFSZ];
    char saved_name[PL_NSIZ + 13]; /* SAVEF on this UNIX, non-FILE_AREAS build */
    unsigned char header[1 + sizeof(int) + sizeof(struct version_info)
                         + sizeof(struct savefile_info) + sizeof(int) + PL_NSIZ];
    int gfd = -1, lfd = -1, out = -1, pid, level, lev, cmc, namesize;
    int processed[128] = {0};
    size_t fixed = sizeof header - PL_NSIZ;
    struct stat st;
    boolean ok = FALSE;
    set_levelfile_name(lock, 0);
    snprintf(zero, sizeof zero, "%s", fqname(lock, LEVELPREFIX, 0));
    gfd = open(zero, O_RDONLY);
    if (gfd < 0) return FALSE;
    if (fstat(gfd, &st)) goto finish;
    if (st.st_size == sizeof(int)) {
        /* A character name was entered but no game state was written. */
        close(gfd);
        return TRUE;
    }
    if (read(gfd, &pid, sizeof pid) != sizeof pid
        || read(gfd, &level, sizeof level) != sizeof level
        || level < 1 || level > 127
        || read(gfd, saved_name, sizeof saved_name) != sizeof saved_name
        || read(gfd, header, fixed) != (ssize_t) fixed) goto finish;
    memcpy(&cmc, header + 1, sizeof cmc);
    memcpy(&namesize, header + fixed - sizeof namesize, sizeof namesize);
    if (header[0] != 'h' || cmc != 0 || namesize != PL_NSIZ
        || read(gfd, header + fixed, PL_NSIZ) != PL_NSIZ) goto finish;
    set_savefile_name();
    snprintf(destination, sizeof destination, "%s", fqname(SAVEF, SAVEPREFIX, 0));
    /* Never replace an existing regular save with a checkpoint. */
    if (access(destination, F_OK) == 0) goto finish;
    snprintf(temp, sizeof temp, "%s.recover.tmp", destination);
    out = open(temp, O_WRONLY | O_CREAT | O_EXCL, FCMASK);
    if (out < 0) goto finish;
    if (write(out, header, sizeof header) != sizeof header) goto finish;
    set_levelfile_name(lock, level);
    lfd = open(fqname(lock, LEVELPREFIX, 0), O_RDONLY);
    if (lfd < 0 || !copy_fd(lfd, out)) goto finish;
    close(lfd); lfd = -1;
    if (!copy_fd(gfd, out)) goto finish;
    processed[0] = processed[level] = 1;
    for (lev = 1; lev < 128; ++lev) {
        xint8 marker = (xint8) lev;
        if (lev == level) continue;
        set_levelfile_name(lock, lev);
        lfd = open(fqname(lock, LEVELPREFIX, 0), O_RDONLY);
        if (lfd < 0) {
            if (errno == ENOENT) continue;
            goto finish;
        }
        if (write(out, &marker, sizeof marker) != sizeof marker || !copy_fd(lfd, out)) goto finish;
        close(lfd); lfd = -1;
        processed[lev] = 1;
    }
    if (fsync(out)) goto finish;
    close(out); out = -1;
    if (rename(temp, destination)) goto finish;
    for (lev = 0; lev < 128; ++lev) if (processed[lev]) {
        int suffix = 0;
        set_levelfile_name(lock, lev);
        snprintf(path, sizeof path, "%s", fqname(lock, LEVELPREFIX, 0));
        do {
            snprintf(temp, sizeof temp, "%s.recovered.%d", path, suffix++);
        } while (access(temp, F_OK) == 0);
        /* Retain a copy of the interrupted session for diagnosis. */
        if (rename(path, temp)) goto finish;
    }
    ok = TRUE;
finish:
    if (gfd >= 0) close(gfd);
    if (lfd >= 0) close(lfd);
    if (out >= 0) close(out);
    set_levelfile_name(lock, 0);
    return ok;
}

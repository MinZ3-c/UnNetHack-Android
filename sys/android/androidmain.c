/* Android port maintainers: modified for Android integration; publication notice added 2026-09-13. Earlier individual edit dates were not preserved in the uploaded snapshot. */
/* androidmain.c
 * based on unixmain.c
 */

#include "hack.h"
#include "dlb.h"
extern void setUsername(void);
#include <setjmp.h>

#include <sys/stat.h>
#include <pwd.h>
#ifndef O_RDONLY
#include <fcntl.h>
#endif

static jmp_buf env;

extern struct passwd *getpwuid( uid_t);
extern struct passwd *getpwnam(const char *);

static boolean whoami(void);
static void process_options(int, char **);

static void wd_message(void);

static char *make_lockname(filename, lockname)
const char *filename;
char *lockname;
{
#  ifdef NO_FILE_LINKS
	Strcpy(lockname, LOCKDIR);
	Strcat(lockname, "/");
	Strcat(lockname, filename);
#  else
	Strcpy(lockname, filename);
#  endif
	Strcat(lockname, "_lock");
	return lockname;
}

void remove_lock_file(const char *filename)
{
	char locknambuf[BUFSZ];
	const char *lockname;

	lockname = make_lockname(filename, locknambuf);
	unlink(lockname);
}

void nethack_exit(int code)
{
	longjmp(env, code);
}

int UnNetHackMain(int argc, char** argv)
{
	debuglog("Starting UnNetHack!");

	int val;

	val = setjmp(env);
	if(val)
	{
		debuglog("exiting...");
		return 0;
	}

	NHFILE *nhfp;
	boolean resuming = FALSE;
	boolean exact_username;
	FILE* fp;

	early_init();
	hname = argv[0];
	hackpid = getpid();
	(void)umask(0777 & ~FCMASK);
	(void) mkdir("save", 0700);

	// hack
	// remove dangling locks
	remove_lock_file(RECORD);
	remove_lock_file(HLOCK);
	// make sure RECORD exists
	fp = fopen_datafile(RECORD, "a", SCOREPREFIX);
	if (fp) fclose(fp);
	/* fcntl locking needs the permanent lock target to exist. */
	fp = fopen_datafile(HLOCK, "a", LOCKPREFIX);
	if (fp) fclose(fp);

	choose_windows(DEFAULT_WINDOW_SYS);

	initoptions();

	init_nhwindows(&argc, argv);
	//exact_username = whoami();

	/*
	 * It seems you really want to play.
	 */
	u.uhp = 1; /* prevent RIP on early quits */

	process_options(argc, argv); /* command line options */

#ifdef DEF_PAGER
	if(!(catmore = nh_getenv("HACKPAGER")) && !(catmore = nh_getenv("PAGER")))
	catmore = DEF_PAGER;
#endif

#ifdef MAIL
	getmailstatus();
#endif

	plnamesuffix(); /* strip suffix from name; calls askname() */
					/* again if suffix was whole name */
					/* accepts any suffix */
#ifdef WIZARD
	if(!wizard)
#endif
	setUsername();

	Sprintf(lock, "%d%s", (int)getuid(), plname);
	getlock();

	dlb_init(); /* must be before newgame() */

	/*
	 * Initialization of the boundaries of the mazes
	 * Both boundaries have to be even.
	 */
	x_maze_max = COLNO - 1;
	if(x_maze_max % 2)
		x_maze_max--;
	y_maze_max = ROWNO - 1;
	if(y_maze_max % 2)
		y_maze_max--;

	/*
	 *  Initialize the vision system.  This must be before mklev() on a
	 *  new game or before a level restore on a saved game.
	 */
	vision_init();

	display_gamewindows();

	LI = 25;
	CO = 180;

	if((nhfp = restore_saved_game()) != NULL)
	{
#ifdef WIZARD
		/* Since wizard is actually flags.debug, restoring might
		 * overwrite it.
		 */
		boolean remember_wiz_mode = wizard;
#endif
		const char *fq_save = fqname(SAVEF, SAVEPREFIX, 1);

#ifdef NEWS
		if(iflags.news)
		{
			display_file(NEWS, FALSE);
			iflags.news = FALSE; /* in case dorecover() fails */
		}
#endif
		raw_print("restore save");
		pline("Restoring save file...");
		mark_synch(); /* flush output */
		if(!dorecover(nhfp))
			goto not_recovered;
#ifdef WIZARD
		if(!wizard && remember_wiz_mode) wizard = TRUE;
#endif
		resuming = TRUE;
		check_special_room(FALSE);
		wd_message();

		if(discover || wizard)
		{
			if(yn("Do you want to keep the save file?") == 'n')
			{
				(void)delete_savefile();
			}
			else
			{
				compress_area(NULL, fq_save);
			}
		}
		flags.move = 0;
	}
	else
	{
		not_recovered: player_selection();
		newgame();
		wd_message();

		flags.move = 0;

	}

	moveloop(resuming);

	return (0);
}

static void process_options(argc, argv)
	int argc;char *argv[];
{
	int i;

	/*
	 * Process options.
	 */
	while(argc > 1 && argv[1][0] == '-')
	{
		argv++;
		argc--;
		switch(argv[0][1])
		{
		case 'D':
#ifdef WIZARD
			wizard = TRUE;
		break;
#endif
		/* otherwise fall thru to discover */
		case 'X':
			discover = TRUE;
		break;
#ifdef NEWS
			case 'n':
			iflags.news = FALSE;
			break;
#endif
		case 'u':
			if(!*plname)
			{
				if(argv[0][2])
					(void)strncpy(plname, argv[0] + 2, sizeof(plname) - 1);
				else if(argc > 1)
				{
					argc--;
					argv++;
					(void)strncpy(plname, argv[0], sizeof(plname) - 1);
				}
				else
					raw_print("Player name expected after -u");
			}
		break;
		case 'I':
		case 'i':
			if(!strncmpi(argv[0] + 1, "IBM", 3))
				switch_graphics(IBM_GRAPHICS);
		break;
			/*  case 'D': */
		case 'd':
			if(!strncmpi(argv[0] + 1, "DEC", 3))
				switch_graphics(DEC_GRAPHICS);
		break;
		case 'p': /* profession (role) */
			if(argv[0][2])
			{
				if((i = str2role(&argv[0][2])) >= 0)
					flags.initrole = i;
			}
			else if(argc > 1)
			{
				argc--;
				argv++;
				if((i = str2role(argv[0])) >= 0)
					flags.initrole = i;
			}
		break;
		case 'r': /* race */
			if(argv[0][2])
			{
				if((i = str2race(&argv[0][2])) >= 0)
					flags.initrace = i;
			}
			else if(argc > 1)
			{
				argc--;
				argv++;
				if((i = str2race(argv[0])) >= 0)
					flags.initrace = i;
			}
		break;
		case '@':
			flags.randomall = 1;
		break;
		default:
			if((i = str2role(&argv[0][1])) >= 0)
			{
				flags.initrole = i;
				break;
			}
			/* else raw_printf("Unknown option: %s", *argv); */
		}
	}
}

static boolean whoami()
{
	/*
	 * Who am i? Algorithm: 1. Use name as specified in NETHACKOPTIONS
	 *			2. Use getlogin()		(if 1. fails)
	 * The resulting name is overridden by command line options.
	 * If everything fails, or if the resulting name is some generic
	 * account like "games", "play", "player", "hack" then eventually
	 * we'll ask him.
	 * Note that we trust the user here; it is possible to play under
	 * somebody else's name.
	 */
	register char *s;

	if(*plname)
		return FALSE;
	if((s = getlogin()))
		(void)strncpy(plname, s, sizeof(plname) - 1);
	return TRUE;
}

#ifdef PORT_HELP
void
port_help()
{
	/*
	 * Display unix-specific help.   Just show contents of the helpfile
	 * named by PORT_HELP.
	 */
	display_file(PORT_HELP, TRUE);
}
#endif

static void wd_message()
{
	if(discover)
		You("are in non-scoring discovery mode.");
}

/*
 * Add a slash to any name not ending in /. There must
 * be room for the /
 */
void append_slash(name)
	char *name;
{
	char *ptr;

	if(!*name)
		return;
	ptr = name + (strlen(name) - 1);
	if(*ptr != '/')
	{
		*++ptr = '/';
		*++ptr = '\0';
	}
	return;
}


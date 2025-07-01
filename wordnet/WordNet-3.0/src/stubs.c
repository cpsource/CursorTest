/* Modernized gateway between Tcl and the Wordnet C library */

#ifdef _WINDOWS
#include <windows.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tcl.h>
#include <tk.h>
#include <wn.h>

static char *Id = "$Id: stubs.c,v 1.7 2005/04/29 19:01:57 wn Exp $";

static char resultbuf[SEARCHBUF];

#ifndef HAVE_LANGINFO_CODESET
char *nl_langinfo(int item) {
   static char val[4] = "Sun";
   return val;
}
#endif

int wn_findvalidsearches(ClientData clientData, Tcl_Interp *interp,
                         int argc, char *argv[])
{
    unsigned int bitfield;
    static char bitfieldstr[32];
    char *morph;
    int pos;

    if (argc != 3) {
        Tcl_SetResult(interp,
            "usage: findvalidsearches searchword partofspeechnum",
            TCL_STATIC);
        return TCL_ERROR;
    }

    pos = atoi(argv[2]);
    bitfield = is_defined(argv[1], pos);

    if ((morph = morphstr(argv[1], pos)) != NULL) {
        do {
            bitfield |= is_defined(morph, pos);
        } while ((morph = morphstr(NULL, pos)) != NULL);
    }

    snprintf(bitfieldstr, sizeof(bitfieldstr), "%u", bitfield);
    Tcl_SetResult(interp, bitfieldstr, TCL_STATIC);

    return TCL_OK;
}

int wn_bit(ClientData clientData, Tcl_Interp *interp,
           int argc, char *argv[])
{
    unsigned int bitfield;
    static char bitfieldstr[32];
    int whichbit;

    if (argc != 2) {
        Tcl_SetResult(interp, "usage: bit bitnum", TCL_STATIC);
        return TCL_ERROR;
    }

    whichbit = atoi(argv[1]);
    bitfield = bit(whichbit);

    snprintf(bitfieldstr, sizeof(bitfieldstr), "%u", bitfield);
    Tcl_SetResult(interp, bitfieldstr, TCL_STATIC);

    return TCL_OK;
}

int wn_search(ClientData clientData, Tcl_Interp *interp,
              int argc, char *argv[])
{
    int pos, searchtype, sense;
    char *morph;

    if (argc != 5) {
        Tcl_SetResult(interp,
            "usage: search searchword partofspeechnum searchtypenum sensenum",
            TCL_STATIC);
        return TCL_ERROR;
    }

    pos = atoi(argv[2]);
    searchtype = atoi(argv[3]);
    sense = atoi(argv[4]);

    strcpy(resultbuf, findtheinfo(argv[1], pos, searchtype, sense));

    if ((morph = morphstr(argv[1], pos)) != NULL) {
        do {
            strcat(resultbuf, findtheinfo(morph, pos, searchtype, sense));
        } while ((morph = morphstr(NULL, pos)) != NULL);
    }

    Tcl_SetResult(interp, resultbuf, TCL_VOLATILE);

    return TCL_OK;
}

int wn_glosses(ClientData clientData, Tcl_Interp *interp,
               int argc, char *argv[])
{
    if (argc != 2) {
        Tcl_SetResult(interp, "usage: glosses [1 | 0]", TCL_STATIC);
        return TCL_ERROR;
    }
    dflag = atoi(argv[1]);
    return TCL_OK;
}

int wn_fileinfo(ClientData clientData, Tcl_Interp *interp,
                int argc, char *argv[])
{
    if (argc != 2) {
        Tcl_SetResult(interp, "usage: fileinfo [1 | 0]", TCL_STATIC);
        return TCL_ERROR;
    }
    fileinfoflag = atoi(argv[1]);
    return TCL_OK;
}

int wn_byteoffset(ClientData clientData, Tcl_Interp *interp,
                  int argc, char *argv[])
{
    if (argc != 2) {
        Tcl_SetResult(interp, "usage: byteoffset [1 | 0]", TCL_STATIC);
        return TCL_ERROR;
    }
    offsetflag = atoi(argv[1]);
    return TCL_OK;
}

int wn_senseflag(ClientData clientData, Tcl_Interp *interp,
                 int argc, char *argv[])
{
    if (argc != 2) {
        Tcl_SetResult(interp, "usage: senseflag [1 | 0]", TCL_STATIC);
        return TCL_ERROR;
    }
    wnsnsflag = atoi(argv[1]);
    return TCL_OK;
}

int wn_contextualhelp(ClientData clientData, Tcl_Interp *interp,
                      int argc, char *argv[])
{
    int pos, searchtype;

    if (argc != 3) {
        Tcl_SetResult(interp,
            "usage: contextualhelp partofspeechnum searchtypenum",
            TCL_STATIC);
        return TCL_ERROR;
    }

    pos = atoi(argv[1]);
    searchtype = atoi(argv[2]);

    Tcl_SetResult(interp, helptext[pos][searchtype], TCL_STATIC);

    return TCL_OK;
}

int wn_reopendb(ClientData clientData, Tcl_Interp *interp,
                int argc, char *argv[])
{
    if (argc != 1) {
        Tcl_SetResult(interp, "usage: reopendb", TCL_STATIC);
        return TCL_ERROR;
    }
    re_wninit();
    return TCL_OK;
}

int wn_abortsearch(ClientData clientData, Tcl_Interp *interp,
                   int argc, char *argv[])
{
    if (argc != 1) {
        Tcl_SetResult(interp, "usage: abortsearch", TCL_STATIC);
        return TCL_ERROR;
    }
    abortsearch = 1;
    return TCL_OK;
}

void tkwn_doevents(void)
{
    while (Tcl_DoOneEvent(TCL_WINDOW_EVENTS | TCL_DONT_WAIT) != 0) {}
}

int tkwn_displayerror(char *msg)
{
#ifdef _WINDOWS
    MessageBeep(MB_ICONEXCLAMATION);
    MessageBox(NULL, msg, "WordNet Library Error",
        MB_ICONEXCLAMATION | MB_OK | MB_TASKMODAL | MB_SETFOREGROUND);
#else
    fprintf(stderr, "%s", msg);
#endif
    return -1;
}

int Wordnet_Init(Tcl_Interp *interp)
{
    interface_doevents_func = tkwn_doevents;
    display_message = tkwn_displayerror;
    wninit();

    Tcl_CreateCommand(interp, "findvalidsearches",
        (Tcl_CmdProc *) wn_findvalidsearches,
        NULL, NULL);
    Tcl_CreateCommand(interp, "bit",
        (Tcl_CmdProc *) wn_bit,
        NULL, NULL);
    Tcl_CreateCommand(interp, "search",
        (Tcl_CmdProc *) wn_search,
        NULL, NULL);
    Tcl_CreateCommand(interp, "glosses",
        (Tcl_CmdProc *) wn_glosses,
        NULL, NULL);
    Tcl_CreateCommand(interp, "fileinfo",
        (Tcl_CmdProc *) wn_fileinfo,
        NULL, NULL);
    Tcl_CreateCommand(interp, "byteoffset",
        (Tcl_CmdProc *) wn_byteoffset,
        NULL, NULL);
    Tcl_CreateCommand(interp, "senseflag",
        (Tcl_CmdProc *) wn_senseflag,
        NULL, NULL);
    Tcl_CreateCommand(interp, "contextualhelp",
        (Tcl_CmdProc *) wn_contextualhelp,
        NULL, NULL);
    Tcl_CreateCommand(interp, "reopendb",
        (Tcl_CmdProc *) wn_reopendb,
        NULL, NULL);
    Tcl_CreateCommand(interp, "abortsearch",
        (Tcl_CmdProc *) wn_abortsearch,
        NULL, NULL);

    return TCL_OK;
}


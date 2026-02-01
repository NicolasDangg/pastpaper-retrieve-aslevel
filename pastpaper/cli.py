import curses
import os

from pastpaper.scraper import scrape_subject
from pastpaper.subjects import LEVELS, PAPER_TYPES, SESSIONS, SUBJECTS


def multiselect(stdscr, title, options):
    curses.curs_set(0)
    selected = set()
    idx = 0
    keys = list(options.keys())

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, title)

        for i, key in enumerate(keys):
            marker = "[x]" if key in selected else "[ ]"
            line = f"{marker} {options[key][0] if isinstance(options[key], tuple) else options[key]}"
            if i == idx:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(i + 2, 2, line)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 2, line)

        stdscr.addstr(len(keys) + 4, 2, "space = select | enter = confirm | esc = quit")
        keypress = stdscr.getch()

        if keypress == curses.KEY_UP and idx > 0:
            idx -= 1
        elif keypress == curses.KEY_DOWN and idx < len(keys) - 1:
            idx += 1
        elif keypress == ord(" "):
            k = keys[idx]
            selected.symmetric_difference_update({k})
        elif keypress in (10, 13):
            return list(selected)
        elif keypress == 27:
            exit(0)


def singleselect(stdscr, title, options):
    curses.curs_set(0)
    idx = 0
    keys = list(options.keys())

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, title)

        for i, key in enumerate(keys):
            value = options[key][0] if isinstance(options[key], tuple) else options[key]
            if i == idx:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(i + 2, 2, value)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 2, value)

        keypress = stdscr.getch()

        if keypress == curses.KEY_UP and idx > 0:
            idx -= 1
        elif keypress == curses.KEY_DOWN and idx < len(keys) - 1:
            idx += 1
        elif keypress in (10, 13):
            return keys[idx]
        elif keypress == 27:
            exit(0)


def tui(stdscr):
    level_key = singleselect(stdscr, "select level", LEVELS)
    subject_key = singleselect(stdscr, "select subject", SUBJECTS)
    paper_key = singleselect(stdscr, "select paper type", PAPER_TYPES)

    session_keys = multiselect(stdscr, "select sessions", SESSIONS)

    stdscr.clear()
    stdscr.addstr(0, 0, "enter years (comma separated, e.g. 23,24,25): ")
    curses.echo()
    years = stdscr.getstr().decode().replace(" ", "").split(",")
    curses.noecho()

    stdscr.clear()
    stdscr.addstr(0, 0, "enter paper numbers (e.g. 11,12,13 or leave blank for all): ")
    curses.echo()
    paper_nums_raw = stdscr.getstr().decode().replace(" ", "")
    curses.noecho()

    paper_numbers = paper_nums_raw.split(",") if paper_nums_raw else None

    level = LEVELS[level_key]
    subject_name, subject_code = SUBJECTS[subject_key]
    paper_type = PAPER_TYPES[paper_key]

    session_codes = [SESSIONS[k][1] for k in session_keys]
    year_codes = [y[-2:] for y in years]

    out_dir = os.path.join(os.getcwd(), "pastpaper", subject_name.replace(" ", "_"))

    stdscr.clear()
    stdscr.addstr(0, 0, "downloading... press any key to start")
    stdscr.getch()

    curses.endwin()

    scrape_subject(
        subject_code=subject_code,
        level=level,
        paper_type=paper_type,
        session_code=session_codes,
        year_code=year_codes,
        paper_numbers=paper_numbers,
        out_dir=out_dir,
    )


def main():
    curses.wrapper(tui)


if __name__ == "__main__":
    main()

import curses
import os
import time

from pastpaper.scraper import scrape_subject
from pastpaper.subjects import LEVELS, PAPER_TYPES, SESSIONS, SUBJECTS

LOGO = [
    "  ____   _    ____ _____   ____   _    ____  _____ ____  ",
    " |  _ \\ / \\  / ___|_   _| |  _ \\ / \\  |  _ \\| ____|  _ \\ ",
    " | |_) / _ \\ \\___ \\ | |   | |_) / _ \\ | |_) |  _| | |_) |",
    " |  __/ ___ \\ ___) || |   |  __/ ___ \\|  __/| |___|  _ < ",
    " |_| /_/   \\_\\____/ |_|   |_| /_/   \\_\\_|   |_____|_| \\_\\",
    "",
    "Past Paper Retrieve for AS and A Level, by Nicolas Dang",
]


MIN_WIDTH = 80
MIN_HEIGHT = 24


def check_terminal_size(stdscr):
    while True:
        height, width = stdscr.getmaxyx()
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            stdscr.clear()
            stdscr.border()
            center_text(
                stdscr,
                f"Please resize your terminal to at least {MIN_WIDTH}x{MIN_HEIGHT}.",
                height // 2,
                color=2,
                bold=True,
            )
            stdscr.refresh()
            time.sleep(0.2)
        else:
            break


def center_text(stdscr, text, y, color=None, bold=False):
    height, width = stdscr.getmaxyx()
    # Truncate text if too long
    if len(text) > width - 2:
        text = text[: max(0, width - 5)] + "..."
    x = max(0, (width - len(text)) // 2)
    if 0 <= y < height:
        if color:
            stdscr.attron(curses.color_pair(color))
        if bold:
            stdscr.attron(curses.A_BOLD)
        try:
            stdscr.addstr(y, x, text)
        except curses.error:
            pass
        if color:
            stdscr.attroff(curses.color_pair(color))
        if bold:
            stdscr.attroff(curses.A_BOLD)


def multiselect(stdscr, title, options, logo=None):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)
    selected = set()
    idx = 0
    keys = list(options.keys())

    while True:
        check_terminal_size(stdscr)
        stdscr.clear()
        stdscr.border()
        # Draw logo if provided
        logo_height = 0
        if logo:
            for i, line in enumerate(logo):
                center_text(stdscr, line, i + 1, color=1, bold=True)
            logo_height = len(logo) + 2
        center_text(stdscr, title, logo_height, color=1, bold=True)

        for i, key in enumerate(keys):
            marker = "✔" if key in selected else "○"
            line = f"{marker} {options[key][0] if isinstance(options[key], tuple) else options[key]}"
            height, width = stdscr.getmaxyx()
            if len(line) > width - 6:
                line = line[: max(0, width - 9)] + "..."
            y = logo_height + 2 + i
            if i == idx:
                stdscr.attron(curses.color_pair(2))
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, 4, line)
                stdscr.attroff(curses.A_REVERSE)
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(y, 4, line)

        center_text(
            stdscr,
            "SPACE = select | ENTER = confirm | ESC = quit",
            logo_height + 4 + len(keys),
            color=3,
        )
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


def singleselect(stdscr, title, options, logo=None):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    idx = 0
    keys = list(options.keys())

    while True:
        check_terminal_size(stdscr)
        stdscr.clear()
        stdscr.border()
        # Draw logo if provided
        logo_height = 0
        if logo:
            for i, line in enumerate(logo):
                center_text(stdscr, line, i + 1, color=1, bold=True)
            logo_height = len(logo) + 2
        center_text(stdscr, title, logo_height, color=1, bold=True)

        for i, key in enumerate(keys):
            value = options[key][0] if isinstance(options[key], tuple) else options[key]
            height, width = stdscr.getmaxyx()
            if len(value) > width - 6:
                value = value[: max(0, width - 9)] + "..."
            y = logo_height + 2 + i
            if i == idx:
                stdscr.attron(curses.color_pair(2))
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, 4, value)
                stdscr.attroff(curses.A_REVERSE)
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(y, 4, value)

        keypress = stdscr.getch()

        if keypress == curses.KEY_UP and idx > 0:
            idx -= 1
        elif keypress == curses.KEY_DOWN and idx < len(keys) - 1:
            idx += 1
        elif keypress in (10, 13):
            return keys[idx]
        elif keypress == 27:
            exit(0)


import signal


def draw_logo_centered(stdscr):
    height, width = stdscr.getmaxyx()
    logo_height = len(LOGO)
    for i, line in enumerate(LOGO):
        # Truncate logo line if too long
        logo_line = line
        if len(logo_line) > width - 2:
            logo_line = logo_line[: max(0, width - 5)] + "..."
        y = max(0, (height - logo_height) // 2 + i - 6)
        center_text(stdscr, logo_line, y, color=1, bold=True)
    # Add credits line below the logo
    credits = "All credits to Past Paper Co, this is only a client"
    y_credits = max(0, (height - logo_height) // 2 - 6) + logo_height + 1
    if len(credits) > width - 2:
        credits = credits[: max(0, width - 5)] + "..."
    center_text(stdscr, credits, y_credits, color=3, bold=False)
    return y_credits + 1


def tui(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)

    def redraw_selection(draw_func, *args, **kwargs):
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        return draw_func(stdscr, *args, logo_bottom=logo_bottom, **kwargs)

    def singleselect_centered(stdscr, title, options, logo_bottom=0):
        curses.curs_set(0)
        idx = 0
        keys = list(options.keys())
        while True:
            check_terminal_size(stdscr)
            stdscr.clear()
            stdscr.border()
            draw_logo_centered(stdscr)
            center_text(stdscr, title, logo_bottom, color=1, bold=True)
            for i, key in enumerate(keys):
                value = (
                    options[key][0] if isinstance(options[key], tuple) else options[key]
                )
                height, width = stdscr.getmaxyx()
                if len(value) > width - 6:
                    value = value[: max(0, width - 9)] + "..."
                y = logo_bottom + 2 + i
                if i == idx:
                    stdscr.attron(curses.color_pair(2))
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(y, 4, value)
                    stdscr.attroff(curses.A_REVERSE)
                    stdscr.attroff(curses.color_pair(2))
                else:
                    stdscr.addstr(y, 4, value)
            keypress = stdscr.getch()
            if keypress == curses.KEY_UP and idx > 0:
                idx -= 1
            elif keypress == curses.KEY_DOWN and idx < len(keys) - 1:
                idx += 1
            elif keypress in (10, 13):
                return keys[idx]
            elif keypress == 27:
                exit(0)

    def multiselect_centered(stdscr, title, options, logo_bottom=0):
        curses.curs_set(0)
        selected = set()
        idx = 0
        keys = list(options.keys())
        while True:
            check_terminal_size(stdscr)
            stdscr.clear()
            stdscr.border()
            draw_logo_centered(stdscr)
            center_text(stdscr, title, logo_bottom, color=1, bold=True)
            for i, key in enumerate(keys):
                marker = "✔" if key in selected else "○"
                line = f"{marker} {options[key][0] if isinstance(options[key], tuple) else options[key]}"
                height, width = stdscr.getmaxyx()
                if len(line) > width - 6:
                    line = line[: max(0, width - 9)] + "..."
                y = logo_bottom + 2 + i
                if i == idx:
                    stdscr.attron(curses.color_pair(2))
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(y, 4, line)
                    stdscr.attroff(curses.A_REVERSE)
                    stdscr.attroff(curses.color_pair(2))
                else:
                    stdscr.addstr(y, 4, line)
            center_text(
                stdscr,
                "SPACE = select | ENTER = confirm | ESC = quit",
                logo_bottom + 4 + len(keys),
                color=3,
            )
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

    # Dynamic resizing handler
    def handle_resize(sig, frame):
        curses.resize_term(*stdscr.getmaxyx())
        stdscr.clear()
        stdscr.refresh()

    signal.signal(signal.SIGWINCH, handle_resize)

    # Always show logo and selection below it, centered
    level_key = redraw_selection(singleselect_centered, "Select Level", LEVELS)
    subject_key = redraw_selection(singleselect_centered, "Select Subject", SUBJECTS)
    paper_key = redraw_selection(
        singleselect_centered, "Select Paper Type", PAPER_TYPES
    )
    session_keys = redraw_selection(multiselect_centered, "Select Sessions", SESSIONS)

    # Years input
    while True:
        check_terminal_size(stdscr)
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        center_text(
            stdscr,
            "Enter years (comma separated, e.g. 23,24,25):",
            logo_bottom,
            color=1,
            bold=True,
        )
        curses.echo()
        stdscr.attron(curses.color_pair(5))
        height, width = stdscr.getmaxyx()
        prompt = "> "
        if len(prompt) > width - 6:
            prompt = prompt[: max(0, width - 9)] + "..."
        stdscr.addstr(logo_bottom + 2, 4, prompt)
        years = stdscr.getstr(logo_bottom + 2, 6).decode().replace(" ", "").split(",")
        stdscr.attroff(curses.color_pair(5))
        curses.noecho()
        break

    # Paper numbers input
    while True:
        check_terminal_size(stdscr)
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        center_text(
            stdscr,
            "Enter paper numbers (e.g. 11,12,13 or leave blank for all):",
            logo_bottom,
            color=1,
            bold=True,
        )
        curses.echo()
        stdscr.attron(curses.color_pair(5))
        height, width = stdscr.getmaxyx()
        prompt = "> "
        if len(prompt) > width - 6:
            prompt = prompt[: max(0, width - 9)] + "..."
        stdscr.addstr(logo_bottom + 2, 4, prompt)
        paper_nums_raw = stdscr.getstr(logo_bottom + 2, 6).decode().replace(" ", "")
        stdscr.attroff(curses.color_pair(5))
        curses.noecho()
        break

    paper_numbers = paper_nums_raw.split(",") if paper_nums_raw else None

    level = LEVELS[level_key]
    subject_name, subject_code = SUBJECTS[subject_key]
    paper_type = PAPER_TYPES[paper_key]

    session_codes = [SESSIONS[k][1] for k in session_keys]
    year_codes = [y[-2:] for y in years]

    out_dir = os.path.join(
        os.path.expanduser("~"),
        "Documents",
        "past paper",
        f"{subject_name.replace(' ', '_')}-{subject_code}",
    )

    # Summary screen
    while True:
        check_terminal_size(stdscr)
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        center_text(stdscr, "Summary", logo_bottom, color=1, bold=True)
        height, width = stdscr.getmaxyx()
        summary_lines = [
            f"Level: {level}",
            f"Subject: {subject_name}",
            f"Paper Type: {paper_type}",
            f"Sessions: {', '.join(session_codes)}",
            f"Years: {', '.join(year_codes)}",
            f"Paper Numbers: {', '.join(paper_numbers) if paper_numbers else 'All'}",
            f"Download folder: {out_dir}",
        ]
        for i, line in enumerate(summary_lines):
            if len(line) > width - 6:
                line = line[: max(0, width - 9)] + "..."
            stdscr.addstr(logo_bottom + 2 + i, 4, line)
        center_text(
            stdscr, "Press any key to start downloading...", logo_bottom + 11, color=3
        )
        stdscr.getch()
        break

    # Progress bar function
    def show_progress_bar(stdscr, total, current, y, width=50):
        percent = int((current / total) * 100) if total else 0
        filled = int(width * current // total) if total else 0
        bar = "[" + "#" * filled + "-" * (width - filled) + "]"
        stdscr.addstr(y, 4, f"{bar} {percent}% ({current}/{total})")
        stdscr.refresh()

    # Build download tasks
    from pastpaper.scraper import build_download_tasks, download_with_retry

    tasks = build_download_tasks(
        subject_code=subject_code,
        level=level,
        paper_type=paper_type,
        sessions=session_codes,
        years=year_codes,
        paper_numbers=paper_numbers,
        out_dir=out_dir,
    )

    # Download loop with progress bar
    while True:
        check_terminal_size(stdscr)
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        center_text(stdscr, "Downloading...", logo_bottom, color=1, bold=True)
        total = len(tasks)
        y_bar = logo_bottom + 2
        y_status = logo_bottom + 4
        for i, (url, out_path) in enumerate(tasks, 1):
            show_progress_bar(stdscr, total, i, y_bar)
            line = f"Downloading {os.path.basename(out_path)}..."
            height, width = stdscr.getmaxyx()
            if len(line) > width - 6:
                line = line[: max(0, width - 9)] + "..."
            stdscr.addstr(y_status + i, 4, line)
            stdscr.refresh()
            success = download_with_retry(url, out_path)
            status = "✔" if success else "✗"
            line = f"{status} {os.path.basename(out_path)}"
            if len(line) > width - 6:
                line = line[: max(0, width - 9)] + "..."
            stdscr.addstr(y_status + i, 4, line)
            stdscr.refresh()
            time.sleep(0.1)
        show_progress_bar(stdscr, total, total, y_bar)
        center_text(
            stdscr,
            "Download complete! Press any key to exit.",
            y_status + total + 2,
            color=3,
        )
        stdscr.getch()
        break
    curses.endwin()


def main():
    curses.wrapper(tui)


if __name__ == "__main__":
    main()

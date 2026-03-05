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
    
    # Session selection (with validation)
    while True:
        # Filter sessions for Computer Science
        available_sessions = SESSIONS
        if subject_key == "4": # Computer Science (9618)
            available_sessions = {k: v for k, v in SESSIONS.items() if v[0] != "march"}
            
        session_keys = redraw_selection(
            multiselect_centered, "Select Sessions (SPACE to select, ENTER to confirm)", available_sessions
        )
        if session_keys:
            break
        # Show a temporary warning if nothing selected
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        center_text(stdscr, "PLEASE SELECT AT LEAST ONE SESSION!", 1, color=2)
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()
        time.sleep(1)

    # Years input
    while True:
        check_terminal_size(stdscr)
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        center_text(
            stdscr,
            "Enter years (23,24,25) or leave blank for 23,24,25:",
            logo_bottom,
            color=1,
            bold=True,
        )
        curses.echo()
        stdscr.attron(curses.color_pair(5))
        prompt = "Years: "
        stdscr.addstr(logo_bottom + 2, 4, prompt)
        years_raw = stdscr.getstr(logo_bottom + 2, 4 + len(prompt)).decode().strip()
        if not years_raw:
            years = ["23", "24", "25"]
        else:
            years = [y.strip() for y in years_raw.split(",") if y.strip()]
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
            "Enter paper numbers (e.g. 11,12) or leave blank for all:",
            logo_bottom + 4,
            color=1,
            bold=True,
        )
        curses.echo()
        stdscr.attron(curses.color_pair(5))
        prompt = "Paper Numbers: "
        stdscr.addstr(logo_bottom + 6, 4, prompt)
        paper_nums_raw = stdscr.getstr(logo_bottom + 6, 4 + len(prompt)).decode().replace(" ", "")
        stdscr.attroff(curses.color_pair(5))
        curses.noecho()
        break

    paper_numbers = [p.strip() for p in paper_nums_raw.split(",") if p.strip()] or None

    level_ui, level_slug = LEVELS[level_key]
    subject_name, subject_code, subject_slug = SUBJECTS[subject_key]
    paper_type = PAPER_TYPES[paper_key]

    session_codes = [SESSIONS[k][1] for k in session_keys]
    session_slugs = [SESSIONS[k][2] for k in session_keys]
    year_codes = [y.strip()[-2:] for y in years if y.strip()]

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
            f"Level: {level_ui.upper()}",
            f"Subject: {subject_name.title()}",
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
    def show_progress_bar(stdscr, total, current, y, width=40):
        percent = int((current / total) * 100) if total else 0
        filled = int(width * current // total) if total else 0
        bar = "[" + "#" * filled + "-" * (width - filled) + "]"
        stdscr.addstr(y, 4, f"{bar} {percent}% ({current}/{total})")

    def draw_log_panel(stdscr, start_y):
        height, width = stdscr.getmaxyx()
        log_dir = os.path.expanduser("~/pastpaper_logs")
        log_path = os.path.join(log_dir, "download_status.log")
        
        panel_y = start_y + 2
        if panel_y >= height - 2:
            return

        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(panel_y, 4, "--- BACKGROUND TASK MONITOR ---")
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)

        if not os.path.exists(log_path):
            stdscr.addstr(panel_y + 1, 6, "No activity yet...")
            return

        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
                # Show last 5-8 lines depending on space
                max_lines = min(height - panel_y - 4, 8)
                display_lines = lines[-max_lines:] if lines else []
                for i, line in enumerate(display_lines):
                    # Truncate if too long
                    msg = line.strip()
                    if len(msg) > width - 10:
                        msg = msg[:width-13] + "..."
                    stdscr.addstr(panel_y + 1 + i, 6, msg)
        except Exception:
            stdscr.addstr(panel_y + 1, 6, "Error reading logs")

    # Build download tasks
    from pastpaper.scraper import build_download_tasks, download_with_retry

    tasks = build_download_tasks(
        subject_code=subject_code,
        subject_slug=subject_slug,
        level_slug=level_slug,
        selected_type=paper_type,
        session_codes=session_codes,
        session_slugs=session_slugs,
        years=year_codes,
        paper_numbers=paper_numbers,
        out_dir=out_dir,
    )

    if not tasks:
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        center_text(stdscr, "No matching papers found!", logo_bottom, color=2, bold=True)
        center_text(stdscr, "Check your year/session/paper selection.", logo_bottom + 2)
        center_text(stdscr, "Press any key to exit.", logo_bottom + 4, color=3)
        stdscr.getch()
        curses.endwin()
        return

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
            stdscr.clear()
            stdscr.border()
            logo_bottom = draw_logo_centered(stdscr)
            center_text(stdscr, "Downloading...", logo_bottom, color=1, bold=True)
            
            y_bar = logo_bottom + 2
            y_status = logo_bottom + 4
            
            show_progress_bar(stdscr, total, i, y_bar)
            
            # Check if file already exists
            if os.path.exists(out_path):
                from pastpaper.scraper import log_download_status
                log_download_status(subject_slug, url, out_path, "SKIPPED")
                line = f"Skipping (exists): {os.path.basename(out_path)}"
            else:
                line = f"Processing {i}/{total}: {os.path.basename(out_path)}"
                
            height, width = stdscr.getmaxyx()
            if len(line) > width - 10:
                line = line[: width - 13] + "..."
            stdscr.addstr(y_status, 4, line)
            stdscr.refresh()
            
            if not os.path.exists(out_path):
                success = download_with_retry(url, out_path)
            
            # After each task, we refresh the view to show the log entry from scraper
            draw_log_panel(stdscr, y_status + 2)
            stdscr.refresh()
            time.sleep(0.05)
            
        stdscr.clear()
        stdscr.border()
        logo_bottom = draw_logo_centered(stdscr)
        center_text(stdscr, "Download Complete!", logo_bottom, color=3, bold=True)
        show_progress_bar(stdscr, total, total, logo_bottom + 2)
        draw_log_panel(stdscr, logo_bottom + 4)
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

import os

from pastpaper.scraper import scrape_subject
from pastpaper.subjects import LEVELS, PAPER_TYPES, SESSIONS, SUBJECTS
from pastpaper.utils import menu


def main():
    print("pastpaper downloader (cie)")

    level_choice = menu("select level:", LEVELS)
    if level_choice not in LEVELS:
        print("invalid level")
        return

    subject_choice = menu("select subject:", SUBJECTS)
    if subject_choice not in SUBJECTS:
        print("invalid subject")
        return

    session_choice = menu("select session:", SESSIONS)
    if session_choice not in SESSIONS:
        print("invalid session")
        return

    year = input("enter year (e.g. 2025): ").strip()
    if not year.isdigit() or len(year) != 4:
        print("invalid year")
        return

    session_name, session_code = SESSIONS[session_choice]
    year_code = year[-2:]

    paper_choice = menu("what to download:", PAPER_TYPES)
    if paper_choice not in PAPER_TYPES:
        print("invalid option")
        return

    level = LEVELS[level_choice]
    subject_name, subject_code = SUBJECTS[subject_choice]
    paper_type = PAPER_TYPES[paper_choice]

    print("\nstarting download...")

    base_out = os.path.join(os.getcwd(), "pastpaper", subject_name.replace(" ", "_"))

    scrape_subject(
        subject_code=subject_code,
        level=level,
        paper_type=paper_type,
        session_code=session_code,
        year_code=year_code,
        out_dir=base_out,
    )

    print("\ndownload complete.")


if __name__ == "__main__":
    main()

from pastpaper.subjects import LEVELS, PAPER_TYPES, SUBJECTS
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

    paper_choice = menu("what to download:", PAPER_TYPES)
    if paper_choice not in PAPER_TYPES:
        print("invalid option")
        return

    level = LEVELS[level_choice]
    subject_name, subject_code = SUBJECTS[subject_choice]
    paper_type = PAPER_TYPES[paper_choice]

    print("\nsummary")
    print("level:", level)
    print("subject:", subject_name, subject_code)
    print("papers:", paper_type)

    print("\n(download logic will be called here)")


if __name__ == "__main__":
    main()

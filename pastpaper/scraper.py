import os
import re
import time
from typing import Iterable, List

import requests
from tqdm import tqdm

BASE_URL = "https://pastpapers.co/cie"


def scrape_subject(
    subject_code: str,
    level: str,
    paper_type: str,
    session_code: str | List[str],
    year_code: str | List[str],
    out_dir: str,
    paper_numbers: Iterable[str] | None = None,
    retries: int = 3,
    timeout: int = 15,
):
    """
    subject_code: e.g. '9701'
    level: 'as' or 'a2'
    paper_type: 'qp', 'ms', or 'both'
    session_code: 'm' | 's' | 'w' OR list of them
    year_code: '25' OR list of them
    paper_numbers: ['11','12','13'] or None for all
    """

    if isinstance(session_code, str):
        session_code = [session_code]
    if isinstance(year_code, str):
        year_code = [year_code]

    os.makedirs(out_dir, exist_ok=True)

    tasks = build_download_tasks(
        subject_code,
        level,
        paper_type,
        session_code,
        year_code,
        paper_numbers,
    )

    if not tasks:
        print("no matching papers found")
        return

    with tqdm(tasks, desc="downloading", unit="file") as bar:
        for url, out_path in bar:
            if os.path.exists(out_path):
                bar.set_postfix_str("skipped")
                continue

            success = download_with_retry(
                url,
                out_path,
                retries=retries,
                timeout=timeout,
            )

            bar.set_postfix_str("ok" if success else "failed")


def build_download_tasks(
    subject_code: str,
    level: str,
    paper_type: str,
    sessions: List[str],
    years: List[str],
    paper_numbers: Iterable[str] | None,
):
    tasks = []

    for year in years:
        for session in sessions:
            prefix = f"{subject_code}_{session}{year}"

            if paper_type in ("qp", "both"):
                tasks += discover_files(
                    prefix,
                    "qp",
                    paper_numbers,
                )

            if paper_type in ("ms", "both"):
                tasks += discover_files(
                    prefix,
                    "ms",
                    paper_numbers,
                )

    return tasks


def discover_files(prefix, kind, paper_numbers):
    """
    Example file:
    9701_m25_qp_12.pdf
    """

    results = []

    for paper in paper_numbers or [
        "11",
        "12",
        "13",
        "21",
        "22",
        "23",
        "31",
        "32",
        "33",
    ]:
        filename = f"{prefix}_{kind}_{paper}.pdf"
        url = f"{BASE_URL}/{filename}"

        out_path = os.path.join(
            os.getcwd(),
            "pastpaper",
            prefix,
            kind,
            filename,
        )

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        results.append((url, out_path))

    return results


def download_with_retry(url, out_path, retries=3, timeout=15):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.content[:4] == b"%PDF":
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return True
        except requests.RequestException:
            pass

        time.sleep(1.5 * attempt)

    return False

import os
import time
from typing import Iterable, List

import requests
from tqdm import tqdm

BASE_API = "https://pastpapers.co/api/file"
BOARD = "caie"

SESSION_MAP = {
    "m": "March",
    "s": "May-June",
    "w": "Oct-Nov",
}

LEVEL_MAP = {
    "as": "A-Level",  # Both AS and A2 papers are under A-Level
    "a2": "A-Level",
}

# you can expand this later or move to subjects.py
SUBJECT_MAP = {
    "9701": "Chemistry-9701",
    "9702": "Physics-9702",
    "9709": "Mathematics-9709",
}


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
        out_dir,
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
    out_dir: str,
):
    tasks = []

    subject_slug = SUBJECT_MAP.get(subject_code)
    if not subject_slug:
        raise ValueError(f"unknown subject code: {subject_code}")

    level_name = LEVEL_MAP[level]

    for year in years:
        for session in sessions:
            session_name = SESSION_MAP[session]
            session_folder = f"20{year}-{session_name}"

            prefix = f"{subject_code}_{session}{year}"

            if paper_type in ("qp", "both"):
                tasks += discover_files(
                    subject_slug,
                    level_name,
                    session_folder,
                    prefix,
                    "qp",
                    paper_numbers,
                    out_dir,
                )

            if paper_type in ("ms", "both"):
                tasks += discover_files(
                    subject_slug,
                    level_name,
                    session_folder,
                    prefix,
                    "ms",
                    paper_numbers,
                    out_dir,
                )

    return tasks


def discover_files(
    subject_slug: str,
    level_name: str,
    session_folder: str,
    prefix: str,
    kind: str,
    paper_numbers: Iterable[str] | None,
    out_dir: str,
):
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

        url = (
            f"{BASE_API}/"
            f"{BOARD}/"
            f"{level_name}/"
            f"{subject_slug}/"
            f"{session_folder}/"
            f"{filename}"
            "?download=true"
        )

        out_path = os.path.join(
            out_dir,
            session_folder,
            kind,
            filename,
        )

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        results.append((url, out_path))

    return results


def download_with_retry(url, out_path, retries=3, timeout=60):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://pastpapers.co/",
        "Accept": "application/pdf,*/*",
    }

    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Downloading {url}")
            r = requests.get(url, headers=headers, timeout=timeout, stream=True)

            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)

                # sanity check
                with open(out_path, "rb") as f:
                    if f.read(4) == b"%PDF":
                        return True

                os.remove(out_path)
            else:
                print(f"Failed to download {url}: Status code {r.status_code}")

        except requests.Timeout:
            print(f"Timeout error for {url}")
        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")

        time.sleep(2 * attempt)

    return False

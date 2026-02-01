import os

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from pastpaper.utils import ensure_dir, sanitize_filename

BASE_URL = "https://pastpapers.co"

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def download_file(url, out_path):
    r = requests.get(url, headers=HEADERS, stream=True)
    r.raise_for_status()

    total = int(r.headers.get("content-length", 0))
    with (
        open(out_path, "wb") as f,
        tqdm(
            total=total, unit="B", unit_scale=True, desc=os.path.basename(out_path)
        ) as bar,
    ):
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))


def scrape_subject(subject_code, level, paper_type, out_dir):
    """
    level: as | a | both
    paper_type: qp | ms | both
    """

    ensure_dir(out_dir)

    url = f"{BASE_URL}/cie/{subject_code}"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    links = soup.select("a[href$='.pdf']")

    for a in links:
        href = a["href"]
        text = a.get_text(strip=True).lower()

        if level != "both" and level not in text:
            continue

        if paper_type == "qp" and "question" not in text:
            continue
        if paper_type == "ms" and "mark" not in text:
            continue

        pdf_url = href if href.startswith("http") else BASE_URL + href
        filename = sanitize_filename(os.path.basename(href))
        out_path = os.path.join(out_dir, filename)

        if os.path.exists(out_path):
            continue

        print(f"downloading {filename}")
        download_file(pdf_url, out_path)

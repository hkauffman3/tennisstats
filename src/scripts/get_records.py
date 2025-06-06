#!/usr/bin/env python3
import re
import sys
import os
import urllib.request
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import socket
from time import sleep

def extract_ratings(html_text):
    """
    Given the raw HTML of a TennisRecord profile page, extract:
      1) “Current Rating” + its “as of” date
      2) “Estimated Dynamic Rating” + its “as of” date

    Returns a tuple:
      (current_rating, current_rating_date, dynamic_rating, dynamic_rating_date)
    If any piece cannot be found, returns "N/A" for the missing parts.
    """
    current_pattern = re.compile(
        r'<td[^>]*>\s*<span[^>]*?font-weight:bold;?[^>]*>([^<]+)</span>\s*<br>\s*'
        r'<span[^>]*?>(\d{1,2}/\d{1,2}/\d{4})</span>',
        re.IGNORECASE
    )
    dynamic_pattern = re.compile(
        r'Estimated Dynamic Rating[\s\S]*?<span[^>]*?font-weight:bold;?[^>]*>\s*([^<]+?)\s*</span>\s*<br>\s*'
        r'<span[^>]*?>(\d{1,2}/\d{1,2}/\d{4})</span>',
        re.IGNORECASE
    )

    current_match = current_pattern.search(html_text)
    if current_match:
        current_rating = current_match.group(1).strip()
        current_date   = current_match.group(2).strip()
    else:
        current_rating = "N/A"
        current_date   = "N/A"

    dynamic_match = dynamic_pattern.search(html_text)
    if dynamic_match:
        dynamic_rating = dynamic_match.group(1).strip()
        dynamic_date   = dynamic_match.group(2).strip()
    else:
        dynamic_rating = "N/A"
        dynamic_date   = "N/A"

    return current_rating, current_date, dynamic_rating, dynamic_date


def fetch_page(url, timeout=30):
    """
    Fetch the given URL via urllib.request.
    On success, return decoded HTML as text.
    On failure (HTTPError, URLError, socket.timeout), return None.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Python urllib)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except (HTTPError, URLError, socket.timeout):
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 get_records.py INPUT_HTML [OUTPUT_HTML]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "tennis_with_ratings.html"

    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found.")
        sys.exit(1)

    # Read the entire input HTML
    with open(input_file, "r", encoding="utf-8") as f:
        html = f.read()

    # Extract all player names from <a> tags
    name_pattern = re.compile(r'<a [^>]*?>([^<]+)</a>', re.IGNORECASE)
    raw_names = name_pattern.findall(html)
    names = sorted({n.strip() for n in raw_names}, key=lambda x: x.split()[-1])

    total = len(names)
    base_url = "https://www.tennisrecord.com/adult/profile.aspx?playername="

    html_header = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>TennisRecord Player Links With Ratings</title>
</head>
<body>
  <h1>TennisRecord Player Links With Ratings</h1>
  <ul>
"""
    html_footer = """  </ul>
</body>
</html>
"""

    list_items = []
    for idx, name in enumerate(names, start=1):
        encoded_name = quote(name)
        profile_url = base_url + encoded_name

        print(f"[{idx}/{total}] Fetching “{name}” …", end=" ", flush=True)
        page_html = fetch_page(profile_url, timeout=30)
        if page_html is None:
            print("→ Page error; using N/A")
            current_rating = "N/A"
            current_date   = "N/A"
            dynamic_rating = "N/A"
            dynamic_date   = "N/A"
        else:
            current_rating, current_date, dynamic_rating, dynamic_date = extract_ratings(page_html)
            print(f"→ Current={current_rating} ({current_date}), Dynamic={dynamic_rating} ({dynamic_date})")

        list_items.append(
            f'    <li>\n'
            f'      <a href="{profile_url}" target="_blank">{name}</a>\n'
            f'      (Current Rating {current_rating} as of {current_date}  |  '
            f'Dynamic {dynamic_rating} as of {dynamic_date})\n'
            f'    </li>\n'
        )

        # Sleep to avoid hammering the site too quickly
        sleep(0.5)

    # Write output HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_header)
        f.write("".join(list_items))
        f.write(html_footer)

    print(f"\n✅ Done! Wrote '{output_file}' with {total} entries.")


if __name__ == "__main__":
    main()


import re
import sys
from urllib.parse import quote
import os

# Handle command-line arguments
if len(sys.argv) < 2:
    print("Usage: python generate_links.py input_file.html [output_file.html]")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2] if len(sys.argv) > 2 else "tennis_profiles_cleaned.html"

# Read the input HTML
if not os.path.exists(input_file):
    print(f"Error: File '{input_file}' does not exist.")
    sys.exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    html = f.read()

# Extract names from <a> tags
name_pattern = re.compile(r'<a [^>]*?>(.*?)</a>', re.IGNORECASE)
names = name_pattern.findall(html)

# Clean, deduplicate, sort
names = sorted(set(name.strip() for name in names), key=lambda x: x.split()[-1])

# Build output HTML
html_header = """<!DOCTYPE html>
<html>
<head>
  <title>TennisRecord Player Links</title>
</head>
<body>
  <h1>TennisRecord Player Links</h1>
  <ul>
"""

html_footer = """  </ul>
</body>
</html>
"""

base_url = "https://www.tennisrecord.com/adult/profile.aspx?playername="
list_items = ""

for name in names:
    encoded_name = quote(name)
    list_items += f'    <li><a href="{base_url}{encoded_name}" target="_blank">{name}</a></li>\n'

# Write output file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_header + list_items + html_footer)

print(f"✅ HTML written to '{output_file}' with {len(names)} player links.")

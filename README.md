# tennisstats

This repository contains a script that extracts TennisRecord ratings for players listed in a USTA team summary page.

## Usage

1. Save the USTA team summary (from the 'old' site) as a full HTML file (e.g. `team.html`).
2. Run the script with Python 3 and pass the saved HTML file:

```bash
python3 src/scripts/get_records.py team.html
```

To use a custom output path, supply a second argument:

```bash
python3 src/scripts/get_records.py team.html output.html
```

The script fetches rating data for each player and writes an HTML file (default `tennis_with_ratings.html`) containing the links and ratings.

### Download this page:
![USTA Team Page to Download](https://github.com/user-attachments/assets/9b7d536c-9d02-48dc-9c89-296d4133e178)

### output looks like this
![image](https://github.com/user-attachments/assets/0cc6fe8c-0c67-42d7-ba9f-80b3c664031a)


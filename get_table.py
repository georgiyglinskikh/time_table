import os  # For file operations
import re  # Regexp
from typing import *  # Strong typing

import pandas as pd # For reading excel files with time tables
import requests  # Web socket
from bs4 import BeautifulSoup  # HTML parser

# Constants
school = "http://xn--116-5cdozfc7ak5r.xn--80acgfbsl1azdqr.xn--p1ai"
tables = f"{school}/info/2245"
link_classes = "file xls"
span_classes = "caption"

# Get whole html file with tables
page = requests.get(tables)

# Parse it into soup
soup = BeautifulSoup(page.content, "html.parser")

# Get add links to tables
links = soup.find_all("a", {"class": link_classes}, limit=32)
spans = {
    el
        .findChild("span", {"class": span_classes}, recursive=False)
        .findChild("span", recursive=False)
    for el in links
}


def clear(x: str, chars: List[str]) -> str:
    """Remove all useless chars such as escape characters"""
    for char in chars:
        x.replace(char, "")
    return x


clear_chars = ["\n", "\r", "\t"]
urls = [clear(el["href"], clear_chars) for el in links]
names = [clear(el.text, clear_chars) for el in spans]

# Construct list of dictionaries with name and url properties
tables_info_unsorted = list(
    {"name": name, "url": url}
    for (name, url) in zip(names, urls)
)
tables_info = sorted(tables_info_unsorted, key=lambda x: x["name"])

date_format = r"(\d{2})\.(\d{2})"


def select_date(s: str) -> str:
    """Return all substrings that matches date_format"""
    return re.search(date_format, s).group(0)


# Read user input for date
print("Выбери дату: ")
for (i, dict_t) in enumerate(tables_info):
    name = dict_t["name"]
    print(f"{i}) {select_date(name)}")
table = tables_info[int(input("> "))]

# Download file for future reading
if not os.path.exists(table["name"]):
    table_xls = requests.get(table["url"], allow_redirects=True)  # Get from server
    open(table["name"], "wb").write(table_xls.content)  # Write it to the file

data_table = pd.read_excel(table["name"])

# TODO: Обработка таблиц с пользов. данными и с расписанием

# Remove table before finishing
os.remove(table["name"])

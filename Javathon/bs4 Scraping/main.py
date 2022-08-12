import requests

from bs4 import BeautifulSoup

req = requests.get("https://en.wikipedia.org/wiki/List_of_Java_bytecode_instructions")
soup = BeautifulSoup(req.text, 'html.parser')

data = []
table = soup.find('table')  # Get first table (this is really unreliable, but this is just temporary code)
table_body = table.find('tbody')

rows = table_body.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    # print(cols)
    for ele in cols:
        try:
            print(f"{cols[0]} = {int(cols[1], 16)}")
        finally:
            break
    # data.append([ele for ele in cols if ele])  # Get rid of empty values

print(data)

import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import json

df = pd.DataFrame(columns=["smybol", "name", "tradable"])
idx = 0

# The URL of the page you want to scrape
url = 'https://www.kap.org.tr/en/bist-sirketler'  # Replace with the actual URL

# Send a GET request to fetch the page content
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the div elements with the class 'comp-cell _04 vtable'
    company_cells = soup.find_all('div', class_='comp-cell _04 vtable')
    company_cells2 = soup.find_all('div', class_='comp-cell _14 vtable')
    
    # Loop through all found divs and extract the symbol
    company_symbols = []
    company_names = []
    for cell in company_cells:
        # Extract the text within the <a> tag
        symbol = cell.find('a').text.strip()

        company_symbols.append(symbol)
        # for sym in symbol.split(','):
        #     company_symbols.append(sym.strip())

    for cell in company_cells2:
        name = cell.find('a').text.strip()
        company_names.append(name)

    for symbol, name in zip(company_symbols, company_names):
        # print(f"{symbol}: {name}")
        for sym in symbol.split(','):
            # print(f"{sym.strip()}: {name}")
            df.loc[idx] = [sym.strip(), name, 0]
            idx += 1

    # Output the list of symbols
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    exit()

def verify_yfinance(df: pd.DataFrame) -> None:
    for idx in range(len(df)):
        print(f"Verifying {df.loc[idx, 'smybol']}...")

        if "previousClose" in yf.Ticker(f"{df.loc[idx, 'smybol']}.IS").info:
            df.loc[idx, 'tradable'] = 1
        else:
            df.loc[idx, 'tradable'] = -1

print("Verifying tradable companies...")
verify_yfinance(df)

df = df[df['tradable'] == 1].reset_index(drop=True).drop(columns=['tradable'])

df.to_csv("bist_companies/bist_companies.csv", index=False)

arr = [{"symbol": df.loc[idx, 'smybol'], "name": df.loc[idx, 'name']} for idx in range(len(df))]

with open("bist_companies/bist_companies.json", "w") as f:
    json.dump(arr, f, indent=4, ensure_ascii=False)

print("Done!")

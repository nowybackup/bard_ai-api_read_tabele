import urllib.request
import codecs
import time
import json
import re
import pandas as pd
import os
from typing import Optional
from enum import Enum

def delay_execution():
    time.sleep(1)

def send_request(url, headers, data):
    req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode('utf-8'), method='POST')
    with urllib.request.urlopen(req) as response:
        response_data = response.read().decode('utf-8')
        return json.loads(response_data)

def read_file(input_file):
    with codecs.open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()
    return lines

def prepare_requests(lines):
    requests = []
    for i in range(0, len(lines), 20):
        batch = lines[i:i+20]
        table = ', '.join(batch)
        query = f"find the stock market symbol based on the company name, correct the company name if possible, make a table: Company Name | Stock Market Symbol ({table})"
        requests.append(query)
    return requests

class RowNumberParam:
    """Parametry do filtrowania wierszy"""
    CONDITION_1 = "Condition_1"
    CONDITION_2 = "Condition_2"
    CONDITION_3 = "Condition_3"

def extract_table_data(text, start_column=None, end_column=None, start_row=2, end_row=None,
                       start_row_number=1, row_number_param=None):
    """
    Ekstrahuje dane z tabeli w formacie tekstowym i zwraca je jako sformatowaną tabelę.

    Parametry:
    - text (str): Tekst zawierający tabelę.
    - start_column (int): Indeks startowej kolumny (domyślnie: None).
    - end_column (int): Indeks końcowej kolumny (domyślnie: None).
    - start_row (int): Indeks startowego wiersza (domyślnie: 2).
    - end_row (int): Indeks końcowego wiersza (domyślnie: None).
    - start_row_number (int): Początkowy numer dla numeracji wierszy (domyślnie: 1).
    - row_number_param (str): Parametr do filtrowania wierszy, które mają być numerowane (domyślnie: None).

    Zwraca:
    - str: Dane tabeli jako sformatowana tabela.
    """
    start_row_number = start_row_number + count

    # Split the text into lines
    lines = text.strip().split("\n")

    # Find the start and end indices of the table
    table_start = None
    table_end = None
    
    # Dodaj instrukcję debugowania
    print("Szukanie początku i końca tabeli...")

    for i, line in enumerate(lines):
        if "|" in line:
            table_start = i
            break

    for i in range(len(lines) - 1, -1, -1):
        if "|" in lines[i]:
            table_end = i
            break

    if table_start is None or table_end is None:
        return "Nie znaleziono tabeli."
    
    # Dodaj instrukcję debugowania
    print("Początek tabeli:", table_start)
    print("Koniec tabeli:", table_end)

    # Extract the table content
    table_content = [line.strip() for line in lines[table_start:table_end + 1] if line.strip()]

    # Extract the column names from the header row
    header_row = table_content[0]
    columns = ["Numer wiersza"] + [col.strip() for col in header_row.split("|") if col.strip()]

    # Determine the start and end column indices
    if start_column is None:
        start_column = 1

    if end_column is None:
        end_column = len(columns)

    # Determine the start and end row indices
    if start_row is None:
        start_row = 2

    if end_row is None:
        end_row = len(table_content)

    # Validate the start and end row/column indices
    start_row = max(1, start_row)  # Upewnij się, że start_row wynosi co najmniej 1
    start_col = max(1, start_column)  # Upewnij się, że start_col wynosi co najmniej 1
    end_row = min(end_row, len(table_content))  # Upewnij się, że end_row jest w zakresie tabeli
    end_col = min(end_column, len(columns))  # Upewnij się, że end_col jest w zakresie tabeli

    # Extract the specified range of rows and columns
    rows_range = table_content[start_row - 1:end_row]
    cols_range = columns[start_col - 1:end_col]

    # Initialize an empty list to store the filtered rows
    filtered_rows = []

    # Iterate over the rows and filter out the rows without stock market symbols
    for i, row in enumerate(rows_range, start=start_row_number):
        values = [str(i)] + [value.strip() for value in row.split("|") if value.strip()]

        # Create a dictionary mapping column names to values
        row_data = dict(zip(cols_range, values))

        # Check if the row meets the condition for row numbering
        if row_number_param is not None and row_number_param in row_data:
            filtered_rows.append(row_data)
        elif row_number_param is None:
            filtered_rows.append(row_data)

    # Create a pandas DataFrame from the filtered rows
    df = pd.DataFrame(filtered_rows)

    # Return the DataFrame as a formatted table
    return df.to_string(index=False)



def usun_gorny_wiersz(tekst):
    linie = tekst.split('\n')
    if len(linie) < 2:
        return ''

    linie = linie[2:]
    tekst_bez_gornego_wiersza = '\n'.join(linie)

    return tekst_bez_gornego_wiersza

def filter_response(response):

    part_1 = response['choices'][0]['content'][0]
    part_2 = response['choices'][1]['content'][0]
    part_3 = response['choices'][2]['content'][0]

    print("Podzielono odpowiedź na części: ")

    part_1 = extract_table_data(part_1)
    part_2 = extract_table_data(part_2)
    part_3 = extract_table_data(part_3)

    part_1 = usun_gorny_wiersz(part_1)
    part_2 = usun_gorny_wiersz(part_2)
    part_3 = usun_gorny_wiersz(part_3)

    return part_1, part_2, part_3

def save_to_file(data, output_file):
    if isinstance(data, list):
        data = '\n'.join(data)

    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(data + '\n')

# Przykładowe użycie:
input_file =  'input.txt'
output_file_0 = 'output_0.txt'
output_file_1 = 'output_1.txt'
output_file_2 = 'output_2.txt'

url = "http://localhost:8000/ask"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

data = {
    "session_id": "YAgBB_5wpl2eyclUfKIvEszH3sA6KKOexSbMG-Mrvu3lE-BMfCaMjLM5RyNOqDiXBsNvjw.", # cooke  __Secure-1PSID
    "message": ""
}

lines = read_file(input_file)
chunk_size = 20  # ilość lini czytanych na zapytanie
count = 0

for count in range(0, len(lines), chunk_size):
    chunk = lines[count:count+chunk_size]  # Odczytaj kolejny fragment pliku
    requests = prepare_requests(chunk)
    print("Przetwarzanie linii:", count+1, "-", min(count+chunk_size, len(lines)))
    retry_chunk = []  # Przechowuje linie do ponownego przetwarzania

    for line, query in zip(chunk, requests):
        while True:
            try:
                if retry_chunk:
                    # Ponowne przetwarzanie linii, które wymagały ponownej próby
                    data["message"] = retry_chunk.pop(0)
                else:
                    data["message"] = query

                print("Odczytano plik: ")
                print("Przygotowano zapytanie: ")
                print("Wysłano zapytanie do API: ")
                response = send_request(url, headers, data)
                print("Otrzymano odpowiedź: ")
                part_1, part_2, part_3 = filter_response(response)
                print("Przefiltrowano dane do zapisu w pliku: ")
                save_to_file(part_1, output_file_0)
                print("Zapisano w pliku 1: ")
                save_to_file(part_2, output_file_1)
                print("Zapisano w pliku 2: ")
                save_to_file(part_3, output_file_2)
                print("Zapisano w pliku 3: ")
                break  # Wyjście z pętli while w przypadku sukcesu
            except Exception as e:
                print("Wystąpił błąd sieci:", str(e))
                print("Ponowne próbowanie...")
                retry_chunk = chunk[chunk.index(line):]  # Przetwarzaj linie od błędnej linii do końca fragmentu

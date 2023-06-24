import urllib.request
import codecs
import time
import json
import sys
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

def find_table_indices(lines):
    """Znajduje indeksy początku i końca tabeli w tekście.

    Parametry:
    - lines (List[str]): Lista linii tekstu.

    Zwraca:
    - Tuple[Optional[int], Optional[int]]: Indeks początku i końca tabeli lub None, jeśli tabela nie została znaleziona.
    """
    table_start = None
    table_end = None

    for i, line in enumerate(lines):
        if "|" in line:
            table_start = i
            break

    for i in range(len(lines) - 1, -1, -1):
        if "|" in lines[i]:
            table_end = i
            break

    return table_start, table_end

def extract_table_content(lines, table_start, table_end):
    """Ekstrahuje zawartość tabeli z listy linii tekstu.

    Parametry:
    - lines (List[str]): Lista linii tekstu.
    - table_start (Optional[int]): Indeks początku tabeli.
    - table_end (Optional[int]): Indeks końca tabeli.

    Zwraca:
    - List[str]: Lista linii zawierających treść tabeli.
    """
    if table_start is None or table_end is None:
        return []

    table_content = [line.strip() for line in lines[table_start:table_end + 1] if line.strip()]
    return table_content

def extract_columns(header_row):
    """
    Ekstrahuje nazwy kolumn z wiersza nagłówka.

    Parametry:
    - header_row (str): Wiersz nagłówka.

    Zwraca:
    - list: Lista nazw kolumn.
    """
    columns = ["Numer wiersza"] + [col.strip() for col in header_row.split("|") if col.strip()]
    return columns


def extract_rows_range(table_content, start_row, end_row):
    """
    Ekstrahuje zakres wierszy z zawartości tabeli.

    Parametry:
    - table_content (list): Lista zawartości tabeli.
    - start_row (int): Indeks startowego wiersza.
    - end_row (int): Indeks końcowego wiersza.

    Zwraca:
    - list: Zakres wierszy.
    """
    start_row = max(1, start_row)
    end_row = min(end_row, len(table_content))
    rows_range = table_content[start_row - 1:end_row]
    return rows_range


def filter_rows(rows_range, start_row_number, row_number_param, columns):
    """
    Filtruje wiersze, uwzględniając numerację i parametr `row_number_param`.

    Parametry:
    - rows_range (list): Zakres wierszy.
    - start_row_number (int): Początkowy numer dla numeracji wierszy.
    - row_number_param (str): Parametr do filtrowania wierszy, które mają być numerowane.
    - columns (list): Lista nazw kolumn.

    Zwraca:
    - list: Przefiltrowane wiersze.
    """
    filtered_rows = []

    for i, row in enumerate(rows_range, start=start_row_number):
        values = [str(i)] + [value.strip() for value in row.split("|") if value.strip()]
        row_data = dict(zip(columns, values))

        if row_number_param is not None and row_number_param in row_data:
            filtered_rows.append(row_data)
        elif row_number_param is None:
            filtered_rows.append(row_data)

    return filtered_rows

def create_dataframe(filtered_rows, columns):
    """
    Tworzy obiekt DataFrame na podstawie przefiltrowanych wierszy i nazw kolumn.

    Parametry:
    - filtered_rows (list): Przefiltrowane wiersze.
    - columns (list): Lista nazw kolumn.

    Zwraca:
    - DataFrame: Obiekt DataFrame.
    """
    df = pd.DataFrame(filtered_rows, columns=columns)
    return df

def format_table(df):
    """
    Formatuje DataFrame jako sformatowaną tabelę.

    Parametry:
    - df (DataFrame): Obiekt DataFrame.

    Zwraca:
    - str: Sformatowana tabela.
    """
    return df.to_string(index=False)

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
    table_start, table_end = find_table_indices(lines)

    if table_start is None or table_end is None:
        return "Nie znaleziono tabeli."

    # Extract the table content
    table_content = extract_table_content(lines, table_start, table_end)

    if not table_content:
        return "Nie znaleziono tabeli."

    columns = extract_columns(table_content[0])
    rows_range = extract_rows_range(table_content, start_row, end_row)
    filtered_rows = filter_rows(rows_range, start_row_number, row_number_param, columns)
    df = create_dataframe(filtered_rows, columns)

    return format_table(df)

def usun_gorny_wiersz(tekst):
    linie = tekst.split('\n')
    if len(linie) < 2:
        return ''

    linie = linie[2:]
    tekst_bez_gornego_wiersza = '\n'.join(linie)

    return tekst_bez_gornego_wiersza

def filter_response(response):

    print(response)

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
            except IOError as e:
                print("Wystąpił błąd wejścia-wyjścia (IO):", str(e))
                # Dodatkowe informacje o błędzie IO
                print("Blad: ", e.errno)
                print("Opis błędu: ", e.strerror)
                print("Ścieżka pliku: ", e.filename)
                print("Ponowne próbowanie...")
                retry_chunk = chunk[chunk.index(line):]  # Przetwarzaj linie od błędnej linii do końca fragmentu
            except ValueError as e:
                print("Wystąpił błąd wartości:", str(e))
                # Dodatkowe informacje o błędzie wartości
                print("Wartość nieprawidłowa:", e.args[0])
                print("Ponowne próbowanie...")
                retry_chunk = chunk[chunk.index(line):]  # Przetwarzaj linie od błędnej linii do końca fragmentu
            except KeyError as e:
                print("Wystąpił błąd klucza (KeyError):", str(e))
                # Dodatkowe informacje o błędzie KeyError
                print("Nieznany klucz:", e.args[0])
                print("Google Bard encountered an error: n38")
                print("Ścieżka błędu:", sys.exc_info()[2].tb_frame.f_code.co_filename)
                print("Linia błędu:", sys.exc_info()[2].tb_lineno)
                print("Ponowne próbowanie...")
                retry_chunk = chunk[chunk.index(line):]  # Przetwarzaj linie od błędnej linii do końca fragmentu
            except Exception as e:
                print("Wystąpił nieznany błąd:", str(e))
                # Dodatkowe informacje o ogólnym błędzie
                print("Typ błędu:", type(e).__name__)
                print("Ponowne próbowanie...")
                retry_chunk = chunk[chunk.index(line):]  # Przetwarzaj linie od błędnej linii do końca fragmentu

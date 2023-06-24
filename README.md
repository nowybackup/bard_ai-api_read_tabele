# bard_ai-api_read_tabele
This script is used with repository "google-bard-api" and have read table in parts for sheets

You need take and install repository google-bard-api
</br>
The request </br>
<code> def prepare_requests(lines):
    requests = []
    for i in range(0, len(lines), 20):
        batch = lines[i:i+20]
        table = ', '.join(batch)
        query = f"example, make a table: Company Name | Stock Market Symbol ({table})"
        requests.append(query)
    return requests </code>
</br>
Cut response on parts</br>
<code>
def filter_response(response):
    part_1 = response['choices'][0]['content'][0]
    part_2 = response['choices'][1]['content'][0]
    part_3 = response['choices'][2]['content'][0]
</code> </br>
Prepare table 
<code> </br>
def extract_table_data(text, start_column=None, end_column=None, start_row=2, end_row=None,
                       start_row_number=1, row_number_param=None):
</code> 
Option: </br>
<code>"""Extracts data from a table in text format and returns it as a formatted table.
Parameters:
text (str): Text containing the table.
start_column (int): Index of the starting column (default: None).
end_column (int): Index of the ending column (default: None).
start_row (int): Index of the starting row (default: 2).
end_row (int): Index of the ending row (default: None).
start_row_number (int): Starting number for row numbering (default: 1).
row_number_param (str): Parameter to filter rows to be numbered (default: None).
Returns:
str: Table data as a formatted table.
"""</code></br>
Save to file</br>
<code> def save_to_file(data, output_file):
    if isinstance(data, list):
        data = '\n'.join(data)
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(data + '\n')</code>
        
Errors Problems is with connetion with API Bard, I have error: Networ error: 'choices'

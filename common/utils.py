import csv

def read_and_sort_csv(file_name, column_index, as_number=False):
    with open(file_name, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        data = list(reader)
        
    # Sort the data based on the 'steam_id' column (assuming it's the first column)
    if as_number:
        data.sort(key=lambda row: int(row[column_index]))
    else:
        data.sort(key=lambda row: row[column_index])
    
    # Write the sorted data back into the CSV file
    with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(data)

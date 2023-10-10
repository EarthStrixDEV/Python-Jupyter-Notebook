import requests
from concurrent.futures import ThreadPoolExecutor
import os

url_input = input("Enter the URL: ")
url = url_input.split('?')[0] if url_input.count('?') > 1 else url_input
print(url)
num_threads = 4  # Number of threads for concurrent downloads

# Step 1: Download the Large File with Split Downloads
def download_chunk(start, end, url, chunk_number):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)

    with open(f'chunk_{chunk_number}', 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

response = requests.head(url)
file_size = int(response.headers['content-length'])

chunk_size = file_size // num_threads

ranges = [(i * chunk_size, min((i + 1) * chunk_size - 1, file_size - 1)) for i in range(num_threads)]

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(lambda args: download_chunk(*args, url, args[2]), [(start, end, i) for i, (start, end) in enumerate(ranges)])

# Step 2: Combine the Files
def combine_files(chunk_prefix, output_file):
    with open(output_file, 'wb') as output_f:
        chunk_number = 0
        while True:
            try:
                with open(f'{chunk_prefix}_{chunk_number}', 'rb') as chunk_f:
                    chunk = chunk_f.read()
                    if not chunk:
                        break
                    output_f.write(chunk)
                chunk_number += 1
            except FileNotFoundError:
                break

chunk_prefix = 'chunk'  # Prefix used while splitting
output_file = 'combined_file.zip'  # Specify the desired output file name

combine_files(chunk_prefix, output_file)

# Step 3: Clean Up Split Files
def clean_up_chunks(chunk_prefix):
    for file_name in os.listdir():
        if file_name.startswith(chunk_prefix):
            os.remove(file_name)

clean_up_chunks(chunk_prefix)  # Clean up files with prefix 'chunk'

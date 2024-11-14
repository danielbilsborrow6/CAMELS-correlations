# import os
# import requests
# import h5py
# from tqdm import tqdm

# def download_file(url, save_path):
#     response = requests.get(url, stream=True)
#     total_size = int(response.headers.get('content-length', 0))  # Get the total file size in bytes
#     chunk_size = 8192  # Size of each chunk to be read at a time (8 KB)

#     if response.status_code == 200:
#         with open(save_path, 'wb') as file, tqdm(
#             desc="Downloading",
#             total=total_size,
#             unit='B',
#             unit_scale=True,
#             unit_divisor=1024,
#         ) as progress_bar:
#             for chunk in response.iter_content(chunk_size=chunk_size):
#                 if chunk:  # filter out keep-alive new chunks
#                     file.write(chunk)
#                     progress_bar.update(len(chunk))
#         print(f"\nDownload completed: {save_path}")
#     else:
#         print(f"Failed to download: {url}")

# def extract_coordinates(original_file, new_file):
#     with h5py.File(original_file, 'r') as f:
#         pos_dm = f['PartType1/Coordinates'][:]/1e3  # Extract coordinates and scale

#     # Save the extracted data to a new .hdf5 file
#     with h5py.File(new_file, 'w') as new_f:
#         new_f.create_dataset('PartType1/Coordinates', data=pos_dm)
#     print(f"Saved coordinates to: {new_file}")
    
#     # Delete the large file after extraction
#     os.remove(original_file)

# filenum = 26

# if __name__ == "__main__":
#     save_directory = "/Users/danie/CAMELS DATA"
#     url = f"https://users.flatironinstitute.org/~camels/Sims/IllustrisTNG/LH/LH_{filenum}/snapshot_090.hdf5"
#     original_file_name = f"LH{filenum}_snap_090IllustrisTNG.hdf5"
#     save_path = os.path.join(save_directory, original_file_name)
#     coordinates_file_name = f"LH{filenum}_coordinates.hdf5"
#     coordinates_path = os.path.join(save_directory, coordinates_file_name)

#     # Ensure the save directory exists
#     if not os.path.exists(save_directory):
#         os.makedirs(save_directory)

#     # Download the original large file
#     download_file(url, save_path)

#     # Extract and save only the coordinates
#     extract_coordinates(save_path, coordinates_path)

#     print(f"Done {filenum}")

import os
import requests
import h5py
import concurrent.futures

def download_chunk(url, start, end, chunk_num, save_directory):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code in (200, 206):  # 206 means partial content
        chunk_path = os.path.join(save_directory, f"chunk_{chunk_num}")
        with open(chunk_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded chunk {chunk_num}")
    else:
        print(f"Failed to download chunk {chunk_num}")

def download_file_in_chunks(url, save_path, chunk_size=10*1024*1024):
    # Get file size from server
    response = requests.head(url)
    file_size = int(response.headers.get('content-length', 0))
    print(f"Total file size: {file_size / (1024 * 1024):.2f} MB")

    # Define download folder and split the download into chunks
    save_directory = os.path.dirname(save_path)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    num_chunks = file_size // chunk_size + (1 if file_size % chunk_size != 0 else 0)

    # Download each chunk in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(download_chunk, url, i * chunk_size, min((i + 1) * chunk_size - 1, file_size - 1), i, save_directory)
            for i in range(num_chunks)
        ]
        concurrent.futures.wait(futures)

    # Combine chunks into a single file
    with open(save_path, 'wb') as file:
        for i in range(num_chunks):
            chunk_path = os.path.join(save_directory, f"chunk_{i}")
            with open(chunk_path, 'rb') as chunk_file:
                file.write(chunk_file.read())
            os.remove(chunk_path)
    print(f"Download completed: {save_path}")

def extract_coordinates(original_file, new_file):
    with h5py.File(original_file, 'r') as f:
        pos_dm = f['PartType1/Coordinates'][:]/1e3  # Extract coordinates and scale

    # Save the extracted data to a new .hdf5 file
    with h5py.File(new_file, 'w') as new_f:
        new_f.create_dataset('PartType1/Coordinates', data=pos_dm)
    print(f"Saved coordinates to: {new_file}")

    # Delete the large file after extraction
    os.remove(original_file)
    print(f"Deleted original file: {original_file}")

if __name__ == "__main__":
    filenum = 47
    save_directory = "/Users/danie/CAMELS DATA"
    url = f"https://users.flatironinstitute.org/~camels/Sims/IllustrisTNG/LH/LH_{filenum}/snapshot_090.hdf5"
    original_file_name = f"LH{filenum}_snap_090IllustrisTNG.hdf5"
    save_path = os.path.join(save_directory, original_file_name)
    coordinates_file_name = f"LH{filenum}_coordinates.hdf5"
    coordinates_path = os.path.join(save_directory, coordinates_file_name)

    # Download the original large file in chunks
    download_file_in_chunks(url, save_path)

    # Extract and save only the coordinates, then delete the full file
    extract_coordinates(save_path, coordinates_path)

    print(f"Done {filenum}")


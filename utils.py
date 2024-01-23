import taufactor as tau
from taufactor.metrics import volume_fraction
from taufactor.metrics import surface_area
from taufactor.metrics import triple_phase_boundary
import tifffile
import torch
import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from email.parser import HeaderParser
import zipfile
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow


def tau_factor(query_img):
    try:
        print("----------------------------------------")
        print("Function calling...")
        print("----------------------------------------")

        # Read the image file
        img = tifffile.imread(query_img)

        # Create a solver object with the loaded image
        s = tau.Solver(img)

        # Calculate volume fraction and surface area
        vf = volume_fraction(img)
        sa = surface_area(img, phases=[1])

        # Solve for D_eff and tau
        s.solve()

        # Extract values from tensors or convert to list if more than one element
        D_eff_value = s.D_eff.item() if s.D_eff.numel() == 1 else s.D_eff.tolist()
        tau_value = s.tau.item() if s.tau.numel() == 1 else s.tau.tolist()
        surface_area_value = sa.item() if sa.numel() == 1 else sa.tolist()
        volume_fraction_value = vf

        # Construct and return a JSON object containing all results
        results = {
            "Microstructure": query_img.split('/')[-1],
            "Effective Diffusivity": D_eff_value,
            "Tau": tau_value,
            "Volume Fraction": volume_fraction_value,
            "Surface Area": surface_area_value
        }
        return json.dumps(results)

    except Exception as e:
        # If processing fails, return a JSON object with an error message
        error = {"Microstructure": query_img.split('/')[-1],
                 "Error": f"Cannot process image: {e}"}
        return json.dumps(error)



def extract_image_paths(directory):
    
    """
    Function to extract image paths from a given directory and generate a sentence listing these paths.

    :param directory: The local directory to search for image files (e.g., './3DvoxelImage').
    :return: Tuple containing the path to the output text file with image paths and a sentence listing these paths.
    """
    # Define the image extensions to search for (assuming TIFF format)
    image_extensions = {'.tif', '.tiff'}

    image_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(tuple(image_extensions)):
                # Construct the path with './directory_name/' format
                image_path = os.path.join(directory, file)
                image_paths.append(image_path)

    # Write the image paths to a text file
    output_file_path = os.path.join('.', 'image_paths.txt')
    with open(output_file_path, 'w') as file:
        for path in image_paths:
            file.write(f"{path}\n")

    # Construct a sentence with all image paths
    image_path = "Please help me analyze these images. These are the images' path: " + ", ".join(f"'{path}'" for path in image_paths)

    return output_file_path, image_path

def search_zenodo_datasets(query, access_token='Ge', max_results=10):
    # API search URL
    url = f"https://zenodo.org/api/records/?q={query}&type=dataset"

    # Set request headers, including the authentication token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Send GET request
    response = requests.get(url, headers=headers)

    # Check response status
    if response.status_code == 200:
        # Parse response data
        data = response.json()

        # Extract and return the most relevant results
        return [item['links']['self_html'] for item in data['hits']['hits'][:max_results]]
    else:
        # Return error message in case of an error
        return f"Error: {response.status_code}"

import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import nbformat as nbf

def create_and_execute_python_file(code, output_filename='created_script.py'):
    """
    Create a Python script file with the provided code and execute it upon user's consent.
    If the script cannot be executed, it will return an error message instead of crashing.
    
    :param code: String containing the code to be included in the script.
    :param output_filename: Filename for the created Python script.
    :return: None
    """
    # Save the code as a .py file
    with open(output_filename, 'w') as file:
        file.write(code)
    print(f"Python script saved as {output_filename}")

    # Ask user for permission to execute the script
    consent = input("Do you want to execute the script? (yes/no): ")
    if consent.lower() == 'yes':
        try:
            # Attempt to execute the script
            exec(open(output_filename).read())
            return "Script executed successfully."
        except Exception as e:
            return f"Script could not be executed due to an error: {e}"
    else:
        return "Script execution aborted by user."



def download_links_and_download_files(page_url):
    """
    Accesses a specified webpage, searches for all links that contain the word 'download',
    and prompts the user whether to download each found file. If the user agrees, the function
    downloads the file and saves it locally.

    :param page_url: URL of the web page to search for download links.
    
    """
    
    def find_download_links(url):
        response = requests.get(url)
        if response.status_code != 200:
            return f"Unable to access the page. Status code: {response.status_code}"
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        return set(urljoin(url, link['href']) for link in links if 'download' in link['href'])

    def download_file(url, default_filename):
        response = requests.get(url, stream=True)
        # try to get filename from Content-Disposition header
        content_disp = response.headers.get('content-disposition')
        if content_disp:
            header_parser = HeaderParser()
            headers = header_parser.parsestr('Content-Disposition: ' + content_disp)
            filename = headers.get_filename()
            if filename:
                filename = unquote(filename)
        else:
            # if Content-Disposition header is not present, try to get filename from URL
            filename = default_filename or urlparse(url).path.split('/')[-1]

        if not filename:
            # if filename is not present in URL, use default filename
            filename = 'downloaded_file'

        # download file
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded: {filename}")
        return filename

    download_links = find_download_links(page_url)

    if not download_links:
        return "No download links found"
    
    downloaded_files = []
    for link in download_links:
        answer = input(f"Do you want to download the file from {link}? (yes/no): ")
        if answer.lower() == 'yes':
            filename = link.split('/')[-1]
            down_load_filename = download_file(link, filename)
            # upload_google_drive(down_load_filename)
            downloaded_files.append(down_load_filename)

    if downloaded_files:
        return f"Downloaded files: {', '.join(downloaded_files)}"
    else:
        return "No files downloaded"
    

def extract_and_organize_files(zip_file_path, output_folder, file_extension):
    # Check if the file is a ZIP format
    if not zip_file_path.endswith('.zip'):
        print("The file is not a ZIP archive.")
        return

    # Unzip the ZIP file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall("extracted")

    # Create a new folder to store files of the specified format
    os.makedirs(output_folder, exist_ok=True)

    # Search for all files of the specified format in the extracted folder
    for root, dirs, files in os.walk("extracted"):
        for file in files:
            if file.lower().endswith('.' + file_extension):
                source_file = os.path.join(root, file)
                shutil.copy(source_file, output_folder)

    print(f"All {file_extension.upper()} files have been copied to {output_folder}")

import csv
def read_file(file_path):
    """
    Reads a file and returns its contents based on the file extension.

    :param file_path: str, the path to the file.
    :return: Depending on the file extension:
             - list of lists for CSV files,
             - string for Python files,
             - error message if the file cannot be processed or the type is unsupported.
    """
    # Determine the file extension
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    try:
        if file_extension == '.csv':
            content = []
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    content.append(row)
            return content

        elif file_extension == '.py':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()

        else:
            return f"Unsupported file type: {file_extension}"

    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"


def upload_google_drive(upload_filename, folder_id='18rx0j7qYvW_5Hhyu84alYhcQdWLqRXRa', credentials_file='credentials.json'):
    """
    Uploads a file to a specific Google Drive folder and returns the link to the uploaded file.
    
    :param upload_filename: Name of the file to upload.
    :param folder_id: ID of the Google Drive folder where the file will be uploaded (default is specified).
    :param credentials_file: Path to the JSON file with Google Drive API credentials (default 'credentials.json').
    :return: A message indicating successful upload and a link to the uploaded file.
    """

    # Load credentials and create a Google Drive API service
    creds = None
    with open(credentials_file, 'r') as file:
        creds_json = json.load(file)['installed']
        flow = InstalledAppFlow.from_client_config({'installed': creds_json}, ['https://www.googleapis.com/auth/drive'])
        creds = flow.run_local_server(port=8080)

    service = build('drive', 'v3', credentials=creds)

    # Upload the file to the specified Google Drive folder
    file_metadata = {
        'name': upload_filename,
        'parents': [folder_id]  # Add the parent folder ID
    }
    media = MediaFileUpload(upload_filename, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Generate a link to the uploaded file
    file_id = file.get('id')
    file_link = f"https://drive.google.com/file/d/{file_id}/view"

    return f"'{upload_filename}' is uploaded to Google Drive. Its file id is {file_id}. Link to the file: {file_link}"


def find_json(file_or_dir_path):
    """
    Searches a zip file or a directory for JSON files.
    Asks the user to confirm if a found JSON file is the metadata file.
    If confirmed, lists the keys of the JSON structure and asks the user which parts to extract.
    Returns the contents of the selected parts for all items in the JSON file.

    :param file_or_dir_path: Path to the zip file or directory.
    :return: The contents of the selected parts of the JSON file or a message if not found.
    """
    def is_non_empty_file(fpath):  
        return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

    def extract_selected_data(json_content, keys_to_extract):
        extracted_data = {}
        for item_id, item_data in json_content.items():
            extracted_data[item_id] = {key: item_data[key] for key in keys_to_extract if key in item_data}
        return extracted_data

    def search_metadata(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json') and is_non_empty_file(os.path.join(root, file)):
                    file_path = os.path.join(root, file)
                    user_confirm = input(f"Found file: {file}. Is this the metadata file? (yes/no): ").lower()
                    if user_confirm == 'yes':
                        with open(file_path, 'r') as metadata_file:
                            try:
                                json_content = json.load(metadata_file)
                                first_item = next(iter(json_content.values()))
                                if isinstance(first_item, dict):
                                    keys = list(first_item.keys())
                                    print("JSON file contains items with the following fields:")
                                    print("\n".join(keys))
                                    user_keys = input("Enter the fields you want to extract (separated by commas): ")
                                    selected_keys = [key.strip() for key in user_keys.split(',')]
                                    return extract_selected_data(json_content, selected_keys)
                                else:
                                    return "JSON file does not contain a valid structure."
                            except json.JSONDecodeError:
                                return "Invalid JSON format in file."

        return "No metadata found."

    if zipfile.is_zipfile(file_or_dir_path):
        with zipfile.ZipFile(file_or_dir_path, 'r') as zip_ref:
            zip_ref.extractall("temp_unzip_folder")
        result = search_metadata("temp_unzip_folder")
    else:
        result = search_metadata(file_or_dir_path)

    return result if result else "No metadata found."


def extract_files_from_folder_or_zip(source_path, target_filename, destination_folder='DATA'):
    """
    Extracts files with the specified name from a given folder or zip file,
    including any nested folders and zip files within. For zip files, the function
    extracts only the target files directly to the destination folder, without preserving
    any of the original folder structure.

    :param source_path: Path to the source folder or zip file.
    :param target_filename: Name of the file to search for and extract.
    :param destination_folder: Folder where the extracted files will be stored.
    """
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    def search_and_extract_from_zip(zip_path):
        """ Search and extract matching files from the given zip file. """
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith(target_filename):
                    # Extract file directly to the destination folder without the original folder structure
                    target_file = zip_ref.open(file)
                    destination_file_path = os.path.join(destination_folder, os.path.basename(file))
                    with open(destination_file_path, 'wb') as f:
                        shutil.copyfileobj(target_file, f)
                elif file.endswith('.zip'):
                    # Temporarily extract nested zip file to a temp folder
                    temp_folder = os.path.join(destination_folder, 'temp_zip_extraction')
                    os.makedirs(temp_folder, exist_ok=True)
                    zip_ref.extract(file, temp_folder)
                    nested_zip_path = os.path.join(temp_folder, file)
                    search_and_extract_from_zip(nested_zip_path)
                    # Clean up the temp folder
                    shutil.rmtree(temp_folder)

    def search_and_extract_from_folder(folder_path):
        """ Search and extract matching files from the given folder. """
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file == target_filename:
                    # Copy file directly to the destination folder
                    shutil.copy2(os.path.join(root, file), destination_folder)
                elif file.endswith('.zip'):
                    # Search within nested zip file
                    search_and_extract_from_zip(os.path.join(root, file))

    if os.path.isfile(source_path) and source_path.endswith('.zip'):
        # Source is a zip file
        search_and_extract_from_zip(source_path)
    elif os.path.isdir(source_path):
        # Source is a folder
        search_and_extract_from_folder(source_path)

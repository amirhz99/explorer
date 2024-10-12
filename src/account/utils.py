import zipfile
import os
from typing import Dict

# Extract the ZIP and return a list of extracted files
def extract_zip(zip_path: str, extract_to: str) -> Dict[str, str]:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    # Create a map of sessions and JSON files based on matching names
    extracted_files = {}
    for filename in os.listdir(extract_to):
        name, ext = os.path.splitext(filename)
        if name not in extracted_files:
            extracted_files[name] = {}
        if ext == ".session":
            extracted_files[name]["session"] = os.path.join(extract_to, filename)
        elif ext == ".json":
            extracted_files[name]["json"] = os.path.join(extract_to, filename)
    
    return extracted_files
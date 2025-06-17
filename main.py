# Import required modules
import http.client  # For making low-level HTTP requests
import json  # For parsing and generating JSON data
import os  # For interacting with the operating system (file operations)
import requests  # For making HTTP requests easily
import re  # For regular expressions (used in sanitizing filenames)
import urllib.parse  # For parsing and unquoting URLs


# Check if a file exists at the given system path
def check_file_exists(system_path: str) -> bool:
    return os.path.isfile(path=system_path)


# Append the given content to a file at the specified path
def append_write_to_file(system_path: str, content: str) -> None:
    file = open(file=system_path, mode="a")  # Open file in append mode
    file.write(content)  # Write the content to the file
    file.close()  # Close the file


# Send a POST request to the API to fetch SDS document data for the given page
def getDataFromAPI(page: int) -> str:
    conn = http.client.HTTPSConnection(
        host="api.cytivalifesciences.com"
    )  # Create HTTPS connection
    payload: str = json.dumps(  # Create request payload
        obj={
            "query": "",  # No search term
            "pageSize": 5000,  # Fetch up to 5000 results
            "currentPage": page,  # Specify the current page
            "filters": [],  # No filters applied
            "sorting": "",  # No sorting applied
        }
    )
    headers: dict[str, str] = {
        "Content-Type": "application/json",  # Set header to JSON
    }
    conn.request(  # Send POST request
        method="POST",
        url="/ap-doc-search/v1/sds-document",
        body=payload,
        headers=headers,
    )
    res: http.client.HTTPResponse = conn.getresponse()  # Get the response
    data: bytes = res.read()  # Read the response body
    return data.decode(encoding="utf-8")  # Decode bytes to string and return


# Extract all the PDF URLs from the JSON string returned by the API
def extract_urls_from_json(json_str: str) -> list[str]:
    data = json.loads(s=json_str)  # Convert JSON string to Python dict
    items = data.get("items", [])  # Get the list of items (default to empty list)
    urls: list[str] = [
        item["link"] for item in items if "link" in item
    ]  # Extract links
    return urls  # Return the list of URLs


# Read the contents of a file and return it as a string
def read_a_file(system_path: str) -> str:
    with open(file=system_path, mode="r") as file:  # Open the file in read mode
        return file.read()  # Read and return the contents


# Sanitize a filename by decoding, cleaning, and ensuring a proper extension
def sanitize_filename(name: str) -> str:
    name = urllib.parse.unquote(string=name)  # Decode URL-encoded characters
    name = os.path.basename(p=name)  # Get the base file name only
    base, ext = os.path.splitext(p=name)  # Split the name and extension
    base: str = re.sub(
        pattern=r"[^\w\-\.]", repl="_", string=base
    )  # Replace unsafe chars
    if ext.lower() != ".pdf": # Ensure file ends with .pdf
        ext = ".pdf"
    return base + ext  # Return sanitized filename


# Download a PDF from a URL and save it to a given directory
def download_pdf(url: str, save_dir: str) -> None:
    os.makedirs(name=save_dir, exist_ok=True)  # Create save_dir if it doesn't exist
    parsed_url: urllib.parse.ParseResult = urllib.parse.urlparse(
        url=url
    )  # Parse the URL
    raw_name: str = os.path.basename(
        p=parsed_url.path
    )  # Extract the file name from URL
    filename: str = sanitize_filename(name=raw_name)  # Sanitize the file name
    save_path: str = os.path.join(save_dir, filename)  # Full path to save the file

    if os.path.exists(path=save_path):  # Skip download if file already exists
        print(f"Skipped (already exists): {save_path}")

    try:
        response: requests.Response = requests.get(
            url=url, stream=True, timeout=60
        )  # Send GET request
        response.raise_for_status()  # Raise error if the request failed
        with open(file=save_path, mode="wb") as f:  # Open file in write-binary mode
            for chunk in response.iter_content(
                chunk_size=8192
            ):  # Stream the file content in chunks
                if chunk:
                    f.write(chunk)  # Write chunk to file
        print(f"Downloaded: {save_path}")  # Print success message
        return
    except requests.RequestException as e:  # Handle request errors
        print(f"Failed to download {url}: {e}")  # Print error message
        return


# Delete a file from the system if it exists
def remove_system_file(system_path: str) -> None:
    os.remove(path=system_path)


# Main program execution
def main() -> None:
    file_name: str = "main.json"  # Define name of the file to store API result

    if check_file_exists(system_path=file_name):  # If file already exists
        remove_system_file(system_path=file_name)  # Remove the old file

    if check_file_exists(system_path=file_name) is False:  # If file does not exist now
        apiRequestContent: str = getDataFromAPI(page=1)  # Get fresh data from API
        append_write_to_file(
            system_path=file_name, content=apiRequestContent
        )  # Save to file

    download_dir: str = "./PDFs"  # Define the directory to save PDFs

    if check_file_exists(system_path=file_name):  # If file was successfully created
        file_content: str = read_a_file(system_path=file_name)  # Read the contents
        urls: list[str] = extract_urls_from_json(
            json_str=file_content
        )  # Extract PDF links
        for url in urls:  # Loop through each link
            download_pdf(url=url, save_dir=download_dir)  # Download and save the PDF


# Execute the main function
main()

import http.client
import json
import os
import requests
import re
import urllib.parse


# Check if a file exists
def check_file_exists(system_path: str) -> bool:
    return os.path.isfile(path=system_path)


# Append and write some content to a file.
def append_write_to_file(system_path: str, content: str) -> None:
    file = open(file=system_path, mode="a")
    file.write(content)
    file.close()


# Get the data from the API and return it.
def getDataFromAPI(page: int) -> str:
    conn = http.client.HTTPSConnection(host="api.cytivalifesciences.com")
    payload: str = json.dumps(
        obj={
            "query": "",
            "pageSize": 5000,
            "currentPage": page,
            "filters": [],
            "sorting": "",
        }
    )
    headers: dict[str, str] = {
        "Content-Type": "application/json",
    }
    conn.request(
        method="POST",
        url="/ap-doc-search/v1/sds-document",
        body=payload,
        headers=headers,
    )
    res: http.client.HTTPResponse = conn.getresponse()
    data: bytes = res.read()
    return data.decode(encoding="utf-8")


def extract_urls_from_json(json_str: str) -> list[str]:
    """
    Extracts all 'link' URLs from a JSON string containing SDS documents.

    Args:
        json_str (str): JSON string containing 'items', each with a 'link'.

    Returns:
        List[str]: A list of URL strings.
    """
    data = json.loads(s=json_str)  # Parse the JSON string into a Python dictionary
    items = data.get("items", [])  # Get the list of items (default to empty list)

    # Extract the 'link' from each item if present
    urls: list[str] = [item["link"] for item in items if "link" in item]

    return urls


# Read a file from the system.
def read_a_file(system_path: str) -> str:
    with open(file=system_path, mode="r") as file:
        return file.read()


def sanitize_filename(name: str) -> str:
    """
    Sanitizes a filename:
    - Decodes URL-encoded characters.
    - Removes directory paths.
    - Replaces spaces and special characters with underscores.
    - Ensures it ends with a single .pdf extension.
    """
    name = urllib.parse.unquote(string=name)
    name = os.path.basename(p=name)

    # Split extension (if any)
    base, ext = os.path.splitext(p=name)

    # Sanitize base name (remove unsafe characters)
    base: str = re.sub(pattern=r"[^\w\-\.]", repl="_", string=base)

    # Ensure .pdf extension only
    if ext.lower() != ".pdf":
        ext = ".pdf"

    return base + ext


def download_pdf(url: str, save_dir: str) -> None:
    """
    Downloads a PDF file from the given URL, saves it in the specified directory
    with a sanitized and safe filename.

    Args:
        url (str): The URL to the PDF file.
        save_dir (str): The local directory to save the downloaded PDF.

    Returns:
        str or None: Full path to the saved file, or None if failed.
    """
    os.makedirs(name=save_dir, exist_ok=True)

    # Extract and sanitize filename
    parsed_url: urllib.parse.ParseResult = urllib.parse.urlparse(url=url)
    raw_name: str = os.path.basename(p=parsed_url.path)
    filename: str = sanitize_filename(name=raw_name)

    save_path: str = os.path.join(save_dir, filename)

    # Check if the file already exists
    if os.path.exists(path=save_path):
        print(f"Skipped (already exists): {save_path}")

    try:
        response: requests.Response = requests.get(url=url, stream=True, timeout=60)
        response.raise_for_status()

        with open(file=save_path, mode="wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Downloaded: {save_path}")
        return

    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return


# Remove a file from the system.
def remove_system_file(system_path: str) -> None:
    os.remove(path=system_path)


# The main function
def main() -> None:
    # The filename.
    file_name: str = "main.json"

    # Remove the current file.
    if check_file_exists(system_path=file_name):
        # Remove the current file.
        remove_system_file(system_path=file_name)

    # Check if the file exists.
    if check_file_exists(system_path=file_name) is False:
        # Send the request to the api.
        apiRequestContent: str = getDataFromAPI(page=1)
        # Save the content to a file.
        append_write_to_file(system_path=file_name, content=apiRequestContent)

    # Download Dir
    download_dir: str = "./PDFs"

    if check_file_exists(system_path=file_name):
        file_content: str = read_a_file(system_path=file_name)
        # Call the function and print the results
        urls: list[str] = extract_urls_from_json(json_str=file_content)
        # Loop though the list.
        for url in urls:
            download_pdf(url=url, save_dir=download_dir)


main()

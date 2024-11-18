import json
import os

import requests


def download_images_from_json(folder_path: str, file_pattern: str) -> None:
    """Work."""
    lst = []
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.startswith(file_pattern) and file_name.endswith(".json"):
                json_file_path = os.path.join(root, file_name)  # noqa: PTH118

                # Open and parse the JSON file
                with open(json_file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)

                    # Check if 'resourcesFull' is present in the JSON data
                    resources = data.get("resourcesFull")
                    if resources:
                        for image_url in resources:
                            lst.append(image_url)
                            part = image_url.split("/")
                            # Save the image with the key as the file name
                            image_file_path = os.path.join(r"jpg", part[-3], part[-1])  # noqa: PTH118
                            if os.path.exists(image_file_path):  # noqa: PTH110
                                print(f"File {image_file_path} already exists. Skipping download.")
                                continue
                            try:
                                # Download the image
                                response = requests.get(image_url)
                                if response.status_code == 200:
                                    os.makedirs(  # noqa: PTH103
                                        os.path.join(r"jpg", part[-3]),  # noqa: PTH118
                                        exist_ok=True,
                                    )
                                    with open(image_file_path, "wb") as image_file:
                                        image_file.write(response.content)
                                    print(f"Downloaded {image_file_path} successfully.")
                                else:
                                    print(f"Failed to download {image_url}. Status code: {response.status_code}")
                            except requests.exceptions.RequestException as e:
                                print(f"Error downloading {image_url}: {e}")
    return lst


if __name__ == "__main__":
    # Set the folder path and file pattern
    folder_path = "json"  # Update with your folder path
    file_pattern = "C1B0003883315"

    # Run the function
    lst = download_images_from_json(folder_path, file_pattern)

    json.dump(lst, open("epaveldas.json", "w"))  # noqa: SIM115

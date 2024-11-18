import os

from split_paragraph import main as process


def main(input_dir: str, output_dir: str) -> None:
    """Main."""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)  # noqa: PTH103

    # Loop over all files in the input directory
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".jpg"):
                # Define full file paths
                img_path = os.path.join(root, filename)  # noqa: PTH118

                # Calculate the relative path for the output directory structure
                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)  # noqa: PTH118

                # Create the output subdirectory if it doesn't exist
                os.makedirs(output_subdir, exist_ok=True)  # noqa: PTH103

                # Define the output text file path
                txt_filename = f"{os.path.splitext(filename)[0]}.txt"  # noqa: PTH122
                txt_path = os.path.join(output_subdir, txt_filename)  # noqa: PTH118
                if os.path.isfile(txt_path):  # noqa: PTH113
                    continue
                print(f"Process {filename}")
                # Perform OCR
                extracted_text = process(img_path)

                # Save OCR result to a text file
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)


if __name__ == "__main__":
    # Define input and output directories
    input_dir = "static/jpg"
    output_dir = "static/txt"
    main(input_dir, output_dir)

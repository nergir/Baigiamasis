import glob
import pandas as pd
from collections import Counter


def check_unique(field_names):
    # Count occurrences of each value in the list
    value_counts = Counter(field_names)

    # Convert to a dictionary (optional)
    value_counts_dict = dict(value_counts)

    # Display the counts
    for i, k in value_counts_dict.items():
        if k > 1:
            print(i, k)
    else:
        print("unikalus")


def make_unique(input_list):
    """
    Modifies the list to make each element unique by appending a suffix to duplicates.

    Parameters:
    - input_list: list of str, the input list of strings.

    Returns:
    - list of str, modified list with unique elements.
    """
    # Dictionary to count occurrences
    occurrence_dict = {}

    # List to store the modified elements
    unique_list = []

    for item in input_list:
        if item not in occurrence_dict:
            # First occurrence, add directly
            occurrence_dict[item] = 0
            unique_list.append(item)
        else:
            # Increment occurrence count and create a unique version
            occurrence_dict[item] += 1
            new_item = f"{item} like {occurrence_dict[item]}"
            unique_list.append(new_item)

    return unique_list


def csv_files_header(file, skip_char="#", skip_rows=0, delimiter=";"):
    """
    Joins multiple CSV files matching a pattern into one single CSV file,
    including the first 40 rows from each file.

    Parameters:
    - file_pattern: str, pattern to match CSV files (e.g., 'data/*.csv').
    - output_file: str, name of the output file to write to.
    - rows_to_read: int, number of data rows to read from each file (default 40).
    - skiprows: int, number of rows to skip at the start of each file (default 0).
    - delimiter: str, field delimiter (default ';').
    """
    # Get a list of files matching the pattern
    fields = []
    with open(file, "r", encoding="iso-8859-13") as infile:
        # Skip the specified number of rows
        for _ in range(skip_rows):
            next(infile)

        for line in infile:
            if line.startswith(skip_char):
                fields.append(line)
            else:
                break
    return fields


def concat_csv_files_skip(
    file_pattern, output_file, skip_char="#", skip_rows=0, delimiter=";"
):
    """
    Concatenates multiple CSV files matching a pattern into one single CSV file,
    skipping any rows that start with a specified character.

    Parameters:
    - file_pattern: str, pattern to match CSV files (e.g., 'data/*.csv').
    - output_file: str, name of the output file to write to.
    - skip_char: str, character to skip rows starting with (default '#').
    - skiprows: int, number of rows to skip at the start of each file (default 0).
    - delimiter: str, field delimiter (default ';').
    """
    # Get a list of files matching the pattern
    file_list = glob.glob(file_pattern)

    with open(output_file, "w", encoding="iso-8859-13", newline="\n") as outfile:
        # writer = csv.writer(outfile, delimiter=delimiter)

        for i, file in enumerate(file_list):
            with open(file, "r", encoding="iso-8859-13") as infile:
                # Skip the specified number of rows
                for _ in range(skip_rows):
                    next(infile)

                for line in infile:
                    if line.startswith(skip_char) or ";" not in line:
                        continue  # Skip this line if it starts with the skip character

                    # Write the line to the output file
                    # writer.writerow(line.strip().split(delimiter))
                    outfile.write(line.strip())

            print(f"Processed {file}")


def join_csv_files(file_pattern, output_file, skiprows=40, delimiter=";"):
    """
    Joins multiple CSV files matching a pattern into one single CSV file.

    Parameters:
    - file_pattern: str, pattern to match CSV files (e.g., 'data/*.csv').
    - output_file: str, name of the output file to write to.
    - skiprows: int, number of rows to skip at the start of each file (default 40).
    - delimiter: str, field delimiter (default ';').
    """
    # Get a list of files matching the pattern
    file_list = glob.glob(file_pattern)

    with open(output_file, "w", encoding="iso-8859-13") as outfile:
        for file in file_list:
            with open(file, "r", encoding="iso-8859-13") as infile:
                # Skip the specified number of rows
                for _ in range(skiprows):
                    next(infile)  # Skip rows

                # Read the remaining lines and write to the output file
                for line in infile:
                    outfile.write(line)

            print(f"Processed {file}")


def read_and_concat(file_pattern, encoding="utf-8", delimiter=",", skiprows=None):
    """
    Reads multiple CSV files matching a pattern and concatenates them into a single DataFrame.

    Parameters:
    - file_pattern: str, pattern to match CSV files (e.g., 'data/*.csv').
    - encoding: str, file encoding (default 'utf-8').
    - delimiter: str, field delimiter (default ',').
    - skiprows: int, number of rows to skip at the start (default None).

    Returns:
    - Concatenated DataFrame containing all the CSV data.
    """
    # Get a list of files matching the pattern
    file_list = glob.glob(file_pattern)

    # Read each CSV file into a DataFrame and collect them in a list
    df_list = []
    for file in file_list:
        try:
            df = pd.read_csv(
                file, encoding=encoding, delimiter=delimiter, skiprows=skiprows
            )
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Concatenate all DataFrames vertically
    if df_list:
        concatenated_df = pd.concat(df_list, ignore_index=True)
        return concatenated_df
    else:
        print("No valid CSV files found or loaded.")
        return None


def join_csv_files_head(
    file_pattern, output_file, rows_to_read=40, skiprows=0, delimiter=";"
):
    """
    Joins multiple CSV files matching a pattern into one single CSV file,
    including the first 40 rows from each file.

    Parameters:
    - file_pattern: str, pattern to match CSV files (e.g., 'data/*.csv').
    - output_file: str, name of the output file to write to.
    - rows_to_read: int, number of data rows to read from each file (default 40).
    - skiprows: int, number of rows to skip at the start of each file (default 0).
    - delimiter: str, field delimiter (default ';').
    """
    # Get a list of files matching the pattern
    file_list = glob.glob(file_pattern)

    with open(output_file, "w", encoding="iso-8859-13") as outfile:
        for i, file in enumerate(file_list):
            with open(file, "r", encoding="iso-8859-13") as infile:
                # Skip the specified number of rows
                for _ in range(skiprows):
                    next(infile)  # Skip rows

                # Read the header from the first file and write it
                if i == 0:
                    header = next(infile)  # Read the header line
                    outfile.write(header)  # Write header to output file

                # Read the next 40 rows and write to the output file
                for _ in range(rows_to_read):
                    line = next(infile, None)
                    if line is None:
                        break  # Exit if there are no more lines to read
                    outfile.write(line)

            print(f"Processed {file}")


def check_rows_start_with_hash(file_path):
    """
    Checks if all rows in the specified CSV file start with a '#' character.

    Parameters:
    - file_path: str, path to the CSV file to check.

    Returns:
    - bool: True if all rows start with '#', False otherwise.
    """
    try:
        with open(file_path, "r", encoding="iso-8859-13") as infile:
            for line_number, line in enumerate(infile):
                if not line.startswith("#"):
                    print(
                        f"{file_path} Row {line_number + 1} does not start with '#': {line.strip()}"
                    )
                    return False
        return True
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False


def compact_indices(indices):
    """
    Compacts a list of indices into a string format.

    Parameters:
    - indices: list of int, indices to compact.

    Returns:
    - str: compacted string representation of indices.
    """
    if not indices:
        return ""

    indices.sort()  # Sort the indices to handle them in order
    compacted = []
    start = indices[0]
    end = indices[0]

    for i in range(1, len(indices)):
        if indices[i] == end + 1:  # Check if current index is consecutive
            end = indices[i]
        else:
            # If not consecutive, add the current range to the list
            if start == end:
                compacted.append(str(start))
            else:
                compacted.append(f"{start}-{end}")
            start = end = indices[i]  # Reset the start and end to the current index

    # Add the last range to the list
    if start == end:
        compacted.append(str(start))
    else:
        compacted.append(f"{start}-{end}")

    return ", ".join(compacted)


def check_csv_files_day(
    file_pattern, output_file, skip_char="#", skip_rows=0, delimiter=";"
):
    """
    Joins multiple CSV files matching a pattern into one single CSV file,
    including the first 40 rows from each file.

    Parameters:
    - file_pattern: str, pattern to match CSV files (e.g., 'data/*.csv').
    - output_file: str, name of the output file to write to.
    - rows_to_read: int, number of data rows to read from each file (default 40).
    - skiprows: int, number of rows to skip at the start of each file (default 0).
    - delimiter: str, field delimiter (default ';').
    """
    # Get a list of files matching the pattern
    file_list = glob.glob(file_pattern)

    with open(output_file, "w", encoding="iso-8859-13") as outfile:
        for i, file in enumerate(file_list):
            data, _ = file.split(".", 2)
            with open(file, "r", encoding="iso-8859-13") as infile:
                # Skip the specified number of rows
                for _ in range(skip_rows):
                    next(infile)

                for line in infile:
                    if line.startswith(skip_char) or ";" not in line:
                        continue  # Skip this line if it starts with the skip character

                    # Write the line to the output file
                    # writer.writerow(line.strip().split(delimiter))
                    line = line.strip()
                    part = line.split(delimiter, 4)
                    if len(part) != 4:
                        continue
                    id_, data_, laikas_, _ = part
                    if data != data_:
                        outfile.write(data, data_)

            print(f"Processed {file}")


if __name__ == "__main__":
    # Example usage 2015-11-13.csv 2013-11-18.csv 2013-01-17.csv 13:23:30
    file_pattern = "Ataskaitos/*.csv"  # e.g., 'data/*.csv'
    output_file = "combined_output_skip.csv"  # Output file name
    check_csv_files_day(file_pattern, "check_day.csv")
    exit(0)
    concat_csv_files_skip(
        file_pattern, output_file, skip_char="#", skip_rows=0, delimiter=";"
    )
    quit(0)
    print(f"All CSV files have been combined into {output_file}.")
    # Example usage
    file_pattern = "Ataskaitos/*.csv"  # e.g., 'data/*.csv'
    output_file = "combined_output_header.csv"  # Output file name
    join_csv_files_head(
        file_pattern, output_file, rows_to_read=40, skiprows=0, delimiter=";"
    )

    print(f"All CSV files have been combined into {output_file}.")

    # Example usage
    file_path = "combined_output_header.csv"  # Replace with your file path
    if check_rows_start_with_hash(file_path):
        print(f"All rows in '{file_path}' start with '#'.")
    else:
        print(f"Not all rows in '{file_path}' start with '#'.")

    # Example usage
    file_pattern = "Ataskaitos/*.csv"  # e.g., 'data/*.csv'
    output_file = "combined_output.csv"  # Output file name
    join_csv_files(file_pattern, output_file, skiprows=40, delimiter=";")

    print(f"All CSV files have been combined into {output_file}.")

    # Example usage
    file_pattern = (
        "Ataskaitos/*.csv"  # For example, 'data/*.csv' for all CSV files in a folder
    )
    df = read_and_concat(
        file_pattern, encoding="iso-8859-13", delimiter=";", skiprows=40
    )

    # Display the concatenated DataFrame
    if df is not None:
        print(df)

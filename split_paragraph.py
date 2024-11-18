import re

import cv2
import enchant
import numpy as np
from pytesseract import Output, pytesseract

lithuanian_dict = enchant.Dict("lt_LT")
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def text_with_rectangle(image: any) -> any:
    """Test."""
    results = pytesseract.image_to_data(image, lang="lit", output_type=Output.DICT, config="--psm 6")
    for i in range(len(results["text"])):
        # extract the bounding box coordinates of the text region from
        # the current result
        x = results["left"][i]
        y = results["top"][i]
        w = results["width"][i]
        h = results["height"][i]
        # extract the OCR text itself along with the confidence of the
        # text localization
        text = results["text"][i]
        conf = float(results["conf"][i])

        # filter out weak confidence text localizations
        if conf > 10:
            # strip out non-ASCII text, so we can draw the text on the image
            # using OpenCV, then draw a bounding box around the text along
            # with the text itself
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img=image,
                text=text,
                org=(x, y),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=0.3,
                color=(36, 0, 255),
                thickness=1,
            )
    return image


def merge_balanced_intervals(intervals: list) -> tuple:
    """Merge intervals based on balanced gaps in pairs.
    Assumes intervals are already sorted.

    Args:
        intervals: List of sorted tuples representing intervals (start, end)
    Returns:
        List of merged intervals and the balanced gap found
    """  # noqa: D205
    if len(intervals) <= 2:
        return intervals, 0

    # Find gaps between consecutive intervals
    gaps = []
    for i in range(len(intervals) - 1):
        gap = intervals[i + 1][0] - intervals[i][1]
        gaps.append(gap)

    # Find the most balanced consecutive gaps
    min_diff = float("inf")
    balanced_idx = 0

    for i in range(len(gaps) - 1):
        diff = abs(gaps[i] - gaps[i + 1])
        if diff < min_diff:
            min_diff = diff
            balanced_idx = i

    # Merge at the most balanced point
    result = []
    i = 0
    while i < len(intervals):
        if i == balanced_idx:
            # Merge this interval with the next one
            merged = (intervals[i][0], intervals[i + 1][1])
            result.append(merged)
            i += 2
        else:
            result.append(intervals[i])
            i += 1

    return result, gaps[balanced_idx]


def detect_columns_bin(binary, left=0, image=None):
    height, width = binary.shape
    limit = width // 3
    b_mean = np.mean(binary == 255, axis=0)
    # print(b_mean)
    empty_rows = np.where(b_mean > 0.99)
    rows = eliminate_non_grouped_sequences(empty_rows[0], 15)
    gaps = find_gaps(rows)
    # print("gaps", left, len(gaps), binary.shape, gaps)
    # Find contours
    if len(gaps) == 3:
        temp, gap = merge_balanced_intervals(gaps)
        # print(temp, gap)
        if len(temp) == 2:
            gaps = temp

    gaps = [gap for gap in gaps if gap[1] - gap[0] > limit]
    if not gaps:
        gaps = [(0, width - 1)]
    # print(limit, len(gaps))
    extracted_texts = []
    slot = 0
    for start, end in gaps:
        if end - start < 1:
            continue
        cropped_region = binary[:, max(0, start - 5) : min(end + 5, width - 1)]
        extracted_text = pytesseract.image_to_string(cropped_region, lang="lit", config="--oem 3 --psm 6")
        extracted_texts.append(extracted_text)
        # text_with_rectangle(cropped_region)
        # cv2.imwrite(f"{left}{slot}.bin.png", cropped_region)
        slot += 1
    return extracted_texts


def find_gaps(empty_rows: list) -> list:
    """Find."""
    if not empty_rows.size:
        return []

    # Convert to a sorted unique array
    empty_rows = np.unique(empty_rows)

    # Initialize variables
    gaps = []

    # Iterate through empty rows to find gaps
    for i in range(1, len(empty_rows)):
        # Check for gaps
        if empty_rows[i] != empty_rows[i - 1] + 1:
            start_gap = empty_rows[i - 1] + 1
            end_gap = empty_rows[i] - 1
            gaps.append((start_gap, end_gap))

    return gaps


def eliminate_non_grouped_sequences(arr, min_length=5):
    # Initialize variables
    grouped_sequences = []
    current_sequence = []

    for i in range(len(arr)):
        # Start a new sequence if current_sequence is empty or the current number continues the sequence
        if not current_sequence or arr[i] == current_sequence[-1] + 1:
            current_sequence.append(arr[i])
        else:
            # If we finish a sequence, check its length
            if len(current_sequence) >= min_length:
                grouped_sequences.extend(current_sequence)
            # Start a new sequence
            current_sequence = [arr[i]]

    # Check the last sequence
    if len(current_sequence) >= min_length:
        grouped_sequences.extend(current_sequence)

    return np.array(grouped_sequences)


def compare_strings(s1: str, s2: str) -> int:
    """Compare two strings and return a similarity score based on common characters."""
    common_chars = set(s1) & set(s2)
    similarity_score = len(common_chars)

    return similarity_score


def find_best_replacement(target, alternatives):
    """Find."""
    best_score = 0
    best_alternative = None

    for alternative in alternatives:
        score = compare_strings(target, alternative)
        if score > best_score:
            best_score = score
            best_alternative = alternative

    return best_alternative


def split_string(s: str) -> str:
    """Split."""
    # Use regex to add a space before the first letter following digits
    result = re.sub(r"\b(\d+)([a-z]+)\b", r"\1 \2", s, re.IGNORECASE)  # noqa: B034
    return result


def join_if_valid(match) -> str:  # noqa: ANN001
    """Join."""
    # Get the parts of the word
    word_part1 = match.group(1)
    word_sep = match.group(2)
    word_part2 = match.group(3)

    # Check if the combined word is in the dictionary
    combined_word = word_part1 + word_part2

    if word_sep.startswith("-"):
        print(word_part1, word_part2, word_sep)
        return combined_word + "\n"
    if lithuanian_dict.check(combined_word):
        print(word_part1, word_part2, lithuanian_dict.check(combined_word))
        return combined_word + "\n"  # Join the split parts if valid
    words = lithuanian_dict.suggest(combined_word)
    best = find_best_replacement(combined_word, words)
    print(combined_word, best, words)
    if best and best.replace(" ", "") == combined_word:
        return best + "\n"
    return f"{word_part1}\n{word_part2}"  # Keep as is if invalid


def main(byla: str, test: bool) -> str:  # noqa: FBT001
    """Main."""
    image = cv2.imread(byla)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Convert to black and white (binary)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    b_mean = np.mean(binary == 255, axis=1)
    # print(b_mean)
    empty_rows = np.where(b_mean > 0.99)
    # print(empty_rows)
    image_with_lines = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    # Draw red lines on empty rows
    rows = eliminate_non_grouped_sequences(empty_rows[0], 15)
    gaps = find_gaps(rows)
    width = image_with_lines.shape[1]
    color = (255, 0, 0)  # (255, 0, 0) is red in BGR
    # print(len(rows))
    for row in rows:
        cv2.line(image_with_lines, (0, row), (width, row), color, 1)
    extracted_texts = []
    limit = binary.shape[0]
    slot = 0
    for start, end in gaps:
        if end - start < 20:
            continue
        cropped_region = image_with_lines[start:end, :]
        if test:
            cv2.imwrite(f"{slot}.png", cropped_region)
        cropped_region_bin = binary[max(start - 10, 0) : min(end + 10, limit), :]
        if test:
            cv2.imwrite(f"{slot}.bin.png", cropped_region)
        # extracted_text = pytesseract.image_to_string(cropped_region, lang='lit', config="--psm 6")
        # extracted_texts.append(extracted_text)
        extracted_texts.extend(detect_columns_bin(cropped_region_bin, slot, cropped_region))
        slot += 1
        if test:
            cv2.rectangle(image_with_lines, (5, start), (width - 5, end), (128, 128, 0), 5)
    text = "\n".join(extracted_texts)
    text = split_string(text)
    text = re.sub(r"(?<=\S)\s{2,}(?=\S)", " ", text, re.MULTILINE)  # noqa: B034
    # return text.replace("-\n", "")
    # return re.sub(r"(\w)-\n(\w)", r"\1\2\n", text)
    return re.sub(r"\b(\w+)(-?)\n(\w+)\b", join_if_valid, text)


if __name__ == "__main__":
    # Load the image
    # byla = "static/jpg/C1B0003883315-1931-Nr.1/0003-3F8F7193CBDEBDA44D07F5184FCA102C.jpg"
    byla = "static/jpg/C1B0003883315-1931-Nr.1/0004-5AC27F980DA9073C8322DB3730C82816.jpg"
    # byla = "static/jpg/C1B0003883315-1931-Nr.1/0002-7A65741F1B4FDF665FE7DFD1BF188014.jpg"
    # byla = "static/jpg/C1B0003883315-1931-Nr.1/0001-C38C4351609E704031483BF4DEC26307.jpg"

    text = main(byla, test=False)
    print(text)

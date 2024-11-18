import ctypes
import fnmatch
import os
import sys
import time

import cv2
import numpy as np
import pytesseract
import win32con
import win32gui
from PIL import Image, ImageGrab

# import pyautogui
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def divide_number(number: int, divider: int = 5) -> list:
    """Divide."""
    if number <= divider:
        return [number]

    # Calculate how many parts we need
    num_parts = (number + divider - 1) // divider  # ceiling division
    base_value = number // num_parts
    remainder = number % num_parts

    # Create result array
    result = [base_value] * num_parts

    # Distribute remainder
    for i in range(remainder):
        result[i] += 1

    # Sort in descending order
    # result.sort(reverse=True)

    return result


def retrieve_jpeg_files(root_dir: str, batch_size: int = 5) -> list:
    """Retrieve."""
    lst = []
    for dirpath, _, filenames in os.walk(root_dir):
        # Filter JPEG files from the current directory
        jpeg_files = fnmatch.filter(filenames, "*.jpg")

        # Batch the found JPEG files
        # for i in range(0, len(jpeg_files), batch_size):
        s = 0
        for i in divide_number(len(jpeg_files), batch_size):
            jpeg_batch = jpeg_files[s : s + i]  # Retrieve next batch of JPEG files
            s += i
            # Create full paths for each file
            full_paths = [os.path.join(dirpath, jpeg_file) for jpeg_file in jpeg_batch]  # noqa: PTH118
            lst.append(full_paths)
    return lst


def move(x: int, y: int) -> None:
    """Move."""
    ctypes.windll.user32.SetCursorPos(x, y)
    # pyautogui.moveTo(x, y)


def click(x: int, y: int) -> None:
    """Click."""
    # pyautogui.moveTo(x, y)
    # pyautogui.click(x, y)
    # return
    #
    # see http://msdn.microsoft.com/en-us/library/ms646260(VS.85).aspx for details
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up


def send_enter(window_handle: int) -> None:
    """Enter."""
    # Send the Enter key to the window
    win32gui.SendMessage(window_handle, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32gui.SendMessage(window_handle, win32con.WM_KEYUP, win32con.VK_RETURN, 0)


def upload(lst: list) -> None:  # noqa: C901
    """Upload."""
    cnt = 0
    # Get the handle of the dialog box (adjust title as per your dialog)
    while True:
        time.sleep(0.1)
        for title in ("Failo išsiuntimas", "Atidarymas"):
            hwnd = win32gui.FindWindow("#32770", title)
            if hwnd:
                break
        if cnt == 3:
            break
        cnt += 1

    if isinstance(lst, list | tuple):
        ini_dir, name = os.path.split(lst and lst[0] or "")
        file_path = '"{}"'.format('" "'.join([os.path.basename(i) for i in lst]))  # noqa: PTH119
    else:
        file_path = lst

    print(ini_dir, file_path)
    cnt = 3
    while cnt:
        dialog = win32gui.FindWindow("#32770", title)
        print("dialog", dialog)
        comboboxex32 = win32gui.FindWindowEx(dialog, 0, "ComboBoxEx32", None)
        combobox = win32gui.FindWindowEx(comboboxex32, 0, "ComboBox", None)
        edit = win32gui.FindWindowEx(combobox, 0, "Edit", None)
        button = win32gui.FindWindowEx(dialog, 0, "Button", "Atidaryti")
        if button == 0:
            button = win32gui.FindWindowEx(dialog, 0, "Button", None)
        cancel = win32gui.FindWindowEx(dialog, 0, "Button", "Atšaukti")
        if cancel:
            break
        cnt -= 1
        time.sleep(0.1)
    button_title = win32gui.GetWindowText(button)
    print(button_title, cancel, edit)

    win32gui.SendMessage(edit, win32con.WM_SETTEXT, 0, ini_dir)
    time.sleep(0.1)
    win32gui.SendMessage(button, win32con.BM_CLICK, None, None)
    # send_enter(edit)
    time.sleep(0.1)
    win32gui.SendMessage(edit, win32con.WM_SETTEXT, 0, file_path)
    time.sleep(0.1)
    win32gui.SendMessage(button, win32con.BM_CLICK, None, None)
    # send_enter(edit)
    time.sleep(0.1)
    while True:
        hwnd = win32gui.FindWindow("#32770", title)
        if hwnd:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.1)
        else:
            break


def grab_file(image_path: str, w: int | None = None, h: int | None = None):  # noqa: ANN201
    """Grab."""
    img = Image.open(image_path)
    img_np = np.array(img)
    if w is None and h is None:
        return img_np

    height, width, _ = img_np.shape

    # Get the half-window view
    img_np = img_np[
        : height // h,
        : width // w,
    ]
    return img_np


def grab_screen(w: int | None = None, h: int | None = None):  # noqa: ANN201
    """Grap."""
    img = ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True)
    img_np = np.array(img)
    if w is None and h is None:
        return img_np

    height, width, _ = img_np.shape

    # Get the half-window view
    img_np = img_np[
        : height // h,
        : width // w,
    ]
    return img_np


def process(image: any, target_text: str) -> tuple:
    """Process."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    df_txt = pytesseract.image_to_data(gray, lang="eng", config="--psm 6", output_type=pytesseract.Output.DATAFRAME)

    # group recognized words by lines
    for _, words_per_line in df_txt.groupby("line_num"):
        # filter out words with a low confidence
        words_per_line = words_per_line[words_per_line["conf"] >= 1]  # noqa: PLW2901
        if not len(words_per_line):
            continue

        words = words_per_line["text"].values  # noqa: PD011
        line = " ".join(str(word) for word in words)
        # print(f"{line_num} '{line}'")

        if target_text in line:
            word_boxes = []
            for left, top, width, height, text in words_per_line[["left", "top", "width", "height", "text"]].values:  # noqa: PD011
                if text in target_text:
                    word_boxes.append((left, top))
                    word_boxes.append((left + width, top + height))
            # print(word_boxes)
            if word_boxes:
                x, y, w, h = cv2.boundingRect(np.array(word_boxes))
                print(x, y, w, h, target_text)
                pt = x + w // 2, y + h // 2
                cropped_image = image[y : y + h, x : x + w]
                cv2.imwrite(f"png/{pt} {w}x{h}.png", cropped_image)
                return pt
    return None


def main() -> None:
    """Main."""
    byla = "skip.txt"
    root_directory = r"c:\ftp\kriminalas\static\jpg"  # Change this to your target directory
    lst_chunk = retrieve_jpeg_files(root_directory)
    print(len(lst_chunk))
    try:
        f = open(byla, "r")  # noqa: SIM115
        skip = f.readline()
        print(skip)
        f.close()
        if skip:
            while lst_chunk and skip not in "\n".join(lst_chunk[0]):
                lst_chunk.pop(0)
    except Exception:  # noqa: BLE001, S110
        pass
    print(len(lst_chunk))
    lst_chunk = [lst for lst in lst_chunk if bool(lst)]
    title = "Failo išsiuntimas"
    while lst_chunk:
        try:
            time.sleep(1)
            hwnd = win32gui.FindWindow("#32770", title)
            if hwnd:
                # win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                print("dialog " * 9)
                continue
            img_np = grab_screen(2, 1)
            pt = process(
                img_np,
                "Processing",
            )
            if pt is not None:
                continue
            pt = process(
                img_np,
                "ying",
            )
            if pt is not None:
                continue
            pt = process(
                img_np,
                "you are human",
            )
            if pt is not None:
                click(pt[0], pt[1])
                continue
            pt = process(
                img_np,
                "Proceed All",
            )
            if pt is not None:
                pt = process(
                    img_np,
                    "Clear All",
                )
                if pt is not None:
                    click(pt[0], pt[1])
                    continue
            pt_proceed = process(
                img_np,
                "Proceed",
            )

            if pt_proceed is not None:
                click(pt_proceed[0], pt_proceed[1])
                time.sleep(1)
                continue
            pt_download = process(
                img_np,
                "Download All",
            )
            pt_upload = process(
                img_np,
                "Upload",
            )
            if pt_upload is None:
                if pt_download is not None:
                    lst_chunk.pop(0)
                    click(pt_download[0], pt_download[1])
                    time.sleep(1)

                    pt = process(
                        img_np,
                        "Start Over",
                    )
                    if pt is not None:
                        click(pt[0], pt[1])
            else:
                # copy_file_path(lst_chunk.pop(0))
                # pyautogui.hotkey("ctrl", "v")
                click(pt_upload[0], pt_upload[1])
                upload(lst_chunk[0])
                continue

        except KeyboardInterrupt:
            text = "\n".join(lst_chunk[0])
            f = open(byla, "w")  # noqa: SIM115
            f.write(text)
            f.close()
            print(text)
            exit()
            # User interrupt the program with ctrl+c
        except Exception:  # noqa: BLE001
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
    os.remove(byla)  # noqa: PTH107


if __name__ == "__main__":
    main()

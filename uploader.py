import threading
import logging
import os
from pydub import AudioSegment
from tkinter import filedialog, Toplevel, ttk


def convert_to_mp3(file_path, file_name, callback):
    logging.info(f"Converting '{file_name}' to MP3...")

    try:
        audio = AudioSegment.from_file(file_path)
        output_path = os.path.splitext(file_path)[0] + ".mp3"
        audio.export(output_path, format="mp3")
        logging.info("Conversion complete")
        callback(output_path)
    except Exception as e:
        logging.error(f"Conversion failed: {e}")


def upload_file(callback):
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.wav;*.mp3;*.flac;*.aac;*.aacp")]
    )
    file_name = file_path.rsplit('/', 1)[-1]

    if file_path:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        logging.info(f"Selected file: {file_name}")

        if ext == '.mp3':
            callback(file_path)
        elif ext in ['.wav', '.flac', '.aac', '.aacp']:

            threading.Thread(target=convert_to_mp3, name="mp3_convertion", args=(file_path, file_name, callback), daemon=True).start()
        else:
            logging.warning(f"Unsupported file format: {ext}")

import threading
import logging
import os
from pydub import AudioSegment
from tkinter import filedialog, Toplevel, ttk
import subprocess


def convert_to_mp3(file_path, file_name, progress_window, progress_bar, callback):
    logging.info(f"Converting '{file_name}' to MP3...")

    output_path = file_path.rsplit('.', 1)[0] + '.mp3'

    # Prepare the ffmpeg command with progress reporting
    command = [
        'ffmpeg', '-i', file_path, '-vn', '-acodec', 'libmp3lame', '-ab', '192k', output_path
    ]

    # Define a process to run the ffmpeg command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Read the output and look for the progress information
    for line in process.stderr:
        if 'time=' in line:
            # Extract the time (e.g., 00:01:23.45) and calculate progress
            time_str = line.split('time=')[1].split(' ')[0]
            time_parts = time_str.split(':')
            seconds = float(time_parts[0]) * 3600 + float(time_parts[1]) * 60 + float(time_parts[2])

            # Get the total duration of the audio file
            duration_command = ['ffmpeg', '-i', file_path]
            duration_process = subprocess.Popen(duration_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                universal_newlines=True)
            duration_output = duration_process.communicate()[1]
            total_time_str = [line for line in duration_output.splitlines() if 'Duration' in line][0]
            total_duration = total_time_str.split('Duration:')[1].split(',')[0]
            total_parts = total_duration.split(':')
            total_seconds = float(total_parts[0]) * 3600 + float(total_parts[1]) * 60 + float(total_parts[2])

            # Calculate percentage of completion
            progress = (seconds / total_seconds) * 100

            # Update the progress bar
            progress_bar['value'] = progress
            progress_window.update_idletasks()

    # Wait for the process to finish
    process.wait()

    # Close the progress window and update the status
    progress_window.destroy()
    callback(output_path)


def upload_file(callback, window):
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
            progress_window, progress_bar = window.conversion_progress()
            threading.Thread(target=convert_to_mp3, name="mp3_convertion", args=(file_path, file_name, progress_window, progress_bar, callback), daemon=True).start()
        else:
            logging.warning(f"Unsupported file format: {ext}")

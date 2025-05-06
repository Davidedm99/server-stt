import os
import tkinter as tk
from tkinter import ttk

import pyperclip
from PIL import Image, ImageTk
from pathlib import Path

from uploader import upload_file
import log_manager
from gui.components import bordered_panel, big_button, small_button
from gui.options_window import OptionsGUI
from options import Options


class MainWindow(tk.Tk):
    main_frame: tk.Frame

    def _add_console_line(self, line: str):
        self.console_text.configure(state='normal')
        self.console_text.insert(tk.END, line + os.linesep)
        self.console_text.configure(state='disabled')
        if self.console_autoscroll.get():
            self.console_text.see(tk.END)

    def show_options(self):
        options = OptionsGUI(self.options)
        options.iconbitmap(self.icon_path)
        options.transient(self)
        options.grab_set()
        self.wait_window(options)

    # Pop up window to show the progress during the ffmpeg conversion
    def conversion_progress(self):
        # Create a new top-level window (popup)
        progress_window = tk.Toplevel(self)
        progress_window.title("Conversion Progress")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)

        # Prevent interaction with the main window
        progress_window.grab_set()

        # Add a label
        label = tk.Label(progress_window, text="The input file was not an mp3! Let me convert it...", font=("Arial", 10))
        label.pack(pady=5)
        label = tk.Label(progress_window, text="Converting... Please wait.", font=("Arial", 10))
        label.pack(pady=2)

        # Add the progress bar
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="determinate")
        progress_bar.pack(pady=10)

        # Return both the window and the progress bar widget
        return progress_window, progress_bar

    def add_converted_file(self, file_path):
        filename = os.path.basename(file_path)
        self.result_listbox.insert(tk.END, filename)

    def show_about(self):
        x, y = self.winfo_pointerxy()
        about = tk.Toplevel()
        about.geometry(f"+{x}+{y}")
        about.iconbitmap(self.icon_path)
        about.title("About")
        about.configure(padx=30, pady=20, background='white', highlightcolor='cornflower blue',
                        highlightbackground='cornflower blue', highlightthickness=1, relief='solid')
        about.overrideredirect(True)
        about.resizable(False, False)

        title_frame = tk.Frame(about, background='white')
        image = Image.open(self.icon_path)
        image = image.resize((64, 64))
        tk_image = ImageTk.PhotoImage(image)
        label = tk.Label(title_frame, image=tk_image, background='white')
        label.image = tk_image
        label.pack(side='left', pady=20)
        tk.Label(title_frame, text=self.title(), font=('Segoe UI', 16), background='white').pack(side=tk.LEFT, padx=20)
        title_frame.pack()

        for abt in self.about:
            tk.Label(about, text=abt.strip(), background='white').pack(pady=0)

        ok = small_button(about, 'Ok', command=about.destroy)
        ok.configure(width=20)
        ok.pack(pady=10)

    def _clear_console(self):
        self.console_text.configure(state='normal')
        self.console_text.delete('1.0', tk.END)
        self.console_text.configure(state='disabled')

    def _copy_console(self):
        pyperclip.copy(self.console_text.get('1.0', tk.END))

    def __init__(self, title: str, icon_path: Path, options: Options, about: list[str]):
        tk.Tk.__init__(self)
        # Window properties
        self.title(title)
        self.icon_path = icon_path
        self.iconbitmap(icon_path)
        self.minsize(600, 400)
        self.geometry('600x400')
        self.configure(background='white', padx=10, pady=5)
        self.columnconfigure(0, weight=1)
        self.console_autoscroll = tk.BooleanVar(value=True)
        self.options = options
        self.about = about
        self.file_icon = ImageTk.PhotoImage(Image.open("gui/icons/file_icon.png").resize((32, 32)))
        self.folder_icon = ImageTk.PhotoImage(Image.open("gui/icons/folder_icon.png").resize((32, 32)))
        # About and options
        header_frame = bordered_panel(self)
        # tk.Label(header_frame,text="Testo di prova",compound="left").pack()
        big_button(header_frame, "About", command=self.show_about).grid(row=0, column=0)
        big_button(header_frame, "Options", command=self.show_options).grid(row=0, column=2)
        header_frame.columnconfigure(1, minsize=5)
        header_frame.grid(row=0, sticky='nw', pady=5)

        # Application-specific panel
        self.main_frame = bordered_panel(self)
        self.main_frame.config(height=200)  # Set a fixed height (optional)
        self.main_frame.grid_propagate(False)  # Prevent it from shrinking to fit contents
        self.main_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.main_frame.columnconfigure(0, weight=1)  # Left panel
        self.main_frame.columnconfigure(1, minsize=2)  # Separator
        self.main_frame.columnconfigure(2, weight=1)  # Right panel
        self.main_frame.rowconfigure(0, weight=1)

        # LEFT: Upload controls
        upload_frame = tk.Frame(self.main_frame, background='white')
        upload_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        upload_frame.columnconfigure(0, weight=1)
        upload_frame.grid_propagate(False)
        upload_frame.config(width=250)

        upload_label = tk.Label(upload_frame, text="Upload Audio", background='white', font=("Arial", 12, "bold"))
        upload_label.pack(anchor='nw')

        upload_file_button = tk.Button(upload_frame,
                                       text="Upload File",
                                       command=lambda: upload_file(self.add_converted_file, self),
                                       image=self.file_icon,
                                       compound="left",
                                       anchor="w",
                                       padx=45,
                                       relief="raised")
        upload_file_button.pack(anchor='nw', pady=(5, 2), fill='x')

        upload_folder_button = tk.Button(upload_frame,
                                         text="Upload Folder",
                                         command=lambda: upload_file(self.add_converted_file),
                                         image=self.folder_icon,
                                         compound="left",
                                         anchor="w",
                                         padx=45,
                                         relief="raised")
        upload_folder_button.pack(anchor='nw', fill='x')

        # SEPARATOR (a thin vertical line)
        separator = tk.Frame(self.main_frame, background='light steel blue')
        separator.config(width=2)
        separator.grid(row=0, column=1, sticky='ns', padx=0, pady=0)

        # RIGHT: List of converted files
        result_frame = tk.Frame(self.main_frame, background='white')
        result_frame.grid(row=0, column=2, sticky='nsew', padx=(5, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        result_frame.grid_propagate(False)
        result_frame.config(width=250)

        result_label = tk.Label(result_frame, text="Converted Files", background='white', font=("Arial", 12, "bold"))
        result_label.grid(row=0, column=0, sticky='nw')

        self.result_listbox = tk.Listbox(result_frame, borderwidth=1, relief='solid')
        self.result_listbox.grid(row=1, column=0, sticky='nsew', pady=(5, 0))

        # Console
        console_frame = bordered_panel(self)
        console_frame.columnconfigure(0, weight=1)
        console_frame.columnconfigure(1, weight=0)
        console_frame.rowconfigure(0, weight=1)

        console_text_frame = tk.Frame(console_frame)
        self.console_text = tk.Text(console_text_frame, state=tk.DISABLED, height=0, width=0,
                                    highlightbackground='cornflower blue', relief='solid', borderwidth=0,
                                    highlightthickness=1, wrap='none')
        self.console_text.pack(side='left', fill=tk.BOTH, expand=True)
        scroll = tk.Scrollbar(console_text_frame, orient='vertical', command=self.console_text.yview)
        scroll.pack(side='left', fill=tk.Y, after=self.console_text)
        self.console_text.configure(yscrollcommand=scroll.set)
        log_manager.add_listener(self._add_console_line)
        console_text_frame.grid(column=0, row=0, sticky='NSEW')

        console_frame.columnconfigure(1, minsize=5)

        console_controls = tk.Frame(console_frame, background='white')
        console_copy = small_button(console_controls, "Copy", command=self._copy_console)
        console_clear = small_button(console_controls, "Clear", command=self._clear_console)

        console_autoscroll = tk.Checkbutton(console_controls, text="Auto scroll", variable=self.console_autoscroll,
                                            background='white')

        console_copy.configure(width=15)
        console_copy.pack(fill='x')
        console_clear.pack(fill='x', pady=5)
        console_autoscroll.pack(fill='x')
        console_controls.grid(column=2, row=0, sticky='NEW')

        self.rowconfigure(2, weight=1)
        console_frame.grid(row=2, sticky='NSEW', pady=5)


if __name__ == '__main__':
    from options import Option
    from pathlib import Path

    opt = Options('test', 'test', [
        Option('Stringa', 'aaa'),
        Option('Intero', 0),
        Option('Float', .5),
        Option('Bool', True),
        Option('Cartella', Path.cwd()),
        Option('File', Path(__file__)),
    ])
    w = MainWindow('test', opt, [f'About string {i}' for i in range(10)])
    tk.Label(w.main_frame, text="Change me!", foreground='red', background='yellow').pack(expand=True, fill='both')

    w.mainloop()

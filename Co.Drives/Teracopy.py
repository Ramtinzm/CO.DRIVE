import tkinter as tk
import os
import shutil
import threading
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import time

class FileTransferApp:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer")
        master.geometry("600x150")
        master.resizable(False, False)

        self.source_label = tk.Label(master, text="Drive for copy:")
        self.source_label.grid(row=0, column=0)
        self.source_entry = tk.Entry(master)
        self.source_entry.grid(row=0, column=1)
        self.source_button = tk.Button(master, text="Browse", command=self.browse_source_drives)
        self.source_button.grid(row=0, column=2)

        self.destination_label = tk.Label(master, text="Destination Drive:")
        self.destination_label.grid(row=1, column=0)
        self.destination_entry = tk.Entry(master)
        self.destination_entry.grid(row=1, column=1)
        self.destination_button = tk.Button(master, text="Browse", command=self.browse_destination_drives)
        self.destination_button.grid(row=1, column=2)

        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=600, mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=3)

        self.speed_label = tk.Label(master, text="Speed:")
        self.speed_label.grid(row=4, column=0)
        self.speed_var = tk.StringVar(master)
        self.speed_var.set("Normal")  # Default value
        self.speed_menu = tk.OptionMenu(master, self.speed_var, "Normal", "Fast", "Very Fast")
        self.speed_menu.grid(row=4, column=1)

        self.start_button = tk.Button(master, text="Start Transfer", command=self.start_transfer)
        self.start_button.grid(row=5, column=1)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_transfer, state=tk.DISABLED)
        self.stop_button.grid(row=5, column=0)
        self.continue_button = tk.Button(master, text="Continue", command=self.continue_transfer, state=tk.DISABLED)
        self.continue_button.grid(row=5, column=2)

        self.drive_select_window = None
        self.selected_drive = tk.StringVar()
        self.transfer_thread = None
        self.stop_flag = threading.Event()

    def browse_source_drives(self):
        self.browse_drives(self.source_entry)

    def browse_destination_drives(self):
        self.browse_drives(self.destination_entry)

    def browse_drives(self, entry):
        drives = self.get_drives()
        self.selected_drive.set('')

        self.drive_select_window = tk.Toplevel(self.master)
        self.drive_select_window.title("Select Drive")
        self.drive_select_window.geometry("200x200")
        self.drive_select_window.resizable(False, False)

        for i, drive in enumerate(drives):
            radio_button = tk.Radiobutton(self.drive_select_window, text=drive, variable=self.selected_drive, value=drive)
            radio_button.pack(anchor=tk.W)

        confirm_button = tk.Button(self.drive_select_window, text="Confirm", command=lambda: self.confirm_drive(entry))
        confirm_button.pack()

    def get_drives(self):
        drives = []
        for i in range(65, 91):
            drive_letter = chr(i) + ':'
            if os.path.exists(drive_letter):
                drives.append(drive_letter)
        return drives

    def confirm_drive(self, entry):
        chosen_drive = self.selected_drive.get()
        if chosen_drive:
            entry.delete(0, tk.END)
            entry.insert(0, chosen_drive)
            self.drive_select_window.destroy()
        else:
            messagebox.showwarning("Warning", "Please select a drive.")

    def start_transfer(self):
        source_path = self.source_entry.get()
        destination_path = self.destination_entry.get()

        if not source_path or not destination_path:
            tk.messagebox.showerror("Error", "Please select both source and destination drives.")
            return

        files = self.get_files_or_folders(source_path)

        if not files:
            tk.messagebox.showerror("Error", "No files or folders selected.")
            return

        self.stop_flag.clear()
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(files)

        self.stop_button.config(state=tk.NORMAL)
        self.continue_button.config(state=tk.DISABLED)
        self.transfer_thread = threading.Thread(target=self.transfer_files, args=(files, destination_path))
        self.transfer_thread.start()

    def transfer_files(self, files, destination_path):
        speed = self.speed_var.get()
        delay = 0

        if speed == "Fast":
            delay = 0.05
        elif speed == "Very Fast":
            delay = 0.01

        for file in files:
            if self.stop_flag.is_set():
                return

            self.transfer_file(file, destination_path)
            self.progress_bar["value"] += 1
            self.master.update_idletasks()
            time.sleep(delay)

        self.stop_button.config(state=tk.DISABLED)
        self.continue_button.config(state=tk.DISABLED)
        messagebox.showinfo("Info", "File transfer completed.")

    def stop_transfer(self):
        self.stop_flag.set()
        self.stop_button.config(state=tk.DISABLED)
        self.continue_button.config(state=tk.NORMAL)

    def continue_transfer(self):
        self.stop_flag.clear()
        self.stop_button.config(state=tk.NORMAL)
        self.continue_button.config(state=tk.DISABLED)

        if self.transfer_thread:
            self.transfer_thread = threading.Thread(target=self.transfer_files, args=(self.remaining_files, self.destination_entry.get()))
            self.transfer_thread.start()

    def transfer_file(self, source_file, destination_path):
        destination = os.path.join(destination_path, os.path.relpath(source_file, os.path.dirname(self.source_entry.get())))

        try:
            if os.path.isdir(source_file):
                shutil.copytree(source_file, destination)
            else:
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(source_file, destination)
        except Exception as e:
            messagebox.showerror("Error", f"Error copying {source_file} to {destination}: {e}")

    def get_files_or_folders(self, path):
        files_and_folders = []
        for root, dirs, files in os.walk(path):
            for name in files:
                files_and_folders.append(os.path.join(root, name))
            for name in dirs:
                files_and_folders.append(os.path.join(root, name))
        return files_and_folders

root = tk.Tk()
app = FileTransferApp(root)
root.mainloop()

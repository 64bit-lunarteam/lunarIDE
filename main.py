import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess

version = 'v0.1.0 Beta, Python Edition'

dark_bg = "#2E2E2E"
dark_fg = "#F8F8F2"
dark_text_bg = "#1E1E1E"
dark_text_fg = "#F8F8F2"
dark_cursor = "#F8F8F2"
line_number_bg = "#3A3A3A"
line_number_fg = "#BBBBBB"

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title(f"LunarIDE ~ {version}")
        self.root.configure(bg=dark_bg)
        self.filename = None

        self.create_widgets()
        self.create_menu()
        self.update_line_numbers()

    def create_widgets(self):
        self.text_frame = tk.Frame(self.root, bg=dark_bg)
        self.text_frame.pack(fill=tk.BOTH, expand=1)

        # Line numbers widget
        self.line_numbers = tk.Text(self.text_frame, width=5, padx=5, bg=line_number_bg, fg=line_number_fg,
                                    font=("Monokai", 12), state=tk.DISABLED, wrap=tk.NONE)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text editor with scrollbar
        self.text_area = tk.Text(self.text_frame, wrap=tk.WORD, font=("Monokai", 12),
                                 bg=dark_text_bg, fg=dark_text_fg, insertbackground=dark_cursor, undo=True)
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

        # Scrollbar for syncing scrolling
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self._sync_scroll)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.line_numbers.config(yscrollcommand=self.scrollbar.set)

        # Bind events for updates
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self._scroll_text)
        self.text_area.bind("<Button-1>", self.update_line_numbers)
        self.text_area.bind("<Return>", self.update_line_numbers)
        self.text_area.bind("<BackSpace>", self.update_line_numbers)
        self.text_area.bind("<Configure>", self.update_line_numbers)  # Window resizing
        self.text_area.bind("<MouseWheel>", self.update_line_numbers)  # Mouse scrolling
        self.text_area.bind("<Return>", self.update_line_numbers)  # Pressing Enter
        self.text_area.bind("<BackSpace>", self.update_line_numbers)  # Pressing Backspace
        self.text_area.bind("<Up>", self.update_line_numbers)  # Arrow keys
        self.text_area.bind("<Down>", self.update_line_numbers)
        self.text_area.bind("<Prior>", self.update_line_numbers)  # Page Up
        self.text_area.bind("<Next>", self.update_line_numbers)  # Page Down


    def create_menu(self):
        menubar = tk.Menu(self.root, bg=dark_bg, fg=dark_fg, activebackground="#444", activeforeground=dark_fg)

        file_menu = tk.Menu(menubar, tearoff=0, bg=dark_bg, fg=dark_fg, activebackground="#444", activeforeground=dark_fg)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0, bg=dark_bg, fg=dark_fg, activebackground="#444", activeforeground=dark_fg)
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=edit_menu)

        run_menu = tk.Menu(menubar, tearoff=0, bg=dark_bg, fg=dark_fg, activebackground="#444", activeforeground=dark_fg)
        run_menu.add_command(label="Run", command=self.run_code)
        menubar.add_cascade(label="Run", menu=run_menu)

        self.root.config(menu=menubar)

    def update_line_numbers(self, event=None):
        """ Updates the line numbers in the gutter, syncing them with text movement. """
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)

        num_lines = int(self.text_area.index(tk.END).split(".")[0])  # Count total lines
        line_number_string = "\n".join(str(i) for i in range(1, num_lines))

        self.line_numbers.insert(tk.END, line_number_string)
        self.line_numbers.config(state=tk.DISABLED)
            
        self._sync_scroll()  # Ensure scroll sync

        self.text_area.edit_modified(False)  # Reset modified flag


    def _sync_scroll(self, *args):
        """ Syncs scrolling between the text area and line numbers while preventing errors. """
        self.line_numbers.yview_moveto(self.text_area.yview()[0])



    def _scroll_text(self, event):
        """ Enables scrolling with the mouse wheel for both text & line numbers. """
        self.text_area.yview_scroll(-1 * (event.delta // 120), "units")
        self.line_numbers.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"

    def new_file(self):
        self.filename = None
        self.text_area.delete(1.0, tk.END)
        self.update_line_numbers()

    def open_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if self.filename:
            with open(self.filename, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.update_line_numbers()

    def save_file(self):
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_as_file()

    def save_as_file(self):
        self.filename = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("All Files", "*.*")])
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))

    def run_code(self):
        if not self.filename:
            messagebox.showerror("Error", "Save the file before running.")
            return
        
        command = f'python "{self.filename}"'
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        output_window = tk.Toplevel(self.root)
        output_window.title("Output")
        output_window.configure(bg=dark_bg)
        output_text = scrolledtext.ScrolledText(output_window, wrap=tk.WORD, font=("Monokai", 12),
                                                bg=dark_text_bg, fg=dark_text_fg, insertbackground=dark_cursor)
        output_text.pack(fill=tk.BOTH, expand=1)
        output_text.insert(tk.END, process.stdout + process.stderr)
        output_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeEditor(root)
    root.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CSVGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Graph Viewer")
        self.file_paths = []
        self.data_frames = []

        # Main layout frames
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for CSV loading and file display
        self.load_button = tk.Button(self.left_frame, text="Load CSV Files", command=self.load_files)
        self.load_button.pack(anchor=tk.W)

        self.file_list_label = tk.Label(self.left_frame, text="Loaded Files:")
        self.file_list_label.pack(anchor=tk.W, pady=(10, 0))

        self.file_listbox = tk.Listbox(self.left_frame, height=2, width=15)
        self.file_listbox.pack(anchor=tk.W, pady=(5, 10))

        # Graph options in the left panel
        self.graph_type_label = tk.Label(self.left_frame, text="Select Graph Type:")
        self.graph_type_label.pack(anchor=tk.W)

        self.graph_type = tk.StringVar(value="Line")
        self.graph_type_menu = tk.OptionMenu(self.left_frame, self.graph_type, "Line", "Bar", "Scatter")
        self.graph_type_menu.pack(anchor=tk.W, pady=(5, 10))

        self.column_label = tk.Label(self.left_frame, text="Select Columns:")
        self.column_label.pack(anchor=tk.W)

        self.column_listbox = tk.Listbox(self.left_frame, selectmode=tk.MULTIPLE, height=10, width=30)
        self.column_listbox.pack(anchor=tk.W, pady=(5, 10))

        self.plot_button = tk.Button(self.left_frame, text="Plot Graph", command=self.plot_graph)
        self.plot_button.pack(anchor=tk.W, pady=(10, 0))

        # Right panel for graph display
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if file_paths:
            self.file_paths = file_paths
            self.data_frames = [pd.read_csv(file) for file in self.file_paths]

            # Update file list
            self.file_listbox.delete(0, tk.END)
            for file in self.file_paths:
                self.file_listbox.insert(tk.END, file.split("/")[-1])  # Show only the file name

            # Update column list
            if self.data_frames:
                self.column_listbox.delete(0, tk.END)
                columns = self.data_frames[0].columns
                for col in columns:
                    self.column_listbox.insert(tk.END, col)

            messagebox.showinfo("Files Loaded", f"Loaded {len(self.file_paths)} files successfully.")

    def plot_graph(self):
        if not self.data_frames:
            messagebox.showwarning("No Files Loaded", "Please load CSV files first.")
            return

        # Get selected columns
        selected_indices = self.column_listbox.curselection()
        selected_columns = [self.column_listbox.get(i) for i in selected_indices]

        if not selected_columns:
            messagebox.showwarning("No Columns Selected", "Please select at least one column to plot.")
            return

        # Validate column selection for scatter plot
        if self.graph_type.get() == "Scatter" and len(selected_columns) < 2:
            messagebox.showwarning("Scatter Plot Error", "Scatter plot requires at least two columns: an x-axis and a y-axis.")
            return

        # Use the first column as x-axis if multiple columns are provided
        x_col = selected_columns[0] if len(selected_columns) > 1 else None
        y_cols = selected_columns[1:] if len(selected_columns) > 1 else [selected_columns[0]]

        # Plot each file's selected columns
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        for i, df in enumerate(self.data_frames):
            try:
                for y_col in y_cols:
                    # Ensure columns are numeric
                    if not pd.api.types.is_numeric_dtype(df[y_col]):
                        try:
                            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to convert column '{y_col}' to numeric.")
                            return

                    if self.graph_type.get() == "Line":
                        if x_col and pd.api.types.is_numeric_dtype(df[x_col]):
                            df.plot(kind='line', x=x_col, y=y_col, ax=ax, label=f"{y_col} (File {i+1})")
                        elif not x_col:
                            df[y_col].plot(kind='line', ax=ax, label=f"{y_col} (File {i+1})")
                    elif self.graph_type.get() == "Bar":
                        if x_col and pd.api.types.is_numeric_dtype(df[x_col]):
                            df.plot(kind='bar', x=x_col, y=y_col, ax=ax, label=f"{y_col} (File {i+1})")
                        elif not x_col:
                            df[y_col].plot(kind='bar', ax=ax, label=f"{y_col} (File {i+1})")
                    elif self.graph_type.get() == "Scatter":
                        if x_col and pd.api.types.is_numeric_dtype(df[x_col]):
                            df.plot(kind='scatter', x=x_col, y=y_col, ax=ax, label=f"{y_col} (File {i+1})")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to plot {y_col} in file {i+1}.\nError: {e}")
                return

        ax.legend()
        self.canvas.draw()


# Run the application
root = tk.Tk()
app = CSVGraphApp(root)
root.mainloop()

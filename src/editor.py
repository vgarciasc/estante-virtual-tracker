import json
import tkinter as tk
import datetime
import ctypes
from tkinter import messagebox
from main import get_current_prices

ctypes.windll.user32.SetProcessDPIAware()

class BookEditorApp:
    def __init__(self, root):
        self.data = json.load(open("data/database.json", "r"))
        self.root = root
        self.root.title("Estante Virtual Tracker - Editor")
        self.root.pack_propagate(False)

        self.listbox_frame = tk.Frame(root)
        self.listbox_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Listbox to display books
        self.book_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.SINGLE)
        self.book_listbox.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)

        self.add_entry_button = tk.Button(self.listbox_frame, text="Add Entry", command=self.add_entry)
        self.add_entry_button.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        self.listbox_frame.grid_rowconfigure(0, weight=1)
        self.listbox_frame.grid_columnconfigure(0, weight=1)

        # Frame to display book details
        self.detail_frame = tk.Frame(root)
        self.detail_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Labels and Entry widgets for book details
        self.name_label = tk.Label(self.detail_frame, text="Name:")
        self.name_label.grid(row=0, column=0, sticky=tk.W)
        self.name_entry = tk.Entry(self.detail_frame)
        self.name_entry.grid(row=0, column=1)

        self.author_label = tk.Label(self.detail_frame, text="Author:")
        self.author_label.grid(row=1, column=0, sticky=tk.W)
        self.author_entry = tk.Entry(self.detail_frame)
        self.author_entry.grid(row=1, column=1)

        self.search_query_label = tk.Label(self.detail_frame, text="Search Query:")
        self.search_query_label.grid(row=2, column=0, sticky=tk.W)
        self.search_query_entry = tk.Entry(self.detail_frame)
        self.search_query_entry.grid(row=2, column=1)

        self.active_label = tk.Label(self.detail_frame, text="Active:")
        self.active_label.grid(row=3, column=0, sticky=tk.W)
        self.active_var = tk.BooleanVar()
        self.active_checkbox = tk.Checkbutton(self.detail_frame, variable=self.active_var)
        self.active_checkbox.grid(row=3, column=1)

        self.price_label = tk.Label(self.detail_frame, text="Prices:")
        self.price_label.grid(row=4, column=0, sticky=tk.W)
        self.price_display = tk.Label(self.detail_frame, text="", fg="gray")
        self.price_display.grid(row=4, column=1, sticky=tk.W)

        self.last_updated_label = tk.Label(self.detail_frame, text="Last Updated:")
        self.last_updated_label.grid(row=5, column=0, sticky=tk.W)
        self.last_updated_display = tk.Label(self.detail_frame, text="", fg="gray")
        self.last_updated_display.grid(row=5, column=1, sticky=tk.W)

        self.update_prices_button = tk.Button(self.detail_frame, text="Update Prices", command=self.update_prices)
        self.update_prices_button.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)

        self.save_changes_button = tk.Button(self.detail_frame, text="Save Changes", command=self.save_changes)
        self.save_changes_button.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E)

        # Bind selection event to update details
        self.book_listbox.bind("<<ListboxSelect>>", self.update_details)

        # Populate the listbox with book names
        self.populate_listbox()

        width, height = 600, 600
        center_x, center_y = self.root.winfo_screenwidth() / 2, self.root.winfo_screenheight() / 2
        self.root.geometry(f"{width}x{height}+{int(center_x - width / 2)}+{int(center_y - height / 2)}")

        self.selected_idx = -1

    def populate_listbox(self):
        for book in self.data["books"]:
            self.book_listbox.insert(tk.END, book["name"])

    def clear_listbox(self):
        self.book_listbox.delete(0, tk.END)

    def update_json_data(self, field, value):
        # Get selected book index
        print(f"In updated_json_data, selected_idx = {self.selected_idx}")
        if self.selected_idx == -1:
            return

        # Update json_data with the new value
        selected_book = self.data["books"][self.selected_idx]
        selected_book[field] = value
        print(f"Updated {field} to {value}.")

    def update_details(self, event):
        # Get selected book index
        selected_index = self.book_listbox.curselection()
        if not selected_index:
            return
        self.selected_idx = selected_index[0]

        # Get selected book data
        selected_book = self.data["books"][selected_index[0]]

        # Update entry widgets with selected book details
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, selected_book["name"])

        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, selected_book["author"])

        self.search_query_entry.delete(0, tk.END)
        self.search_query_entry.insert(0, selected_book["search_query"])

        price_display_str = ", ".join([f"R$ {price:.2f}" for price in selected_book["prices"][:2]])
        if len(selected_book["prices"]) > 2:
            price_display_str += ", ..."
        self.price_display["text"] = price_display_str

        self.last_updated_display["text"] = selected_book['date_updated']

        self.active_var.set(selected_book["active"])

    def update_prices(self):
        # Get selected book index
        if self.selected_idx == -1:
            return

        # Get selected book data
        selected_book = self.data["books"][self.selected_idx]

        # Update prices
        selected_book["prices"] = get_current_prices(selected_book["search_query"])
        selected_book["date_updated"] = datetime.datetime.now().strftime("%Y-%m-%d")

        # Update price display
        price_display_str = ", ".join([f"R$ {price:.2f}" for price in selected_book["prices"][:2]])
        if len(selected_book["prices"]) > 2:
            price_display_str += ", ..."
        self.price_display["text"] = price_display_str

        # Display success message
        messagebox.showinfo("Success", f"Prices updated successfully for \"{selected_book['name']}\".")

    def add_entry(self):
        # Add a new entry with default values
        new_entry = {
            "name": "New Book",
            "author": "New Author",
            "active": True,
            "search_query": "new+book",
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d"),
            "date_updated": "",
            "prices": []
        }
        self.data["books"].append(new_entry)

        # Update the listbox
        self.book_listbox.insert(tk.END, new_entry["name"])

        # Select the new entry
        self.book_listbox.selection_clear(0, tk.END)
        self.book_listbox.selection_set(tk.END)
        self.selected_idx = len(self.data["books"]) - 1
        self.update_details(None)

        # Display success message
        messagebox.showinfo("Success", "New entry added successfully.")

    def save_changes(self):
        self.update_json_data("name", self.name_entry.get())
        self.update_json_data("author", self.author_entry.get())
        self.update_json_data("search_query", self.search_query_entry.get())
        self.update_json_data("active", self.active_var.get())

        with open("data/database.json", "w") as f:
            json.dump(self.data, f, indent=4)

        self.clear_listbox()
        self.populate_listbox()
        self.book_listbox.selection_clear(0, tk.END)
        self.book_listbox.selection_set(self.selected_idx)

        # Display success message
        messagebox.showinfo("Success", f"Changes saved successfully to \"{self.name_entry.get()}\".")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookEditorApp(root)
    root.mainloop()
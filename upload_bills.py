# file_path/app1.py

import flet as ft
import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to SQLite DB
def connect_db():
    try:
        conn = sqlite3.connect('invoices.db')
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection failed: {e}")
        return None

# Save invoice to database
def save_invoice(invoice_name, file_data):
    conn = connect_db()
    if conn is None:
        return "Failed to connect to database."
    
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO invoices (invoice_name, file) VALUES (?, ?)', (invoice_name, file_data))
        conn.commit()
        logging.info(f"Invoice '{invoice_name}' uploaded successfully.")
        return "success"
    except sqlite3.Error as e:
        logging.error(f"Error inserting invoice: {e}")
        return f"Database error: {e}"
    finally:
        conn.close()

# Main Flet app
def main(page: ft.Page):
    page.title = "Invoice Upload App with Error Handling"

    # Function to show a SnackBar
    def show_snackbar(message, bgcolor):
        snack_bar = ft.SnackBar(ft.Text(message), bgcolor=bgcolor)
        page.show_snack_bar(snack_bar)  # Show snack bar using the correct method

    invoice_name_input = ft.TextField(label="Invoice Name (Optional)", width=400)

    # File picker example with all modes
    picked_file = None

    def on_file_picked(e: ft.FilePickerResultEvent):
        nonlocal picked_file
        if e.files:
            picked_file = e.files[0]
            logging.info(f"File picked: {picked_file.name}")
            file_name_display.value = picked_file.name
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    file_name_display = ft.Text(value="No file selected", size=16)

    def upload_file(event):
        if picked_file is None:
            show_snackbar("Please select a file before uploading.", ft.colors.RED)
            return

        # Use file name as invoice name if invoice name is not provided
        invoice_name = invoice_name_input.value if invoice_name_input.value else picked_file.name

        try:
            with open(picked_file.path, "rb") as f:
                file_data = f.read()

            # Save the file data and invoice name to the database
            result = save_invoice(invoice_name, file_data)

            # Display appropriate message using snack bar
            if result == "success":
                show_snackbar("Invoice uploaded successfully!", ft.colors.GREEN)
            else:
                show_snackbar(result, ft.colors.RED)
        except Exception as e:
            logging.error(f"Error reading or saving file: {e}")
            show_snackbar(f"Error uploading file: {e}", ft.colors.RED)

    # Browse button icon and upload button
    file_picker_button = ft.IconButton(
        icon=ft.icons.FOLDER_OPEN,
        icon_size=30,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False),
        tooltip="Browse for file"
    )

    upload_button = ft.ElevatedButton("Upload Invoice", on_click=upload_file, icon=ft.icons.UPLOAD)

    # Layout
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        invoice_name_input,
                        file_picker_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row([file_name_display], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([upload_button], alignment=ft.MainAxisAlignment.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

# Run the app
ft.app(target=main)

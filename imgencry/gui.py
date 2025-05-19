import tkinter as tk
from tkinter import filedialog, messagebox
import requests

def upload_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if not file_path:
        return

    try:
        with open(file_path, "rb") as file:
            response = requests.post("http://127.0.0.1:8000/upload", files={"image": file})
        if response.ok:
            messagebox.showinfo("Success", "Image uploaded and encrypted.")
        else:
            messagebox.showerror("Error", response.text)
    except Exception as e:
        messagebox.showerror("Exception", str(e))

root = tk.Tk()
root.title("AES Image Encryptor")
root.geometry("300x150")

label = tk.Label(root, text="Upload and AES Encrypt an Image")
label.pack(pady=10)

button = tk.Button(root, text="Select Image", command=upload_image)
button.pack(pady=10)

root.mainloop()

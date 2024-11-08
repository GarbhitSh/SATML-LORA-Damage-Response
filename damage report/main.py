import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageGallery:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Image Gallery")
        self.root.geometry("500x600")  # Main window size

        # Frame for thumbnail display
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=1)

        # Canvas for scrolling
        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Scrollbar for the canvas
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        # Configuring the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # This frame will contain the thumbnails
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

        # Ensure the scrollregion is updated whenever the size of the frame changes.
        self.inner_frame.bind("<Configure>", self.onFrameConfigure)

        self.image_files = []  # List to store image paths
        self.load_images(os.getcwd() + "/real_images/")  # Load images automatically

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_images(self, directory):
        if not os.path.exists(directory):
            print("Directory does not exist:", directory)
            return

        # Clear previous images and paths
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.image_files.clear()

        # Load images from the directory
        files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        column = 0
        row = 0
        for image_file in files:
            image_path = os.path.join(directory, image_file)
            self.image_files.append(image_path)
            img = Image.open(image_path)
            img.thumbnail((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.inner_frame, image=img_tk, text=image_file, compound="bottom")
            lbl.image = img_tk  # Keep a reference to prevent garbage-collection
            lbl.grid(row=row, column=column, padx=5, pady=5)
            lbl.bind('<Button-1>', lambda e, idx=len(self.image_files)-1: self.open_full_image(idx))
            column += 1
            if column == 4:  # Adjust the number of columns based on your needs
                column = 0
                row += 1

    def open_full_image(self, index):
        new_window = tk.Toplevel(self.root)
        new_window.title("Image Viewer")
        new_window.geometry("400x400")
        
        img = Image.open(self.image_files[index])
        img_tk = ImageTk.PhotoImage(img)
        lbl = tk.Label(new_window, image=img_tk)
        lbl.image = img_tk
        lbl.pack()

        # Navigation and Swap Buttons
        self.btn_swap = tk.Button(new_window, text="Swap Image", command=lambda: self.swap_image(lbl, index, 'real'))
        self.btn_swap.pack(side=tk.LEFT)

        btn_close = tk.Button(new_window, text="Close", command=new_window.destroy)
        btn_close.pack(side=tk.LEFT)

    def swap_image(self, label, index, image_type):
        real_image_name = os.path.basename(self.image_files[index])
        if image_type == 'real':
            new_image_name = real_image_name.replace('real', 'segmented')
            new_image_path = os.path.join(os.getcwd(), 'segmented_images', new_image_name)
            new_image_type = 'segmented'
        else:
            new_image_name = real_image_name.replace('segmented', 'real')
            new_image_path = os.path.join(os.getcwd(), 'real_images', new_image_name)
            new_image_type = 'real'

        if os.path.exists(new_image_path):
            img = Image.open(new_image_path)
            img_tk = ImageTk.PhotoImage(img)
            label.configure(image=img_tk)
            label.image = img_tk  # Update the reference
            # Update the command of the button to toggle back on next click
            self.btn_swap.configure(command=lambda: self.swap_image(label, index, new_image_type))
        else:
            print("Image does not exist:", new_image_path)

# Main window setup
root = tk.Tk()
app = ImageGallery(root)
root.mainloop()
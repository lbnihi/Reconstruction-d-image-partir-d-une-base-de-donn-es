import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
    
    def create_widgets(self):
        self.load_image_button = tk.Button(self, text="Load Image", command=self.load_image)
        self.load_image_button.pack(side="left")
        self.load_database_button = tk.Button(self, text="Load Database", command=self.load_database_folder)
        self.load_database_button.pack(side="left")
        self.pixelate_button = tk.Button(self, text="Pixelate", command=self.create_window)
        self.pixelate_button.pack(side="left")
        self.quit_button = tk.Button(self, text="Quit", command=self.master.destroy)
        self.quit_button.pack(side="left")
    
    def load_image(self):
        file_path = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")))
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)

    def load_database_folder(self):
        folder_path = filedialog.askdirectory(initialdir="/", title="Select folder")
        if folder_path:
            self.database_images = []
            for filename in os.listdir(folder_path):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    image_path = os.path.join(folder_path, filename)
                    image = Image.open(image_path)
                    self.database_images.append(image)

    def find_best_matching_image(self, pixel_color):
        best_image = None
        smallest_distance = float("inf")
        for image in self.database_images:
            r, g, b = image.resize((1, 1)).getpixel((0, 0))
            distance = ((r - pixel_color[0]) ** 2) + ((g - pixel_color[1]) ** 2) + ((b - pixel_color[2]) ** 2)
            if distance < smallest_distance:
                smallest_distance = distance
                best_image = image
        return best_image
    
    def display_image(self, image):
        img = ImageTk.PhotoImage(image)
        self.panel = tk.Label(self.master, image=img)
        self.panel.image = img
        self.panel.pack(side="bottom", padx=10, pady=10)

    def create_window(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("Pixelate Image")
        self.window.geometry("500x500")

        self.panel = None
        self.result_image = None

        self.pixel_size = tk.IntVar()
        self.pixel_size.set(10)

        tk.Label(self.window, text="Enter pixel size:").pack(pady=5)
        tk.Entry(self.window, textvariable=self.pixel_size, width=10).pack(pady=5)

        #tk.Button(self.window, text="Load Image", command=self.load_image).pack(pady=5)
        tk.Button(self.window, text="Pixelate", command=self.pixelate_image).pack(pady=5)
        tk.Button(self.window, text="Save Image", command=self.save_image).pack(pady=5)
    def pixelate_image(self):
        if not self.image:
            messagebox.showerror("Error", "No image loaded!")
            return
        pixel_size = self.pixel_size.get()
        width, height = self.image.size
        new_image = Image.new('RGB', (width, height), (255, 255, 255))
        pixels = new_image.load()
        for i in range(0, width, pixel_size):
            for j in range(0, height, pixel_size):
                pixel_color = self.get_average_color(i, j, pixel_size)
                best_image = self.find_best_matching_image(pixel_color)
                best_image = best_image.resize((pixel_size, pixel_size))
                new_image.paste(best_image, (i, j))
        self.result_image = new_image
        self.display_image(self.result_image)

    def get_average_color(self, x, y, pixel_size):
        r_total = 0
        g_total = 0
        b_total = 0
        count = 0
        for i in range(x, x + pixel_size):
            for j in range(y, y + pixel_size):
                if i < self.image.size[0] and j < self.image.size[1]:
                    r, g, b = self.image.getpixel((i, j))
                    r_total += r
                    g_total += g
                    b_total += b
                    count += 1
        return (r_total // count, g_total // count, b_total // count)

    def save_image(self):
     if not self.result_image:
        messagebox.showerror("Error", "No image to save!")
        return
    
     file_types = [("JPEG files", "*.jpg"), ("PNG files", "*.png")]
     file_path = filedialog.asksaveasfilename(initialdir="/", title="Save file", filetypes=file_types, defaultextension=file_types)
     if not file_path:
        messagebox.showerror("Error", "No file selected!")
        return

    # Extract the extension from the file_path
     _, ext = os.path.splitext(file_path)
     if not ext:
        messagebox.showerror("Error", "File extension not provided!")
        return

    # Ensure the extension is valid
     if ext.lower() not in ['.jpg', '.jpeg', '.png']:
        messagebox.showerror("Error", "Unsupported file extension!")
        return

     try:
        # Determine the correct format based on the file extension
        format = 'JPEG' if ext.lower() in ['.jpg', '.jpeg'] else 'PNG'
        self.result_image.save(file_path, format=format)
        messagebox.showinfo("Success", "Image saved successfully!")
     except Exception as e:
        messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

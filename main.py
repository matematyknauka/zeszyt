import tkinter as tk
from tkinter import filedialog
import json
from PIL import Image, ImageDraw

class GridNotebook(tk.Frame):
    def __init__(self, parent, cell_size=40, grid_size=10000, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.cell_size = cell_size
        self.grid_size = grid_size
        self.drawing = False
        self.lines = []
        self.current_color = "black"
        self.current_line = []
        self.eraser_size = 10  # Rozmiar gumki

        # Scrollbars setup
        self.canvas = tk.Canvas(self, bg="white", width=600, height=400)
        self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Allow expansion of the canvas
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind mouse events for drawing
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        # Scroll events
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel_linux)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel_linux)

        self.create_grid()
        self.create_color_buttons()
        self.create_action_buttons()

    def create_grid(self):
        """Tworzy dużą siatkę."""
        # Rysowanie linii pionowych
        for i in range(0, self.grid_size, self.cell_size):
            self.canvas.create_line([(i, 0), (i, self.grid_size)], tag='grid_line', fill="lightgray")
        # Rysowanie linii poziomych
        for i in range(0, self.grid_size, self.cell_size):
            self.canvas.create_line([(0, i), (self.grid_size, i)], tag='grid_line', fill="lightgray")

        self.canvas.config(scrollregion=(0, 0, self.grid_size, self.grid_size))

    def create_color_buttons(self):
        """Tworzy przyciski do wyboru koloru."""
        colors = ["red", "blue", "green", "purple", "maroon", "pink", "brown", "orange"]
        color_frame = tk.Frame(self)
        color_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # Dodaj przycisk czarnego koloru
        btn_black = tk.Button(color_frame, bg="black", width=8, command=lambda: self.set_color("black"))
        btn_black.pack(side="left")

        for color in colors:
            btn = tk.Button(color_frame, bg=color, width=8, command=lambda c=color: self.set_color(c))
            btn.pack(side="left")

        # Dodaj przycisk gumki
        btn_eraser = tk.Button(color_frame, text="Gumka", width=8, command=self.use_eraser)
        btn_eraser.pack(side="left")

    def create_action_buttons(self):
        """Tworzy przyciski do cofania i zapisu."""
        action_frame = tk.Frame(self)
        action_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        undo_button = tk.Button(action_frame, text="Cofnij", command=self.undo_last)
        undo_button.pack(side="left", padx=5)

        save_button = tk.Button(action_frame, text="Zapisz", command=self.save_drawing)
        save_button.pack(side="left", padx=5)

        load_button = tk.Button(action_frame, text="Wczytaj", command=self.load_drawing)
        load_button.pack(side="left", padx=5)

        screenshot_button = tk.Button(action_frame, text="Zrzut ekranu", command=self.take_screenshot)
        screenshot_button.pack(side="left", padx=5)

    def set_color(self, color):
        """Ustawia aktualny kolor rysowania."""
        self.current_color = color

    def use_eraser(self):
        """Użyj gumki do mazania."""
        self.current_color = "white"  # Ustaw kolor gumki na biały

    def start_drawing(self, event):
        """Rozpocznij rysowanie."""
        self.drawing = True
        self.last_x, self.last_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.current_line = []

    def draw(self, event):
        """Rysuj podczas ruchu myszki."""
        if self.drawing:
            current_x, current_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

            # Rysuj linię lub użyj gumki
            if self.current_color == "white":  # Jeśli kolor to biały, użyj gumki
                x1 = current_x - self.eraser_size
                y1 = current_y - self.eraser_size
                x2 = current_x + self.eraser_size
                y2 = current_y + self.eraser_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="white")
            else:  # Rysowanie
                line_id = self.canvas.create_line(self.last_x, self.last_y, current_x, current_y, fill=self.current_color, width=2)
                self.current_line.append(line_id)

            self.last_x, self.last_y = current_x, current_y

    def stop_drawing(self, event):
        """Zatrzymaj rysowanie."""
        if self.drawing and self.current_line:
            self.lines.append(self.current_line)
        self.drawing = False

    def undo_last(self):
        """Cofnij ostatnią narysowaną linię."""
        if self.lines:
            last_line = self.lines.pop()
            for segment in last_line:
                self.canvas.delete(segment)

    def save_drawing(self):
        """Zapisz rysunek do pliku JSON."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        lines_data = []
        for line in self.lines:
            line_segments = []
            for line_id in line:
                coords = self.canvas.coords(line_id)
                color = self.canvas.itemcget(line_id, "fill")
                line_segments.append({"coords": coords, "color": color})
            lines_data.append(line_segments)

        with open(file_path, "w") as file:
            json.dump(lines_data, file)

    def load_drawing(self):
        """Wczytaj rysunek z pliku JSON."""
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        self.canvas.delete("all")
        self.create_grid()
        self.lines = []

        with open(file_path, "r") as file:
            lines_data = json.load(file)
            for line in lines_data:
                new_line = []
                for segment in line:
                    line_id = self.canvas.create_line(*segment["coords"], fill=segment["color"], width=2)
                    new_line.append(line_id)
                self.lines.append(new_line)

    def take_screenshot(self):
        """Zrób zrzut ekranu z aktualnego rysunku."""
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Tworzymy obraz
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Rysujemy linie siatki
        for i in range(0, self.grid_size, self.cell_size):
            draw.line([(i, 0), (i, height)], fill="lightgray")
        for i in range(0, self.grid_size, self.cell_size):
            draw.line([(0, i), (width, i)], fill="lightgray")

        # Rysujemy na obrazie linie z płótna
        for line in self.lines:
            for line_id in line:
                coords = self.canvas.coords(line_id)
                color = self.canvas.itemcget(line_id, "fill")
                draw.line(coords, fill=color, width=2)

        # Zapisujemy obraz do pliku
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if file_path:
            image.save(file_path)

    def on_mouse_wheel(self, event):
        """Zarządzanie przewijaniem myszą."""
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def on_mouse_wheel_linux(self, event):
        """Zarządzanie przewijaniem myszą w Linuxie."""
        if event.num == 4:  # Scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Scroll down
            self.canvas.yview_scroll(1, "units")


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Nieskończony zeszyt w kratkę")
    root.geometry("800x600")

    notebook = GridNotebook(root, cell_size=40, grid_size=10000)  # Ustawienie liczby linii na 10 000
    notebook.pack(fill="both", expand=True)

    root.mainloop()

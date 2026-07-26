import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

try:
    import winsound
    SOUND = True
except ImportError:
    SOUND = False


class AnalogTimer:

    def __init__(self, root):
        self.root = root
        self.root.title("Analog Timer")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#f2f2f2")
        self.root.bind(
            "<Escape>",
            lambda e: self.root.attributes("-fullscreen", False)
        )
        # Wyjście z pełnego ekranu klawiszem ESC
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.root.resizable(False, False)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        canvas_size = min(screen_w, screen_h) - 100

        self.canvas = tk.Canvas(
            root,
            bg="#f2f2f2",
            highlightthickness=0
        )

        self.canvas.pack(
            expand=True,
            fill="both"
        )

        # automatyczne przerysowanie po zmianie rozmiaru
        self.canvas.bind("<Configure>", self.resize_clock)


        self.cx = canvas_size // 2
        self.cy = canvas_size // 2
        self.radius = canvas_size // 2 - 40

        controls = tk.Frame(root, bg="#f2f2f2")
        controls.pack()

        tk.Label(
            controls,
            text="Czas:",
            bg="#f2f2f2",
            font=("Segoe UI",11)
        ).grid(row=0,column=0,padx=5)

        self.minutes = tk.IntVar(value=5)

        ttk.Combobox(
            controls,
            width=6,
            textvariable=self.minutes,
            values=list(range(1,61)),
            state="readonly"
        ).grid(row=0,column=1,padx=5)

        tk.Label(
            controls,
            text="min",
            bg="#f2f2f2",
            font=("Segoe UI",11)
        ).grid(row=0,column=2)

        tk.Button(
            controls,
            text="Start",
            width=10,
            command=self.start
        ).grid(row=0,column=3,padx=5)

        tk.Button(
            controls,
            text="Stop",
            width=10,
            command=self.stop
        ).grid(row=0,column=4,padx=5)

        tk.Button(
            controls,
            text="Reset",
            width=10,
            command=self.reset
        ).grid(row=0,column=5,padx=5)

        self.running=False

        self.total_seconds=300
        self.remaining=300

        self.start_time=None
        self.pause_time=0

        #self.radius=260
        #self.cx=325
        #self.cy=325

        self.draw_clock()

    def resize_clock(self, event):

        size = min(event.width, event.height)

        self.cx = event.width // 2
        self.cy = event.height // 2
        
        self.radius = size // 2 - 40

        self.draw_clock()

    def draw_clock(self):

        self.canvas.delete("all")

        cx = self.cx
        cy = self.cy
        r = self.radius

        # ===== Cień =====
        self.canvas.create_oval(
            cx-r+6, cy-r+8,
            cx+r+6, cy+r+8,
            fill="#d7d7d7",
            outline=""
        )

        # ===== Biała tarcza =====
        self.canvas.create_oval(
            cx-r, cy-r,
            cx+r, cy+r,
            fill="white",
            outline="#222222",
            width=2
        )

        # ===== Postęp =====
        elapsed = self.total_seconds - self.remaining
        fraction = elapsed / self.total_seconds if self.total_seconds else 0

        if fraction < 0.50:
            progress_color = "#5CB85C"
        elif fraction < 0.80:
            progress_color = "#F0AD4E"
        else:
            progress_color = "#D9534F"

        self.canvas.create_arc(
            cx-r,
            cy-r,
            cx+r,
            cy+r,
            start=90,
            extent=-360*fraction,
            fill=progress_color,
            outline=""
        )

        # ===== Ponownie tarcza aby powstał pierścień =====
        self.canvas.create_oval(
            cx-r+80,
            cy-r+80,
            cx+r-80,
            cy+r-80,
            fill="white",
            outline=""
        )

        # ===== Kreski =====
        for i in range(60):

            angle = math.radians(i*6-90)

            if i % 5 == 0:
                inner = r-20
                width = 2
            else:
                inner = r-10
                width = 1

            x1 = cx + inner*math.cos(angle)
            y1 = cy + inner*math.sin(angle)

            x2 = cx + r*math.cos(angle)
            y2 = cy + r*math.sin(angle)

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                width=width,
                fill="#303030"
            )

        # ===== Cyfrowy timer =====
        m = int(self.remaining)//60
        s = int(self.remaining)%60

        font_size = int(self.radius / 7)

        self.canvas.create_text(
            cx,
            cy-35,
            text=f"{m:02}:{s:02}",
            font=("Segoe UI", font_size, "bold"),
            fill="#222222"
        )

        self.canvas.create_text(
            cx,
            cy+48,
            text="POZOSTAŁO",
            font=("Segoe UI", int(self.radius/18)),
            fill="#777777"
        )

        # ===== Wskazówka =====
        angle = math.radians(-90 + fraction*360)

        x = cx + (r-18)*math.cos(angle)
        y = cy + (r-18)*math.sin(angle)

        self.canvas.create_line(
            cx,
            cy,
            x,
            y,
            width=3,
            fill="black",
            capstyle=tk.ROUND
        )

        # ===== Środek =====
        #self.canvas.create_oval(
        #   cx-7,
        #   cy-7,
        #   cx+7,
        #   cy+7,
        #   fill="#111111",
        #   outline=""
        #)

    def update(self):

        if not self.running:
            return

        elapsed = time.perf_counter() - self.start_time
        self.remaining = max(0, self.total_seconds - elapsed)

        self.draw_clock()

        m = int(self.remaining) // 60
        s = int(self.remaining) % 60

        if self.remaining > 0:

            self.root.after(16, self.update)   # około 60 FPS

        else:

            self.running = False
            self.remaining = 0

            self.start_time = None
            self.pause_time = 0

            self.draw_clock()

            if SOUND:
                winsound.Beep(1000, 700)

            messagebox.showinfo(
                "Timer",
                "Czas minął!"
            )

    def start(self):

        if self.running:
            return

        # Pierwsze uruchomienie
        if self.start_time is None:
            self.start_time = time.perf_counter()

        # Wznowienie po pauzie
        else:
            self.start_time = time.perf_counter() - self.pause_time

        self.running = True
        self.update()


    def stop(self):

        if self.running:

            self.running = False
            self.pause_time = time.perf_counter() - self.start_time


    def reset(self):

        self.running = False

        self.total_seconds = self.minutes.get() * 60
        self.remaining = self.total_seconds

        self.start_time = None
        self.pause_time = 0

        self.draw_clock()


root = tk.Tk()
app = AnalogTimer(root)
app.reset()
root.mainloop()
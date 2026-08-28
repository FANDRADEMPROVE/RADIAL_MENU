"""
Radial Menu - Menu de anillo activable por hotkey de teclado
(incluyendo teclas F13-F24 que muchos mouse gaming permiten asignar
a un boton fisico, sin necesitar permisos de administrador).

Requiere (se instalan solos via requirements.txt):
    keyboard      -> detectar hotkeys globales y enviar atajos
    Pillow        -> cargar iconos PNG (y SVG si hay cairosvg)
    pywin32       -> lanzar programas de forma mas robusta en Windows

Autor: generado para Francisco
"""

import json
import math
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import font as tkfont

import keyboard
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

ICON_SIZE = 48
BG_COLOR = "#1e1e1e"
RING_COLOR = "#2d2d30"
HOVER_COLOR = "#0e639c"
TEXT_COLOR = "#ffffff"
TRANSPARENT_KEY = "#010101"  # color usado como "transparente" en Windows


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_icon(path, size=ICON_SIZE):
    """Carga un PNG (o SVG si cairosvg esta disponible) como imagen Tk."""
    full_path = path if os.path.isabs(path) else os.path.join(BASE_DIR, path)
    try:
        if full_path.lower().endswith(".svg"):
            import cairosvg
            png_bytes = cairosvg.svg2png(url=full_path, output_width=size, output_height=size)
            import io
            img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        else:
            img = Image.open(full_path).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        # Icono de respaldo: circulo simple si no se encuentra el archivo
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)


class RadialMenu:
    def __init__(self, items, radius, inner_radius, on_close=None, title="Menu"):
        self.items = items
        self.radius = radius
        self.inner_radius = inner_radius
        self.on_close = on_close
        self.title_text = title

        self.root = tk.Toplevel()
        self.root.overrideredirect(True)          # sin bordes de ventana
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT_KEY)
        self.root.attributes("-transparentcolor", TRANSPARENT_KEY)

        size = radius * 2 + 40
        # Centrar en la posicion actual del cursor
        px, py = self.root.winfo_pointerxy()
        x = px - size // 2
        y = py - size // 2
        self.root.geometry(f"{size}x{size}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.root, width=size, height=size,
            bg=TRANSPARENT_KEY, highlightthickness=0
        )
        self.canvas.pack()

        self.center = (size // 2, size // 2)
        self.icon_refs = []  # evitar garbage collection de imagenes
        self.item_boxes = []  # (x1,y1,x2,y2,index)
        self.hover_index = None

        self._draw()

        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Button-1>", self._on_click)
        self.root.bind("<Escape>", lambda e: self._close())
        self.root.bind("<FocusOut>", lambda e: self._close())
        self.root.focus_force()

    def _draw(self):
        cx, cy = self.center
        n = len(self.items)
        if n == 0:
            return
        angle_step = 360 / n

        # Circulo central (indicador)
        self.canvas.create_oval(
            cx - self.inner_radius, cy - self.inner_radius,
            cx + self.inner_radius, cy + self.inner_radius,
            fill=RING_COLOR, outline="#3f3f46", width=2
        )
        self.canvas.create_text(
            cx, cy, text=self.title_text, fill=TEXT_COLOR,
            font=("Segoe UI", 9, "bold"), width=self.inner_radius * 1.6
        )

        for i, item in enumerate(self.items):
            angle_deg = -90 + i * angle_step  # empezar arriba
            angle_rad = math.radians(angle_deg)
            ix = cx + math.cos(angle_rad) * self.radius
            iy = cy + math.sin(angle_rad) * self.radius

            # Sector visual (cuna) detras del icono
            a0 = angle_deg - angle_step / 2
            a1 = angle_deg + angle_step / 2
            self.canvas.create_arc(
                cx - self.radius - 30, cy - self.radius - 30,
                cx + self.radius + 30, cy + self.radius + 30,
                start=-a1, extent=angle_step,
                fill=RING_COLOR, outline=BG_COLOR, width=2,
                style=tk.PIESLICE
            )

            icon_img = load_icon(item.get("icon", ""))
            self.icon_refs.append(icon_img)
            self.canvas.create_image(ix, iy, image=icon_img)

            label = item.get("label", "")
            self.canvas.create_text(
                ix, iy + ICON_SIZE / 2 + 12, text=label,
                fill=TEXT_COLOR, font=("Segoe UI", 8)
            )

            box_r = ICON_SIZE
            self.item_boxes.append((ix - box_r, iy - box_r, ix + box_r, iy + box_r, i))

        # Redibujar el circulo central encima de los sectores
        self.canvas.create_oval(
            cx - self.inner_radius, cy - self.inner_radius,
            cx + self.inner_radius, cy + self.inner_radius,
            fill=RING_COLOR, outline="#3f3f46", width=2
        )
        self.canvas.create_text(
            cx, cy, text=self.title_text, fill=TEXT_COLOR,
            font=("Segoe UI", 9, "bold"), width=self.inner_radius * 1.6
        )

    def _index_at(self, x, y):
        for (x1, y1, x2, y2, idx) in self.item_boxes:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return idx
        return None

    def _on_motion(self, event):
        idx = self._index_at(event.x, event.y)
        if idx != self.hover_index:
            self.hover_index = idx
            # (Aqui se podria resaltar el sector activo redibujando)

    def _on_click(self, event):
        idx = self._index_at(event.x, event.y)
        if idx is not None:
            self._select(idx)
        else:
            self._close()

    def _select(self, idx):
        item = self.items[idx]
        self._close()
        execute_action(item)

    def _close(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        if self.on_close:
            self.on_close()


def execute_action(item):
    """Ejecuta la accion asociada a una opcion del menu (o abre su submenu)."""
    item_type = item.get("type")
    action = item.get("action", "")

    if item_type == "submenu":
        submenu_items = item.get("submenu", [])
        if submenu_items:
            RadialMenu(submenu_items, radius=150, inner_radius=50,
                       title=item.get("label", "Submenu"))
        return

    if item_type == "program":
        try:
            subprocess.Popen(action, shell=True)
        except Exception as e:
            print(f"Error abriendo programa: {e}")

    elif item_type == "script":
        try:
            if action.lower().endswith(".vbs"):
                subprocess.Popen(["wscript.exe", action], shell=True)
            elif action.lower().endswith(".ps1"):
                subprocess.Popen(
                    ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", action],
                    shell=True
                )
            elif action.lower().endswith(".bat") or action.lower().endswith(".cmd"):
                subprocess.Popen(action, shell=True)
            else:
                subprocess.Popen(action, shell=True)
        except Exception as e:
            print(f"Error ejecutando script: {e}")

    elif item_type == "shortcut":
        try:
            keyboard.send(action)
        except Exception as e:
            print(f"Error enviando atajo: {e}")

    elif item_type == "macro":
        try:
            keyboard.write(action)
        except Exception as e:
            print(f"Error escribiendo macro: {e}")


class App:
    def __init__(self):
        self.config = load_config()
        self.root = tk.Tk()
        self.root.withdraw()  # ventana raiz invisible, solo controla el loop
        self.menu_open = False

        hotkey = self.config.get("hotkey", "f13")
        keyboard.add_hotkey(hotkey, self.open_menu)
        print(f"Radial Menu activo. Presiona '{hotkey}' para abrir el menu. "
              f"Cierra esta ventana de consola para salir.")

    def open_menu(self):
        if self.menu_open:
            return
        self.menu_open = True

        def _close():
            self.menu_open = False

        # Debe correr en el hilo principal de Tk
        self.root.after(0, lambda: RadialMenu(
            self.config["items"],
            radius=self.config.get("ring_radius", 170),
            inner_radius=self.config.get("inner_radius", 55),
            on_close=_close,
            title="Menu"
        ))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()

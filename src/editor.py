"""
Editor grafico para configurar el Menu Anillo.
Permite agregar/editar/borrar opciones del anillo principal y de
un submenu por opcion, eligiendo icono (PNG/SVG), tipo de accion
y el valor de esa accion. Guarda todo en config.json.
"""

import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
ICONS_DIR = os.path.join(BASE_DIR, "icons")

os.makedirs(ICONS_DIR, exist_ok=True)

ACTION_TYPES = [
    ("program", "Ejecutar programa (.exe)"),
    ("script", "Ejecutar script (.vbs/.ps1/.bat)"),
    ("shortcut", "Atajo de teclado (ej. ctrl+c)"),
    ("macro", "Macro de texto (escribe texto)"),
    ("submenu", "Abrir submenu"),
]
TYPE_LABELS = {k: v for k, v in ACTION_TYPES}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"hotkey": "f13", "ring_radius": 170, "inner_radius": 55, "items": []}


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class ItemEditor(tk.Toplevel):
    """Ventana para crear/editar una opcion (del anillo o de un submenu)."""

    def __init__(self, master, item=None, allow_submenu=True, on_save=None):
        super().__init__(master)
        self.title("Editar opcion")
        self.resizable(False, False)
        self.on_save = on_save
        self.item = item or {"label": "", "icon": "", "type": "program",
                              "action": "", "submenu": []}
        self.icon_path = self.item.get("icon", "")

        pad = {"padx": 10, "pady": 6}

        tk.Label(self, text="Nombre:").grid(row=0, column=0, sticky="e", **pad)
        self.label_var = tk.StringVar(value=self.item.get("label", ""))
        tk.Entry(self, textvariable=self.label_var, width=35).grid(row=0, column=1, columnspan=2, **pad)

        tk.Label(self, text="Icono (PNG/SVG):").grid(row=1, column=0, sticky="e", **pad)
        self.icon_label = tk.Label(self, text=os.path.basename(self.icon_path) or "(sin icono)")
        self.icon_label.grid(row=1, column=1, sticky="w", **pad)
        tk.Button(self, text="Elegir...", command=self._choose_icon).grid(row=1, column=2, **pad)

        tk.Label(self, text="Tipo de accion:").grid(row=2, column=0, sticky="e", **pad)
        self.type_var = tk.StringVar(value=self.item.get("type", "program"))
        type_values = [label for _, label in ACTION_TYPES]
        if not allow_submenu:
            type_values = [label for key, label in ACTION_TYPES if key != "submenu"]
        self.type_combo = ttk.Combobox(self, values=type_values, state="readonly", width=32)
        current_label = TYPE_LABELS.get(self.type_var.get(), type_values[0])
        self.type_combo.set(current_label)
        self.type_combo.grid(row=2, column=1, columnspan=2, **pad)
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        self.action_label = tk.Label(self, text="Accion:")
        self.action_label.grid(row=3, column=0, sticky="e", **pad)
        self.action_var = tk.StringVar(value=self.item.get("action", ""))
        self.action_entry = tk.Entry(self, textvariable=self.action_var, width=35)
        self.action_entry.grid(row=3, column=1, **pad)
        self.action_browse_btn = tk.Button(self, text="Buscar...", command=self._browse_action)
        self.action_browse_btn.grid(row=3, column=2, **pad)

        self.help_label = tk.Label(self, text="", fg="#555", wraplength=320, justify="left")
        self.help_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=12)
        tk.Button(btn_frame, text="Guardar", width=12, command=self._save).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancelar", width=12, command=self.destroy).pack(side="left", padx=6)

        self._update_action_ui()
        self.grab_set()

    def _on_type_change(self, event=None):
        self._update_action_ui()

    def _current_type_key(self):
        label = self.type_combo.get()
        for key, lbl in ACTION_TYPES:
            if lbl == label:
                return key
        return "program"

    def _update_action_ui(self):
        t = self._current_type_key()
        texts = {
            "program": ("Ruta del .exe:", True, "Ej: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
            "script": ("Ruta del script:", True, "Acepta .vbs, .ps1, .bat/.cmd"),
            "shortcut": ("Atajo (formato 'ctrl+c'):", False, "Usa nombres tipo: ctrl, alt, shift, win, f1..f24"),
            "macro": ("Texto a escribir:", False, "El texto se escribira tal cual, como si lo tecleraras"),
            "submenu": ("(sin accion, se abre un submenu)", False, "Guarda esta opcion y luego usa 'Editar submenu' en la lista principal"),
        }
        label_text, show_browse, help_text = texts.get(t, ("Accion:", True, ""))
        self.action_label.config(text=label_text)
        self.help_label.config(text=help_text)
        if t == "submenu":
            self.action_entry.config(state="disabled")
            self.action_browse_btn.config(state="disabled")
        else:
            self.action_entry.config(state="normal")
            self.action_browse_btn.config(state="normal" if show_browse else "disabled")

    def _browse_action(self):
        t = self._current_type_key()
        if t == "program":
            path = filedialog.askopenfilename(title="Selecciona el ejecutable",
                                               filetypes=[("Ejecutables", "*.exe"), ("Todos", "*.*")])
        elif t == "script":
            path = filedialog.askopenfilename(title="Selecciona el script",
                                               filetypes=[("Scripts", "*.vbs;*.ps1;*.bat;*.cmd"), ("Todos", "*.*")])
        else:
            path = ""
        if path:
            self.action_var.set(path)

    def _choose_icon(self):
        path = filedialog.askopenfilename(
            title="Selecciona un icono",
            filetypes=[("Imagenes", "*.png;*.svg"), ("Todos", "*.*")]
        )
        if not path:
            return
        dest_name = os.path.basename(path)
        dest_path = os.path.join(ICONS_DIR, dest_name)
        try:
            if os.path.abspath(path) != os.path.abspath(dest_path):
                shutil.copy(path, dest_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el icono:\n{e}")
            return
        self.icon_path = os.path.join("icons", dest_name)
        self.icon_label.config(text=dest_name)

    def _save(self):
        label = self.label_var.get().strip()
        if not label:
            messagebox.showwarning("Falta nombre", "Ponle un nombre a la opcion.")
            return
        t = self._current_type_key()
        action = self.action_var.get().strip() if t != "submenu" else ""

        self.item["label"] = label
        self.item["icon"] = self.icon_path
        self.item["type"] = t
        self.item["action"] = action
        if "submenu" not in self.item:
            self.item["submenu"] = []
        if t == "submenu" and self.item.get("submenu") is None:
            self.item["submenu"] = []

        if self.on_save:
            self.on_save(self.item)
        self.destroy()


class SubmenuEditor(tk.Toplevel):
    """Ventana para administrar la lista de opciones dentro de un submenu."""

    def __init__(self, master, parent_item, on_close=None, on_change=None):
        super().__init__(master)
        self.title(f"Submenu de: {parent_item.get('label', '')}")
        self.geometry("420x380")
        self.parent_item = parent_item
        self.on_close = on_close
        self.on_change = on_change  # se llama cada vez que hay un cambio (guardado inmediato)
        if "submenu" not in self.parent_item or self.parent_item["submenu"] is None:
            self.parent_item["submenu"] = []

        tk.Label(self, text=f"Opciones dentro de '{parent_item.get('label','')}'",
                 font=("Segoe UI", 10, "bold")).pack(pady=8)

        self.listbox = tk.Listbox(self, width=50, height=12)
        self.listbox.pack(padx=10, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Agregar", width=10, command=self._add).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Editar", width=10, command=self._edit).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Eliminar", width=10, command=self._delete).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text="Subir", width=10, command=lambda: self._move(-1)).grid(row=1, column=0, padx=4, pady=4)
        tk.Button(btn_frame, text="Bajar", width=10, command=lambda: self._move(1)).grid(row=1, column=1, padx=4, pady=4)

        tk.Button(self, text="Cerrar", width=12, command=self._close).pack(pady=6)

        self._refresh()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.grab_set()

    def _refresh(self):
        self.listbox.delete(0, tk.END)
        for it in self.parent_item["submenu"]:
            tipo = TYPE_LABELS.get(it.get("type", ""), it.get("type", ""))
            self.listbox.insert(tk.END, f"{it.get('label','(sin nombre)')}  —  {tipo}")

    def _notify_change(self):
        """Guarda config.json de inmediato tras cualquier cambio en el submenu."""
        if self.on_change:
            self.on_change()

    def _add(self):
        def _saved(new_item):
            self.parent_item["submenu"].append(new_item)
            self._refresh()
            self._notify_change()
        ItemEditor(self, allow_submenu=False, on_save=_saved)

    def _edit(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        item = self.parent_item["submenu"][idx]

        def _saved(updated):
            self.parent_item["submenu"][idx] = updated
            self._refresh()
            self._notify_change()
        ItemEditor(self, item=item, allow_submenu=False, on_save=_saved)

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar esta opcion del submenu?"):
            del self.parent_item["submenu"][idx]
            self._refresh()
            self._notify_change()

    def _move(self, direction):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        items = self.parent_item["submenu"]
        if 0 <= new_idx < len(items):
            items[idx], items[new_idx] = items[new_idx], items[idx]
            self._refresh()
            self.listbox.selection_set(new_idx)
            self._notify_change()

    def _close(self):
        if self.on_close:
            self.on_close()
        self.destroy()


class MainEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Menu Anillo")
        self.geometry("560x520")
        self.config_data = load_config()

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)
        tk.Label(top, text="Hotkey de teclado para abrir el menu:").pack(side="left")
        self.hotkey_var = tk.StringVar(value=self.config_data.get("hotkey", "f13"))
        tk.Entry(top, textvariable=self.hotkey_var, width=15).pack(side="left", padx=8)
        tk.Label(top, text="(ej: ctrl+shift+alt+space, f13, ctrl+alt+space)").pack(side="left")

        tk.Label(self, text="Opciones del anillo principal:",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        self.listbox = tk.Listbox(self, width=70, height=14)
        self.listbox.pack(padx=10, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Agregar opcion", width=14, command=self._add).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Editar", width=14, command=self._edit).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Eliminar", width=14, command=self._delete).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text="Editar submenu", width=14, command=self._edit_submenu).grid(row=0, column=3, padx=4)

        move_frame = tk.Frame(self)
        move_frame.pack(pady=4)
        tk.Button(move_frame, text="Subir", width=14, command=lambda: self._move(-1)).grid(row=0, column=0, padx=4)
        tk.Button(move_frame, text="Bajar", width=14, command=lambda: self._move(1)).grid(row=0, column=1, padx=4)

        tk.Button(self, text="Guardar configuracion (config.json)", bg="#0e639c", fg="white",
                  width=32, command=self._save_all).pack(pady=14)

        self._refresh()

    def _refresh(self):
        self.listbox.delete(0, tk.END)
        for it in self.config_data["items"]:
            tipo = TYPE_LABELS.get(it.get("type", ""), it.get("type", ""))
            extra = ""
            if it.get("type") == "submenu":
                n = len(it.get("submenu", []))
                extra = f" ({n} opcion(es) dentro)"
            self.listbox.insert(tk.END, f"{it.get('label','(sin nombre)')}  —  {tipo}{extra}")

    def _add(self):
        def _saved(new_item):
            self.config_data["items"].append(new_item)
            self._refresh()
        ItemEditor(self, allow_submenu=True, on_save=_saved)

    def _edit(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        item = self.config_data["items"][idx]

        def _saved(updated):
            self.config_data["items"][idx] = updated
            self._refresh()
        ItemEditor(self, item=item, allow_submenu=True, on_save=_saved)

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar esta opcion del anillo?"):
            del self.config_data["items"][idx]
            self._refresh()

    def _edit_submenu(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        item = self.config_data["items"][idx]
        if item.get("type") != "submenu":
            messagebox.showinfo("Aviso", "Esta opcion no es de tipo 'submenu'. "
                                          "Cambia su

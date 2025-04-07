# GrasCurveEditor: сохраняет исходные комментарии 1:1

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import numpy as np

class GrasEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("GRAS Curve Editor")
        self.params = [{} for _ in range(7)]
        self.original_params = []
        self.comments = {}      # {addr: '# comment'}
        self.raw_lines = {}     # {addr: original_line} — для идеального сохранения
        self.selected_zone = tk.IntVar(value=0)
        self.entries = {}

        self.setup_ui()

    def setup_ui(self):
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.load_file)
        file_menu.add_command(label="Save As", command=self.save_file)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

        top = tk.Frame(self.root)
        top.pack(pady=5)
        tk.Label(top, text="Zone:").pack(side=tk.LEFT)
        self.zone_combo = ttk.Combobox(top, textvariable=self.selected_zone, values=list(range(7)), width=5)
        self.zone_combo.pack(side=tk.LEFT)
        self.zone_combo.bind("<<ComboboxSelected>>", lambda e: self.load_zone())

        grid = tk.Frame(self.root)
        grid.pack()
        self.entries = {k: [] for k in ('alpha', 'beta')}

        for i in range(4):
            for kind in ('alpha', 'beta'):
                lbl = tk.Label(grid, text=f"{kind}[{i}]:")
                lbl.grid(row=i, column=0 if kind=='alpha' else 2, sticky='e')
                ent = tk.Entry(grid, width=6)
                ent.grid(row=i, column=1 if kind=='alpha' else 3)
                self.entries[kind].append(ent)

        tk.Button(self.root, text="Update Curve", command=self.update_graph).pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not path:
            return

        with open(path, "r") as f:
            text = f.readlines()

        pattern = re.compile(r'\((31[6-9A-F][0-9A-F]),\s*([0-9A-Fa-f]{4}),\s*2\)\s*(#.*)?')
        zone_map = [{} for _ in range(7)]
        self.comments.clear()
        self.raw_lines.clear()

        zone_starts = [0x3164 + i * 0x12 for i in range(7)]

        for line in text:
            match = pattern.match(line.strip())
            if match:
                reg, val, comment = match.groups()
                addr = int(reg, 16)
                value = int(val, 16)
                self.raw_lines[addr] = line.strip()  # сохраняем строку как есть
                if comment:
                    self.comments[addr] = comment.strip()

                zone = None
                for z, start in enumerate(zone_starts):
                    if start <= addr < start + 0x12:
                        zone = z
                        break

                if zone is not None:
                    offset = addr - zone_starts[zone]
                    index = offset // 2

                    z = zone_map[zone]
                    if 'tmpr' not in z:
                        z['tmpr'] = 0
                    if 'alpha' not in z:
                        z['alpha'] = [0]*4
                    if 'beta' not in z:
                        z['beta'] = [0]*4

                    if index == 0:
                        z['tmpr'] = value
                    elif 1 <= index <= 4:
                        z['alpha'][index - 1] = value
                    elif 5 <= index <= 8:
                        z['beta'][index - 5] = value

        self.params = zone_map
        self.original_params = []
        for z in zone_map:
            tmpr = z.get('tmpr', 0)
            alpha = z.get('alpha', [0]*4)
            beta = z.get('beta', [0]*4)
            self.original_params.append({'tmpr': tmpr, 'alpha': alpha[:], 'beta': beta[:]})

        self.load_zone()
        self.update_graph()

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return

        lines = ["Addr=2D", "WBlock(0, GRAS_Custom) = ["]
        for i, z in enumerate(self.params):
            base = 0x3164 + i * 0x12
            tmpr = z.get('tmpr', 0)
            alpha = z.get('alpha', [0] * 4)
            beta = z.get('beta', [0] * 4)

            addr_list = [(base, tmpr)] + \
                        [(base + 2 + 2 * j, alpha[j]) for j in range(4)] + \
                        [(base + 10 + 2 * j, beta[j]) for j in range(4)]

            for addr, val in addr_list:
                if addr in self.raw_lines:
                    # если строка не изменилась — сохранить как есть
                    old = self.raw_lines[addr]
                    expected = f"({addr:04X}, {val:04X}, 2)"
                    if expected in old:
                        lines.append(old)
                        continue

                # иначе — генерируем новую строку с сохранением комментария
                comment = f" {self.comments.get(addr, '')}".rstrip()
                lines.append(f"    ({addr:04X}, {val:04X}, 2){f' {comment}' if comment else ''}")

        lines.append("]")
        with open(path, "w") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Saved", f"File saved to {path}")

    def load_zone(self):
        z = self.params[self.selected_zone.get()]
        if 'alpha' not in z:
            z['alpha'] = [0] * 4
        if 'beta' not in z:
            z['beta'] = [0] * 4

        for i in range(4):
            self.entries['alpha'][i].delete(0, tk.END)
            self.entries['alpha'][i].insert(0, f"{z['alpha'][i]}")
            self.entries['beta'][i].delete(0, tk.END)
            self.entries['beta'][i].insert(0, f"{z['beta'][i]}")
        self.update_graph()

    def update_graph(self):
        z = self.params[self.selected_zone.get()]
        for i in range(4):
            try:
                z['alpha'][i] = int(self.entries['alpha'][i].get())
                z['beta'][i] = int(self.entries['beta'][i].get())
            except ValueError:
                continue

        a = np.mean(z['alpha']) / 256
        b = np.mean(z['beta']) / 256
        x = np.linspace(0, 1, 256)
        y = x * (a * x + b)

        self.ax.clear()
        self.ax.plot(x, y, label="Modified")

        orig = self.original_params[self.selected_zone.get()]
        a0 = np.mean(orig['alpha']) / 256
        b0 = np.mean(orig['beta']) / 256
        y0 = x * (a0 * x + b0)
        self.ax.plot(x, y0, label="Original", linestyle='--')

        self.ax.set_title(f"Zone {self.selected_zone.get()} Curve")
        self.ax.set_xlabel("Input Brightness")
        self.ax.set_ylabel("Output")
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = GrasEditor(root)
    root.mainloop()

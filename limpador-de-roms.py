import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict

# Banco de extensões atualizado
EXTENSIONS_DB = {
    "Comuns": [".zip", ".7z", ".rar"],
    "Nintendo": [".nes", ".sfc", ".smc", ".n64", ".z64", ".gb", ".gbc", ".gba", ".nds"],
    "Sega": [".sms", ".md", ".smd", ".gen", ".gg", ".cdi", ".gdi"],
    "Sony": [".bin", ".cue", ".iso", ".chd", ".cso"],
    "Atari": [".a26", ".bin"]
}

def calculate_hash(path, block_size=65536):
    hasher = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for byte_block in iter(lambda: f.read(block_size), b""):
                hasher.update(byte_block)
        return hasher.hexdigest()
    except:
        return None

class RomCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Limpador de ROMs Duplicadas - Versão 3.0")
        self.root.geometry("950x750")
        
        self.folder_path = tk.StringVar()
        self.ext_vars = {} # Guarda as extensões individuais
        self.category_vars = {} # Guarda os checkboxes "Pais"
        self._build_ui()

    def toggle_category(self, category, state):
        """Marca ou desmarca todos os itens de uma categoria específica."""
        for ext in EXTENSIONS_DB[category]:
            self.ext_vars[ext].set(state)

    def _build_ui(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Seleção de Pasta
        ttk.Label(main_frame, text="1. Pasta das ROMs", font=('Arial', 10, 'bold')).pack(anchor="w")
        frame_dir = ttk.Frame(main_frame)
        frame_dir.pack(fill=tk.X, pady=(0, 15))
        ttk.Entry(frame_dir, textvariable=self.folder_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(frame_dir, text="Procurar", command=self.browse_folder).pack(side=tk.LEFT)

        # 2. Extensões com Checkbox Pai
        ttk.Label(main_frame, text="2. Filtros de Console (Clique no título para marcar/desmarcar a coluna)", font=('Arial', 10, 'bold')).pack(anchor="w")
        ext_frame = ttk.LabelFrame(main_frame, text=" Extensões ", padding=10)
        ext_frame.pack(fill=tk.X, pady=(0, 15))

        for i, (cat, exts) in enumerate(EXTENSIONS_DB.items()):
            col = ttk.Frame(ext_frame)
            col.grid(row=0, column=i, sticky="nw", padx=15)
            
            # Checkbox Pai (Título da Coluna)
            cat_var = tk.BooleanVar(value=True)
            self.category_vars[cat] = cat_var
            # O comando lambda garante que a função saiba qual categoria e qual estado aplicar
            cb_parent = ttk.Checkbutton(col, text=cat.upper(), variable=cat_var, 
                                        command=lambda c=cat, v=cat_var: self.toggle_category(c, v.get()))
            cb_parent.pack(anchor="w", pady=(0, 5))
            
            # Linha separadora visual simples
            ttk.Separator(col, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)

            # Checkboxes Filhos
            for ext in exts:
                var = tk.BooleanVar(value=True)
                self.ext_vars[ext] = var
                ttk.Checkbutton(col, text=ext, variable=var).pack(anchor="w", padx=10)

        # 3. Ações
        btn_scan = ttk.Button(main_frame, text="INICIAR VARREDURA", command=self.scan_roms)
        btn_scan.pack(pady=10)

        # 4. Tabela de Resultados
        self.tree = ttk.Treeview(main_frame, columns=("Nome", "Caminho"), show='headings', selectmode="extended")
        self.tree.heading("Nome", text="Nome do Arquivo")
        self.tree.heading("Caminho", text="Caminho Completo")
        self.tree.column("Nome", width=300)
        self.tree.column("Caminho", width=550)
        self.tree.pack(fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # 5. Botão Deletar
        self.delete_btn = tk.Button(main_frame, text="DELETAR SELECIONADOS (AZUL)", 
                                   command=self.delete_selected, bg="#d32f2f", fg="white", 
                                   font=('Arial', 10, 'bold'), pady=10)
        self.delete_btn.pack(fill=tk.X, pady=10)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path: self.folder_path.set(path)

    def scan_roms(self):
        folder = self.folder_path.get()
        if not folder: 
            messagebox.showwarning("Aviso", "Selecione uma pasta primeiro.")
            return
        
        # Pega apenas as extensões cujos checkboxes estão marcados
        selected_exts = [ext for ext, var in self.ext_vars.items() if var.get()]
        if not selected_exts:
            messagebox.showwarning("Aviso", "Selecione ao menos uma extensão.")
            return

        self.tree.delete(*self.tree.get_children())
        hashes = defaultdict(list)

        for root_dir, _, files in os.walk(folder):
            for file in files:
                if any(file.lower().endswith(ext) for ext in selected_exts):
                    path = os.path.join(root_dir, file)
                    h = calculate_hash(path)
                    if h: hashes[h].append(path)

        count = 0
        for h, paths in hashes.items():
            if len(paths) > 1:
                for p in paths:
                    self.tree.insert("", tk.END, values=(os.path.basename(p), p))
                    count += 1

        if count == 0:
            messagebox.showinfo("Busca Concluída", "Nenhuma duplicata encontrada com as extensões selecionadas.")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione (deixe azul) os arquivos que deseja deletar.")
            return

        if messagebox.askyesno("Confirmar", f"Deletar {len(selected)} arquivos permanentemente?"):
            for item in selected:
                path = self.tree.item(item)['values'][1]
                try:
                    os.remove(path)
                    self.tree.delete(item)
                except Exception as e:
                    print(f"Erro ao deletar {path}: {e}")
            messagebox.showinfo("Sucesso", "Arquivos removidos.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RomCleanerApp(root)
    root.mainloop()
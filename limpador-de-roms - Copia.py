import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def calculate_hash(path, block_size=65536):
    """Gera um hash SHA-256 para identificar o conteúdo do arquivo."""
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
        self.root.title("Limpador de ROMs Duplicadas")
        self.root.geometry("700x500")
        
        self.folder_path = tk.StringVar()
        self.selected_exts = []
        self.duplicates = {}

        # --- Interface ---
        # Seleção de Pasta
        tk.Label(root, text="1. Selecione a pasta das ROMs:", font=('Arial', 10, 'bold')).pack(pady=5)
        frame_dir = tk.Frame(root)
        frame_dir.pack()
        tk.Entry(frame_dir, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_dir, text="Procurar", command=self.browse_folder).pack(side=tk.LEFT)

        # Seleção de Extensões
        tk.Label(root, text="2. Extensões (separe por vírgula):", font=('Arial', 10, 'bold')).pack(pady=5)
        self.ext_entry = tk.Entry(root, width=30)
        self.ext_entry.insert(0, ".sfc, .md, .gbc, .gba, .nes")
        self.ext_entry.pack()

        # Botão de Varredura
        self.scan_btn = tk.Button(root, text="Iniciar Varredura", command=self.scan_roms, bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
        self.scan_btn.pack(pady=15)

        # Lista de Resultados
        tk.Label(root, text="Arquivos Duplicados Encontrados:", font=('Arial', 9)).pack()
        self.tree = ttk.Treeview(root, columns=("Caminho"), show='headings')
        self.tree.heading("Caminho", text="Caminho do Arquivo")
        self.tree.column("Caminho", width=600)
        self.tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Botão Deletar
        tk.Button(root, text="Deletar Selecionados", command=self.delete_selected, bg="#f44336", fg="white").pack(pady=10)

    def browse_folder(self):
        directory = filedialog.askdirectory()
        if directory:
            self.folder_path.set(directory)

    def scan_roms(self):
        folder = self.folder_path.get()
        exts = [e.strip().lower() for e in self.ext_entry.get().split(",")]
        
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("Erro", "Selecione uma pasta válida.")
            return

        self.tree.delete(*self.tree.get_children())
        hashes = {}
        self.duplicates = {}

        for root_dir, _, files in os.walk(folder):
            for file in files:
                if any(file.lower().endswith(ext) for ext in exts):
                    full_path = os.path.join(root_dir, file)
                    file_hash = calculate_hash(full_path)
                    
                    if file_hash:
                        if file_hash in hashes:
                            if file_hash not in self.duplicates:
                                # Adiciona o original e a duplicata na visualização
                                self.duplicates[file_hash] = [hashes[file_hash]]
                            self.duplicates[file_hash].append(full_path)
                        else:
                            hashes[file_hash] = full_path

        # Preencher a lista na interface
        for h, paths in self.duplicates.items():
            for p in paths:
                self.tree.insert("", tk.END, values=(p,), tags=(h,))
        
        if not self.duplicates:
            messagebox.showinfo("Busca Concluída", "Nenhuma duplicata encontrada!")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione ao menos um arquivo na lista.")
            return

        if messagebox.askyesno("Confirmar", f"Deseja deletar {len(selected_items)} arquivos?"):
            for item in selected_items:
                file_path = self.tree.item(item)['values'][0]
                try:
                    os.remove(file_path)
                    self.tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível deletar {file_path}: {e}")
            messagebox.showinfo("Sucesso", "Arquivos deletados com sucesso.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RomCleanerApp(root)
    root.mainloop()
import os
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading


class Compactador:
    def __init__(self, root):
        self.root = root
        self.root.title("Compactador de Arquivos")
        self.root.geometry("600x540")
        self.root.resizable(True, True)
        self.root.configure(bg="#1e1e2e")

        self._build_ui()

    def _build_ui(self):
        bg = "#1e1e2e"
        fg = "#cdd6f4"
        accent = "#89b4fa"
        btn_bg = "#313244"

        tk.Label(self.root, text="Compactador por Arquivo", font=("Segoe UI", 16, "bold"),
                 bg=bg, fg=accent).pack(pady=(20, 4))

        tk.Label(self.root, text="Cria um .zip individual para cada arquivo na pasta selecionada",
                 font=("Segoe UI", 9), bg=bg, fg="#a6adc8").pack()

        # Pasta
        frame_pasta = tk.Frame(self.root, bg=bg)
        frame_pasta.pack(pady=16, padx=30, fill="x")

        tk.Label(frame_pasta, text="Pasta:", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w")

        frame_entry = tk.Frame(frame_pasta, bg=bg)
        frame_entry.pack(fill="x", pady=4)

        self.pasta_var = tk.StringVar()
        entry = tk.Entry(frame_entry, textvariable=self.pasta_var, font=("Segoe UI", 10),
                         bg="#313244", fg=fg, insertbackground=fg, relief="flat",
                         bd=6)
        entry.pack(side="left", fill="x", expand=True)

        tk.Button(frame_entry, text="Procurar", font=("Segoe UI", 9),
                  bg=accent, fg="#1e1e2e", activebackground="#74c7ec",
                  relief="flat", padx=10, command=self._selecionar_pasta).pack(side="left", padx=(6, 0))

        # Opções
        frame_opts = tk.Frame(self.root, bg=bg)
        frame_opts.pack(padx=30, fill="x")

        self.incluir_subpastas = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_opts, text="Incluir subpastas (recursivo)",
                       variable=self.incluir_subpastas,
                       bg=bg, fg=fg, selectcolor=btn_bg,
                       activebackground=bg, activeforeground=fg,
                       font=("Segoe UI", 9)).pack(anchor="w")

        self.apagar_original = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_opts, text="Apagar arquivo original após compactar",
                       variable=self.apagar_original,
                       bg=bg, fg="#f38ba8", selectcolor=btn_bg,
                       activebackground=bg, activeforeground="#f38ba8",
                       font=("Segoe UI", 9)).pack(anchor="w")

        # Progresso
        frame_prog = tk.Frame(self.root, bg=bg)
        frame_prog.pack(padx=30, pady=16, fill="x")

        self.label_status = tk.Label(frame_prog, text="Aguardando...", font=("Segoe UI", 9),
                                     bg=bg, fg="#a6adc8", anchor="w")
        self.label_status.pack(fill="x")

        self.progress = ttk.Progressbar(frame_prog, mode="determinate", length=540)
        self.progress.pack(fill="x", pady=6)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#313244", background=accent, thickness=18)

        self.label_contagem = tk.Label(frame_prog, text="", font=("Segoe UI", 9),
                                       bg=bg, fg=fg)
        self.label_contagem.pack()

        # Botão — antes do log para garantir visibilidade
        self.btn_iniciar = tk.Button(self.root, text="COMPACTAR TUDO",
                                     font=("Segoe UI", 12, "bold"),
                                     bg=accent, fg="#1e1e2e",
                                     activebackground="#74c7ec",
                                     relief="flat", padx=30, pady=12,
                                     command=self._iniciar)
        self.btn_iniciar.pack(pady=12)

        # Log
        self.log = tk.Text(self.root, height=5, font=("Consolas", 8),
                           bg="#181825", fg="#a6e3a1", relief="flat",
                           state="disabled", bd=0)
        self.log.pack(padx=30, pady=(0, 10), fill="x")

    def _selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos")
        if pasta:
            self.pasta_var.set(pasta)

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _iniciar(self):
        pasta = self.pasta_var.get().strip()
        if not pasta or not os.path.isdir(pasta):
            messagebox.showerror("Erro", "Selecione uma pasta válida.")
            return

        self.btn_iniciar.configure(state="disabled")
        threading.Thread(target=self._compactar, args=(pasta,), daemon=True).start()

    def _compactar(self, pasta):
        pasta_path = Path(pasta)

        if self.incluir_subpastas.get():
            arquivos = [f for f in pasta_path.rglob("*")
                        if f.is_file() and f.suffix.lower() != ".zip"]
        else:
            arquivos = [f for f in pasta_path.iterdir()
                        if f.is_file() and f.suffix.lower() != ".zip"]

        total = len(arquivos)
        if total == 0:
            self.root.after(0, lambda: messagebox.showinfo("Info", "Nenhum arquivo encontrado na pasta."))
            self.root.after(0, lambda: self.btn_iniciar.configure(state="normal"))
            return

        self.root.after(0, lambda: self.progress.configure(maximum=total, value=0))
        self.root.after(0, lambda: self._log(f"Iniciando: {total} arquivo(s) encontrado(s)\n"))

        erros = 0
        for i, arquivo in enumerate(arquivos, 1):
            zip_path = arquivo.with_suffix(".zip")

            self.root.after(0, lambda f=arquivo.name: self.label_status.configure(
                text=f"Compactando: {f}"))
            self.root.after(0, lambda c=i, t=total: self.label_contagem.configure(
                text=f"{c} / {t}"))

            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED,
                                     compresslevel=6) as zf:
                    zf.write(arquivo, arquivo.name)

                if self.apagar_original.get():
                    arquivo.unlink()
                    self.root.after(0, lambda f=arquivo.name: self._log(f"[OK] {f} → zip (original apagado)"))
                else:
                    self.root.after(0, lambda f=arquivo.name: self._log(f"[OK] {f} → zip"))

            except Exception as e:
                erros += 1
                self.root.after(0, lambda f=arquivo.name, err=str(e): self._log(f"[ERRO] {f}: {err}"))

            self.root.after(0, lambda v=i: self.progress.configure(value=v))

        msg_final = f"Concluído! {total - erros}/{total} arquivos compactados."
        if erros:
            msg_final += f" ({erros} erro(s))"

        self.root.after(0, lambda: self.label_status.configure(text=msg_final))
        self.root.after(0, lambda: self._log(f"\n{msg_final}"))
        self.root.after(0, lambda: self.btn_iniciar.configure(state="normal"))
        self.root.after(0, lambda: messagebox.showinfo("Pronto", msg_final))


if __name__ == "__main__":
    root = tk.Tk()
    app = Compactador(root)
    root.mainloop()

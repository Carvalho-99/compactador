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
        self.root.geometry("600x560")
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
        frame_pasta.pack(pady=14, padx=30, fill="x")

        tk.Label(frame_pasta, text="Pasta:", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w")

        frame_entry = tk.Frame(frame_pasta, bg=bg)
        frame_entry.pack(fill="x", pady=4)

        self.pasta_var = tk.StringVar()
        entry = tk.Entry(frame_entry, textvariable=self.pasta_var, font=("Segoe UI", 10),
                         bg="#313244", fg=fg, insertbackground=fg, relief="flat", bd=6)
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

        # Separador visual
        tk.Frame(self.root, bg="#313244", height=1).pack(fill="x", padx=30, pady=8)

        # Modo de compactação
        frame_modo = tk.Frame(self.root, bg=bg)
        frame_modo.pack(padx=30, fill="x")

        tk.Label(frame_modo, text="Modo de compactação:", font=("Segoe UI", 9, "bold"),
                 bg=bg, fg=fg).pack(anchor="w", pady=(0, 4))

        self.modo_unico = tk.BooleanVar(value=False)

        frame_check_modo = tk.Frame(frame_modo, bg="#313244", padx=10, pady=6)
        frame_check_modo.pack(fill="x")

        tk.Checkbutton(frame_check_modo,
                       text="Compactar a pasta inteira em um único ZIP",
                       variable=self.modo_unico,
                       command=self._atualizar_descricao_modo,
                       bg="#313244", fg="#a6e3a1", selectcolor="#45475a",
                       activebackground="#313244", activeforeground="#a6e3a1",
                       font=("Segoe UI", 9, "bold")).pack(anchor="w")

        self.label_modo = tk.Label(frame_check_modo,
                                   text="Padrão: um .zip por arquivo  (ex: video01.mp4 → video01.zip)",
                                   font=("Segoe UI", 8), bg="#313244", fg="#6c7086")
        self.label_modo.pack(anchor="w", padx=20)

        # Progresso
        frame_prog = tk.Frame(self.root, bg=bg)
        frame_prog.pack(padx=30, pady=12, fill="x")

        self.label_status = tk.Label(frame_prog, text="Aguardando...", font=("Segoe UI", 9),
                                     bg=bg, fg="#a6adc8", anchor="w")
        self.label_status.pack(fill="x")

        self.progress = ttk.Progressbar(frame_prog, mode="determinate", length=540)
        self.progress.pack(fill="x", pady=6)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#313244", background="#89b4fa", thickness=18)

        self.label_contagem = tk.Label(frame_prog, text="", font=("Segoe UI", 9),
                                       bg=bg, fg=fg)
        self.label_contagem.pack()

        # Botão
        self.btn_iniciar = tk.Button(self.root, text="COMPACTAR TUDO",
                                     font=("Segoe UI", 12, "bold"),
                                     bg=accent, fg="#1e1e2e",
                                     activebackground="#74c7ec",
                                     relief="flat", padx=30, pady=12,
                                     command=self._iniciar)
        self.btn_iniciar.pack(pady=10)

        # Log
        self.log = tk.Text(self.root, height=5, font=("Consolas", 8),
                           bg="#181825", fg="#a6e3a1", relief="flat",
                           state="disabled", bd=0)
        self.log.pack(padx=30, pady=(0, 10), fill="x")

    def _atualizar_descricao_modo(self):
        if self.modo_unico.get():
            self.label_modo.configure(
                text="Todos os arquivos → um único arquivo pasta.zip")
        else:
            self.label_modo.configure(
                text="Padrão: um .zip por arquivo  (ex: video01.mp4 → video01.zip)")

    def _selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos")
        if pasta:
            self.pasta_var.set(pasta)

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _resetar(self):
        self.progress.configure(value=0)
        self.label_status.configure(text="Aguardando...")
        self.label_contagem.configure(text="")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.btn_iniciar.configure(state="normal")

    def _iniciar(self):
        pasta = self.pasta_var.get().strip()
        if not pasta or not os.path.isdir(pasta):
            messagebox.showerror("Erro", "Selecione uma pasta válida.")
            return

        self.btn_iniciar.configure(state="disabled")

        if self.modo_unico.get():
            threading.Thread(target=self._compactar_unico, args=(pasta,), daemon=True).start()
        else:
            threading.Thread(target=self._compactar_individual, args=(pasta,), daemon=True).start()

    def _compactar_individual(self, pasta):
        pasta_path = Path(pasta)

        if self.incluir_subpastas.get():
            arquivos = [f for f in pasta_path.rglob("*")
                        if f.is_file() and f.suffix.lower() != ".zip"]
        else:
            arquivos = [f for f in pasta_path.iterdir()
                        if f.is_file() and f.suffix.lower() != ".zip"]

        total = len(arquivos)
        if total == 0:
            self.root.after(0, lambda: messagebox.showinfo("Info", "Nenhum arquivo encontrado."))
            self.root.after(0, self._resetar)
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
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
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

        msg = f"Concluído! {total - erros}/{total} arquivos compactados."
        if erros:
            msg += f" ({erros} erro(s))"

        self.root.after(0, lambda: self.label_status.configure(text=msg))
        self.root.after(0, lambda: self._log(f"\n{msg}"))
        self.root.after(0, lambda: messagebox.showinfo("Pronto", msg))
        self.root.after(0, self._resetar)

    def _compactar_unico(self, pasta):
        pasta_path = Path(pasta)

        if self.incluir_subpastas.get():
            arquivos = [f for f in pasta_path.rglob("*")
                        if f.is_file() and f.suffix.lower() != ".zip"]
        else:
            arquivos = [f for f in pasta_path.iterdir()
                        if f.is_file() and f.suffix.lower() != ".zip"]

        total = len(arquivos)
        if total == 0:
            self.root.after(0, lambda: messagebox.showinfo("Info", "Nenhum arquivo encontrado."))
            self.root.after(0, self._resetar)
            return

        zip_path = pasta_path / f"{pasta_path.name}.zip"
        self.root.after(0, lambda: self.progress.configure(maximum=total, value=0))
        self.root.after(0, lambda: self._log(f"Criando {zip_path.name} com {total} arquivo(s)\n"))

        erros = 0
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                for i, arquivo in enumerate(arquivos, 1):
                    self.root.after(0, lambda f=arquivo.name: self.label_status.configure(
                        text=f"Adicionando: {f}"))
                    self.root.after(0, lambda c=i, t=total: self.label_contagem.configure(
                        text=f"{c} / {t}"))
                    try:
                        arcname = arquivo.relative_to(pasta_path)
                        zf.write(arquivo, arcname)
                        self.root.after(0, lambda f=arquivo.name: self._log(f"[OK] {f}"))
                    except Exception as e:
                        erros += 1
                        self.root.after(0, lambda f=arquivo.name, err=str(e): self._log(f"[ERRO] {f}: {err}"))
                    self.root.after(0, lambda v=i: self.progress.configure(value=v))

            if self.apagar_original.get():
                for arquivo in arquivos:
                    try:
                        arquivo.unlink()
                    except Exception:
                        pass

        except Exception as e:
            self.root.after(0, lambda err=str(e): self._log(f"\n[ERRO FATAL] {err}"))
            self.root.after(0, self._resetar)
            return

        msg = f"Concluído! {zip_path.name} criado com {total - erros} arquivo(s)."
        if erros:
            msg += f" ({erros} erro(s))"

        self.root.after(0, lambda: self.label_status.configure(text=msg))
        self.root.after(0, lambda: self._log(f"\n{msg}"))
        self.root.after(0, lambda: messagebox.showinfo("Pronto", msg))
        self.root.after(0, self._resetar)


if __name__ == "__main__":
    root = tk.Tk()
    app = Compactador(root)
    root.mainloop()

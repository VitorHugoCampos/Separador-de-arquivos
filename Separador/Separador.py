import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import math
import threading

BG      = "#0f0f13"
SURFACE = "#1a1a24"
CARD    = "#22222f"
ACCENT  = "#7c6af7"
ACCENT2 = "#a78bfa"
TEXT    = "#e8e6f0"
MUTED   = "#6b6880"
SUCCESS = "#4ade80"
ERROR   = "#f87171"

def formatar_tamanho(n_bytes):
    for unidade in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unidade}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"

def separar_arquivo(caminho, pasta_destino, n_partes, callback_progresso, callback_fim):
    try:
        tamanho_total = os.path.getsize(caminho)
        tamanho_parte = math.ceil(tamanho_total / n_partes)
        nome_base, ext = os.path.splitext(os.path.basename(caminho))

        with open(caminho, "rb") as f:
            for i in range(n_partes):
                dados = f.read(tamanho_parte)
                if not dados:
                    break
                sufixo = str(i + 1).zfill(len(str(n_partes)))
                nome_saida = os.path.join(pasta_destino, f"{nome_base}_parte{sufixo}{ext}")
                with open(nome_saida, "wb") as out:
                    out.write(dados)
                progresso = int((i + 1) / n_partes * 100)
                callback_progresso(progresso, i + 1, n_partes, len(dados))

        callback_fim(True, None)
    except Exception as e:
        callback_fim(False, str(e))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Separador de Arquivos")
        self.geometry("580x680")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._caminho    = tk.StringVar()
        self._pasta_dest = tk.StringVar()
        self._n_partes   = tk.IntVar(value=2)
        self._construir_ui()

    def _construir_ui(self):
        # Cabeçalho
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=32, pady=(20, 0))
        tk.Label(header, text="✦", font=("Georgia", 22), bg=BG, fg=ACCENT).pack(side="left")
        tf = tk.Frame(header, bg=BG)
        tf.pack(side="left", padx=10)
        tk.Label(tf, text="Separador de Arquivos", font=("Georgia", 18, "bold"), bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(tf, text="Divida qualquer arquivo em partes iguais", font=("Courier", 9), bg=BG, fg=MUTED).pack(anchor="w")
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x", padx=32, pady=(12, 0))

        # Card com scroll via canvas
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=32, pady=12)

        card = tk.Frame(canvas, bg=CARD)
        canvas.create_window((0, 0), window=card, anchor="nw")

        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # ── 01: Arquivo ──────────────────────────────────────────
        self._label_section(inner, "01", "Arquivo de origem")
        drop = tk.Frame(inner, bg=SURFACE, cursor="hand2")
        drop.pack(fill="x", pady=(6, 0))
        drop.bind("<Button-1>", lambda e: self._escolher_arquivo())

        self._ico = tk.Label(drop, text="📂", font=("Arial", 26), bg=SURFACE, fg=ACCENT, cursor="hand2")
        self._ico.pack(pady=(14, 4))
        self._ico.bind("<Button-1>", lambda e: self._escolher_arquivo())

        self._lbl_arquivo = tk.Label(drop, text="Clique para selecionar o arquivo",
                                     font=("Courier", 9), bg=SURFACE, fg=MUTED, cursor="hand2", wraplength=400)
        self._lbl_arquivo.pack()
        self._lbl_arquivo.bind("<Button-1>", lambda e: self._escolher_arquivo())

        self._lbl_info = tk.Label(drop, text="", font=("Courier", 8), bg=SURFACE, fg=ACCENT2)
        self._lbl_info.pack(pady=(2, 0))

        tk.Button(drop, text="Procurar...", font=("Courier", 9), bg=ACCENT, fg="white",
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  activebackground=ACCENT2, activeforeground="white",
                  command=self._escolher_arquivo).pack(pady=(10, 14))

        # ── 02: Pasta destino ─────────────────────────────────────
        self._label_section(inner, "02", "Pasta de destino")
        dest_frame = tk.Frame(inner, bg=SURFACE)
        dest_frame.pack(fill="x", pady=(6, 0))

        self._lbl_dest = tk.Label(dest_frame, text="Mesma pasta do arquivo original",
                                  font=("Courier", 9), bg=SURFACE, fg=MUTED, wraplength=380, justify="left")
        self._lbl_dest.pack(side="left", padx=12, pady=12, fill="x", expand=True)

        tk.Button(dest_frame, text="Escolher", font=("Courier", 9), bg=SURFACE, fg=ACCENT2,
                  relief="flat", padx=10, pady=6, cursor="hand2",
                  activebackground=CARD, activeforeground=ACCENT,
                  command=self._escolher_pasta).pack(side="right", padx=8, pady=8)

        # ── 03: Número de partes ──────────────────────────────────
        self._label_section(inner, "03", "Número de partes")
        ctrl = tk.Frame(inner, bg=CARD)
        ctrl.pack(fill="x", pady=(6, 0))

        tk.Button(ctrl, text="-", font=("Arial", 16, "bold"), bg=SURFACE, fg=ACCENT2,
                  relief="flat", width=3, cursor="hand2", activebackground=CARD,
                  command=lambda: self._ajustar(-1)).pack(side="left")

        self._entry = tk.Entry(ctrl, textvariable=self._n_partes, font=("Georgia", 22, "bold"),
                               width=4, bg=SURFACE, fg=TEXT, relief="flat",
                               justify="center", insertbackground=ACCENT)
        self._entry.pack(side="left", padx=6)

        tk.Button(ctrl, text="+", font=("Arial", 16, "bold"), bg=SURFACE, fg=ACCENT2,
                  relief="flat", width=3, cursor="hand2", activebackground=CARD,
                  command=lambda: self._ajustar(1)).pack(side="left")

        self._lbl_preview = tk.Label(ctrl, text="", font=("Courier", 8), bg=CARD, fg=MUTED)
        self._lbl_preview.pack(side="left", padx=14)
        self._n_partes.trace_add("write", self._atualizar_preview)

        # ── 04: Progresso ─────────────────────────────────────────
        self._label_section(inner, "04", "Progresso")
        prog_bg = tk.Frame(inner, bg=SURFACE, height=8)
        prog_bg.pack(fill="x", pady=(6, 0))
        prog_bg.pack_propagate(False)
        self._barra = tk.Frame(prog_bg, bg=ACCENT, height=8)
        self._barra.place(x=0, y=0, relheight=1, relwidth=0)

        self._lbl_prog = tk.Label(inner, text="Aguardando...", font=("Courier", 8), bg=CARD, fg=MUTED)
        self._lbl_prog.pack(anchor="w", pady=(4, 0))

        # ── Botão principal ───────────────────────────────────────
        self._btn = tk.Button(inner, text="✦  Separar Arquivo",
                              font=("Georgia", 13, "bold"),
                              bg=ACCENT, fg="white", relief="flat",
                              padx=20, pady=14, cursor="hand2",
                              activebackground=ACCENT2, activeforeground="white",
                              command=self._iniciar)
        self._btn.pack(fill="x", pady=(18, 4))

        # Atualiza tamanho do canvas
        card.update_idletasks()
        canvas.config(width=card.winfo_reqwidth(), height=card.winfo_reqheight())

        # Rodapé
        tk.Label(self, text="Os arquivos são salvos na pasta de destino escolhida",
                 font=("Courier", 8), bg=BG, fg=MUTED).pack(pady=(0, 10))

    def _label_section(self, parent, num, texto):
        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(fill="x", pady=(14, 0))
        tk.Label(row, text=num, font=("Courier", 8, "bold"), bg=ACCENT, fg="white", padx=5, pady=2).pack(side="left")
        tk.Label(row, text=f"  {texto}", font=("Courier", 10, "bold"), bg=parent["bg"], fg=ACCENT2).pack(side="left")

    def _escolher_arquivo(self):
        path = filedialog.askopenfilename(title="Selecionar arquivo")
        if path:
            self._caminho.set(path)
            self._lbl_arquivo.config(text=os.path.basename(path), fg=TEXT)
            self._lbl_info.config(text=f"Tamanho: {formatar_tamanho(os.path.getsize(path))}")
            self._ico.config(text="📄")
            # Se ainda não escolheu pasta, sugere a pasta do arquivo
            if not self._pasta_dest.get():
                pasta = os.path.dirname(path)
                self._pasta_dest.set(pasta)
                self._lbl_dest.config(text=pasta, fg=TEXT)
            self._atualizar_preview()

    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Escolher pasta de destino")
        if pasta:
            self._pasta_dest.set(pasta)
            self._lbl_dest.config(text=pasta, fg=TEXT)

    def _ajustar(self, delta):
        val = max(2, min(999, self._n_partes.get() + delta))
        self._n_partes.set(val)

    def _atualizar_preview(self, *_):
        path = self._caminho.get()
        if not path or not os.path.isfile(path):
            self._lbl_preview.config(text="")
            return
        try:
            n = int(self._n_partes.get())
            tam = os.path.getsize(path)
            self._lbl_preview.config(text=f"≈ {formatar_tamanho(math.ceil(tam / n))} por parte")
        except Exception:
            self._lbl_preview.config(text="")

    def _iniciar(self):
        path = self._caminho.get()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Erro", "Selecione um arquivo válido.")
            return
        pasta = self._pasta_dest.get() or os.path.dirname(path)
        if not os.path.isdir(pasta):
            messagebox.showerror("Erro", "Pasta de destino inválida.")
            return
        try:
            n = int(self._n_partes.get())
            if n < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Informe um número de partes >= 2.")
            return

        self._btn.config(state="disabled", text="Separando...")
        self._lbl_prog.config(text="Iniciando...", fg=MUTED)
        self._barra.place(relwidth=0)

        threading.Thread(
            target=separar_arquivo,
            args=(path, pasta, n, self._cb_prog, self._cb_fim),
            daemon=True
        ).start()

    def _cb_prog(self, pct, parte_atual, total, tam_parte):
        self.after(0, lambda: (
            self._barra.place(relwidth=pct / 100),
            self._lbl_prog.config(
                text=f"Parte {parte_atual}/{total} gravada  ({formatar_tamanho(tam_parte)})  — {pct}%",
                fg=ACCENT2)
        ))

    def _cb_fim(self, sucesso, erro):
        self.after(0, self._finalizar, sucesso, erro)

    def _finalizar(self, sucesso, erro):
        self._btn.config(state="normal", text="✦  Separar Arquivo")
        if sucesso:
            self._barra.place(relwidth=1)
            self._barra.config(bg=SUCCESS)
            self._lbl_prog.config(text="✔ Concluído com sucesso!", fg=SUCCESS)
            messagebox.showinfo("Pronto!", f"Arquivo separado com sucesso!\nSalvo em:\n{self._pasta_dest.get()}")
            self._barra.config(bg=ACCENT)
        else:
            self._barra.config(bg=ERROR)
            self._lbl_prog.config(text=f"✖ Erro: {erro}", fg=ERROR)
            messagebox.showerror("Erro", f"Falha ao separar:\n{erro}")
            self._barra.config(bg=ACCENT)


if __name__ == "__main__":
    App().mainloop()
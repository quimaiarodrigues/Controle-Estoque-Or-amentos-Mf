from tkinter import ttk
import os
import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys

# Função para conectar ao banco de dados
def conectar_banco():
    try:
        conn = sqlite3.connect(caminho_banco)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror(
            "Erro", f"Erro ao conectar ao banco de dados App: {e}")
        return None

# Detecta se está rodando como executável ou script Python
if getattr(sys, 'frozen', False):
    os.environ["ENVIRONMENT"] = "production"
else:
    os.environ["ENVIRONMENT"] = "development"

# Obtenha o caminho absoluto do diretório atual
basedir = os.path.dirname(os.path.abspath(__file__))

# Definir o caminho do banco de dados com base no ambiente
if os.environ.get("ENVIRONMENT") == "production":
    caminho_banco = "T:/SETOR PROJETOS/Inmes - Depto. Projetos/db/estoque.db"
else:
    caminho_banco = os.path.join(basedir, 'estoque.db')

# Ajuste da janela do app em relação à tela
def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y-30}")

def criar_tabela_pecas():
    conn = conectar_banco()
    if conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Pecas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    codigo TEXT NOT NULL UNIQUE,
                    descricao TEXT,
                    quantidade INTEGER,
                    preco REAL,
                    fornecedor_id INTEGER,
                    FOREIGN KEY (fornecedor_id) REFERENCES Fornecedores(id)
                )
            ''')

def abrir_janela_cadastro_pecas(root):
    def salvar_peca():
        nome = nome_entry.get().strip()
        codigo = codigo_entry.get().strip()
        descricao = descricao_entry.get().strip()
        quantidade = quantidade_entry.get().strip()
        preco = preco_entry.get().strip()
        fornecedor_nome = fornecedor_combobox.get()

        if nome and codigo and quantidade.isdigit() and preco.replace('.', '', 1).isdigit() and fornecedor_nome:
            try:
                conn = conectar_banco()
                if conn:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT id FROM Fornecedores WHERE nome = ?", (fornecedor_nome,))
                        fornecedor_id = cursor.fetchone()
                        if fornecedor_id:
                            fornecedor_id = fornecedor_id[0]
                            cursor.execute("INSERT INTO Pecas (nome, codigo, descricao, quantidade, preco, fornecedor_id) VALUES (?, ?, ?, ?, ?, ?)",
                                           (nome, codigo, descricao, int(quantidade), float(preco), fornecedor_id))
                            conn.commit()
                            atualizar_lista_pecas(fornecedor_nome)
                            nome_entry.delete(0, tk.END)
                            codigo_entry.delete(0, tk.END)
                            descricao_entry.delete(0, tk.END)
                            quantidade_entry.delete(0, tk.END)
                            preco_entry.delete(0, tk.END)
                            salvar_edicao_btn.config(state=tk.DISABLED)
                            janela_pecas.lift()
                        else:
                            messagebox.showwarning(
                                "Aviso", "Fornecedor não encontrado.")
            except sqlite3.IntegrityError:
                messagebox.showwarning(
                    "Aviso", "O nome ou código da peça já existe.")
        else:
            messagebox.showwarning(
                "Aviso", "Preencha todos os campos corretamente.")

    def editar_peca():
        selected_item = tree.selection()
        if selected_item:
            peca = tree.item(selected_item)['values']
            nome, codigo, descricao, quantidade, preco, fornecedor = peca

            nome_entry.delete(0, tk.END)
            nome_entry.insert(0, nome)
            codigo_entry.delete(0, tk.END)
            codigo_entry.insert(0, codigo)
            descricao_entry.delete(0, tk.END)
            descricao_entry.insert(0, descricao)
            quantidade_entry.delete(0, tk.END)
            quantidade_entry.insert(0, quantidade)
            preco_entry.delete(0, tk.END)
            preco_entry.insert(0, preco.replace('R$ ', ''))
            fornecedor_combobox.set(fornecedor)

            salvar_edicao_btn.config(state=tk.NORMAL)

    def salvar_edicao():
        novo_nome = nome_entry.get().strip()
        novo_codigo = codigo_entry.get().strip()
        nova_descricao = descricao_entry.get().strip()
        nova_quantidade = quantidade_entry.get().strip()
        novo_preco = preco_entry.get().strip()
        novo_fornecedor_nome = fornecedor_combobox.get()

        selected_item = tree.selection()
        if selected_item:
            codigo_original = tree.item(selected_item)['values'][1]

        if novo_nome and novo_codigo and nova_quantidade.isdigit() and novo_preco.replace('.', '', 1).isdigit() and novo_fornecedor_nome:
            try:
                conn = conectar_banco()
                if conn:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT id FROM Fornecedores WHERE nome = ?", (novo_fornecedor_nome,))
                        fornecedor_id = cursor.fetchone()
                        if fornecedor_id:
                            fornecedor_id = fornecedor_id[0]
                            cursor.execute("UPDATE Pecas SET nome = ?, codigo = ?, descricao = ?, quantidade = ?, preco = ?, fornecedor_id = ? WHERE codigo = ?",
                                           (novo_nome, novo_codigo, nova_descricao, int(nova_quantidade), float(novo_preco), fornecedor_id, codigo_original))
                            conn.commit()
                            atualizar_lista_pecas(novo_fornecedor_nome)
                            salvar_edicao_btn.config(state=tk.DISABLED)
                            messagebox.showinfo(
                                "Sucesso", "Peça atualizada com sucesso.")
                            janela_pecas.lift()
                        else:
                            messagebox.showwarning(
                                "Aviso", "Fornecedor não encontrado.")
            except sqlite3.IntegrityError:
                messagebox.showwarning(
                    "Aviso", "O nome ou código da peça já existe.")
        else:
            messagebox.showwarning(
                "Aviso", "Preencha todos os campos corretamente.")

    def excluir_peca():
        selected_item = tree.selection()
        if selected_item:
            peca = tree.item(selected_item)['values']
            codigo = peca[1]

            confirm = messagebox.askyesno(
                "Confirmação", f"Deseja realmente excluir a peça de código {codigo}?")
            if confirm:
                try:
                    conn = conectar_banco()
                    if conn:
                        with conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "DELETE FROM Pecas WHERE codigo = ?", (codigo,))
                            conn.commit()
                            atualizar_lista_pecas(fornecedor_combobox.get())
                            messagebox.showinfo(
                                "Sucesso", "Peça excluída com sucesso.")
                            janela_pecas.lift()
                except sqlite3.Error as e:
                    messagebox.showerror("Erro", f"Erro ao excluir peça: {e}")
        else:
            messagebox.showwarning("Aviso", "Selecione uma peça para excluir.")

    def atualizar_lista_pecas(fornecedor_nome=None):
        for item in tree.get_children():
            tree.delete(item)
        if fornecedor_nome:
            conn = conectar_banco()
            if conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT Pecas.nome, Pecas.codigo, Pecas.descricao, Pecas.quantidade, Pecas.preco, Fornecedores.nome
                        FROM Pecas
                        LEFT JOIN Fornecedores ON Pecas.fornecedor_id = Fornecedores.id
                        WHERE Fornecedores.nome = ?
                        ORDER BY Pecas.nome
                    ''', (fornecedor_nome,))
                    pecas = cursor.fetchall()
                    for peca in pecas:
                        nome, codigo, descricao, quantidade, preco, fornecedor = peca
                        preco_formatado = f"R$ {preco:.2f}"
                        tree.insert('', tk.END, values=(
                            nome, codigo, descricao, quantidade, preco_formatado, fornecedor))

    def on_closing():
        if messagebox.askokcancel("Sair", "Deseja realmente fechar?"):
            janela_pecas.destroy()
            root.destroy()

    janela_pecas = tk.Toplevel(root)
    janela_pecas.title("Cadastro de Peças")
    janela_pecas.geometry("1250x600")
    centralizar_janela(janela_pecas, 1250, 600)
    janela_pecas.focus_force()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    frame_campos = tk.Frame(janela_pecas)
    frame_campos.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    tk.Label(frame_campos, text="Nome da Peça:").grid(
        row=0, column=0, padx=(0, 5), pady=2, sticky='e')
    nome_entry = tk.Entry(frame_campos, width=60)
    nome_entry.grid(row=0, column=1, padx=(0, 10), pady=2, sticky='w')

    tk.Label(frame_campos, text="Código:").grid(
        row=1, column=0, padx=(0, 5), pady=2, sticky='e')
    codigo_entry = tk.Entry(frame_campos, width=60)
    codigo_entry.grid(row=1, column=1, padx=(0, 10), pady=2, sticky='w')

    tk.Label(frame_campos, text="Descrição:").grid(
        row=2, column=0, padx=(0, 5), pady=2, sticky='e')
    descricao_entry = tk.Entry(frame_campos, width=60)
    descricao_entry.grid(row=2, column=1, padx=(0, 10), pady=2, sticky='w')

    tk.Label(frame_campos, text="Quantidade:").grid(
        row=3, column=0, padx=(0, 5), pady=2, sticky='e')
    quantidade_entry = tk.Entry(frame_campos, width=60)
    quantidade_entry.grid(row=3, column=1, padx=(0, 10), pady=2, sticky='w')

    tk.Label(frame_campos, text="Preço:").grid(
        row=4, column=0, padx=(0, 5), pady=2, sticky='e')
    preco_entry = tk.Entry(frame_campos, width=60)
    preco_entry.grid(row=4, column=1, padx=(0, 10), pady=2, sticky='w')

    tk.Label(frame_campos, text="Fornecedor:").grid(
        row=5, column=0, padx=(0, 5), pady=2, sticky='e')
    fornecedor_combobox = ttk.Combobox(frame_campos, width=57)
    fornecedor_combobox.grid(row=5, column=1, padx=(0, 10), pady=2, sticky='w')

    conn = conectar_banco()
    if conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM Fornecedores ORDER BY nome")
            fornecedores = cursor.fetchall()
            fornecedor_combobox['values'] = [fornecedor[0]
                                             for fornecedor in fornecedores]

    fornecedor_combobox.bind("<<ComboboxSelected>>", lambda e: atualizar_lista_pecas(fornecedor_combobox.get()))

    frame_botoes = tk.Frame(frame_campos)
    frame_botoes.grid(row=6, column=1, pady=10, sticky='w')

    tk.Button(frame_botoes, text="Salvar",
              command=salvar_peca).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Editar",
              command=editar_peca).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Excluir",
              command=excluir_peca).pack(side=tk.LEFT, padx=5)
    salvar_edicao_btn = tk.Button(
        frame_botoes, text="Salvar Edição", command=salvar_edicao, state=tk.DISABLED)
    salvar_edicao_btn.pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Voltar para Home",
              command=janela_pecas.destroy).pack(side="left", padx=10)

    tree = ttk.Treeview(janela_pecas, columns=(
        "nome", "codigo", "descricao", "quantidade", "preco", "fornecedor"), show='headings')
    tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    tree.heading("nome", text="Nome")
    tree.heading("codigo", text="Código")
    tree.heading("descricao", text="Descrição")
    tree.heading("quantidade", text="Quantidade")
    tree.heading("preco", text="Preço")
    tree.heading("fornecedor", text="Fornecedor")

    tree.column("codigo", anchor="center")
    tree.column("descricao", anchor="center")
    tree.column("quantidade", anchor="center")
    tree.column("preco", anchor="center")

    janela_pecas.grid_rowconfigure(1, weight=1)
    janela_pecas.grid_columnconfigure(0, weight=1)
    janela_pecas.grid_columnconfigure(1, weight=0)

    janela_pecas.mainloop()

def main():
    criar_tabela_pecas()
    root = tk.Tk()
    root.title("Home")
    centralizar_janela(root, 400, 300)
    tk.Button(root, text="Abrir Cadastro de Peças",
              command=lambda: abrir_janela_cadastro_pecas(root)).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()

import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import PhotoImage
import sqlite3
import sys

# Função para conectar ao banco de dados


def conectar_banco():
    try:
        conn = sqlite3.connect(caminho_banco)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror(
            "Erro", f"Erro ao conectar ao banco de dados: {e}")
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

# Função para criar a tabela de fornecedores


def criar_tabela_fornecedores():
    conn = conectar_banco()
    if conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Fornecedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    cnpj TEXT NOT NULL UNIQUE,
                    telefone TEXT,
                    email TEXT,
                    endereco TEXT
                )
            ''')

# Função para editar fornecedor


def editar_fornecedor(tree, atualizar_lista_fornecedores):
    fornecedor_selecionado = tree.selection()
    if fornecedor_selecionado:
        valores_fornecedor = tree.item(fornecedor_selecionado, 'values')
        nome_atual, cnpj_atual, telefone_atual, email_atual, endereco_atual = valores_fornecedor

        editar_janela = tk.Toplevel()
        editar_janela.title("Editar Fornecedor")
        centralizar_janela(editar_janela, 600, 200)

        tk.Label(editar_janela, text="Nome do Fornecedor:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w")
        nome_entry_editar = tk.Entry(editar_janela, width=40)
        nome_entry_editar.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        nome_entry_editar.insert(0, nome_atual)

        tk.Label(editar_janela, text="CNPJ:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w")
        cnpj_entry_editar = tk.Entry(editar_janela, width=20)
        cnpj_entry_editar.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        cnpj_entry_editar.insert(0, cnpj_atual)

        tk.Label(editar_janela, text="Telefone:").grid(
            row=3, column=0, padx=10, pady=5, sticky="w")
        telefone_entry_editar = tk.Entry(editar_janela, width=20)
        telefone_entry_editar.grid(
            row=3, column=1, padx=10, pady=5, sticky="w")
        telefone_entry_editar.insert(0, telefone_atual)

        tk.Label(editar_janela, text="Email:").grid(
            row=4, column=0, padx=10, pady=5, sticky="w")
        email_entry_editar = tk.Entry(editar_janela)
        email_entry_editar.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        email_entry_editar.insert(0, email_atual)

        tk.Label(editar_janela, text="Endereço:").grid(
            row=5, column=0, padx=10, pady=5, sticky="w")
        endereco_entry_editar = tk.Entry(editar_janela, width=50)
        endereco_entry_editar.grid(
            row=5, column=1, padx=10, pady=5, sticky="w")
        endereco_entry_editar.insert(0, endereco_atual)

        def salvar_edicao():
            novo_nome = nome_entry_editar.get().strip()
            novo_cnpj = cnpj_entry_editar.get().strip()
            novo_telefone = telefone_entry_editar.get().strip()
            novo_email = email_entry_editar.get().strip()
            novo_endereco = endereco_entry_editar.get().strip()

            if novo_nome and novo_cnpj:
                try:
                    conn = conectar_banco()
                    if conn:
                        with conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE Fornecedores SET nome = ?, cnpj = ?, telefone = ?, email = ?, endereco = ? WHERE cnpj = ?",
                                           (novo_nome, novo_cnpj, novo_telefone, novo_email, novo_endereco, cnpj_atual))
                            conn.commit()
                            atualizar_lista_fornecedores()
                            editar_janela.destroy()
                except sqlite3.IntegrityError:
                    messagebox.showwarning(
                        "Aviso", "Já existe um fornecedor com esse nome ou CNPJ.")
            else:
                messagebox.showwarning(
                    "Aviso", "Preencha os campos corretamente.")

        tk.Button(editar_janela, text="Salvar Alterações",
                  command=salvar_edicao).grid(row=6, column=1, pady=10)


# Função para excluir fornecedor
def excluir_fornecedor(tree, atualizar_lista_fornecedores, janela_fornecedor):
    fornecedor_selecionado = tree.selection()
    if fornecedor_selecionado:
        valores_fornecedor = tree.item(fornecedor_selecionado, 'values')
        cnpj = valores_fornecedor[1]  # Supondo que o CNPJ é a segunda coluna
        resposta = messagebox.askyesno(
            "Confirmar Exclusão", f"Deseja realmente excluir o fornecedor com CNPJ {cnpj}?")
        if resposta:
            try:
                conn = conectar_banco()
                if conn:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "DELETE FROM Fornecedores WHERE cnpj = ?", (cnpj,))
                        conn.commit()
                        atualizar_lista_fornecedores()
                        messagebox.showinfo(
                            "Sucesso", "Fornecedor excluído com sucesso.")
                        # Traz a janela de cadastro para frente após a exclusão
                        janela_fornecedor.lift()
            except sqlite3.Error as e:
                messagebox.showerror(
                    "Erro", f"Erro ao excluir fornecedor: {e}")
                janela_fornecedor.focus_force()

    else:
        messagebox.showwarning(
            "Aviso", "Por favor, selecione um fornecedor para excluir.")
        janela_fornecedor.focus_force()


# Função para abrir a janela de cadastro de fornecedores
def abrir_janela_cadastro_fornecedores():
    def salvar_fornecedor():
        nome_fornecedor = nome_entry.get().strip()
        cnpj = cnpj_entry.get().strip()
        telefone = telefone_entry.get().strip()
        email = email_entry.get().strip()
        endereco = endereco_entry.get().strip()

        if nome_fornecedor and cnpj:
            try:
                conn = conectar_banco()
                if conn:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Fornecedores (nome, cnpj, telefone, email, endereco) VALUES (?, ?, ?, ?, ?)",
                                       (nome_fornecedor, cnpj, telefone, email, endereco))
                        conn.commit()
                        atualizar_lista_fornecedores()
                        nome_entry.delete(0, tk.END)
                        cnpj_entry.delete(0, tk.END)
                        telefone_entry.delete(0, tk.END)
                        email_entry.delete(0, tk.END)
                        endereco_entry.delete(0, tk.END)
            except sqlite3.IntegrityError:
                messagebox.showwarning(
                    "Aviso", "O nome ou CNPJ do fornecedor já existe.")
                janela_fornecedor.focus_force()

        else:
            messagebox.showwarning(
                "Aviso", "Preencha os campos obrigatórios corretamente.")
            janela_fornecedor.focus_force()

    def atualizar_lista_fornecedores():
        for item in tree.get_children():
            tree.delete(item)
        conn = conectar_banco()
        if conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT nome, cnpj, telefone, email, endereco FROM Fornecedores ORDER BY nome")
                fornecedores = cursor.fetchall()
                for fornecedor in fornecedores:
                    tree.insert('', tk.END, values=(
                        fornecedor[0], fornecedor[1], fornecedor[2], fornecedor[3], fornecedor[4]))

    janela_fornecedor = tk.Toplevel()
    janela_fornecedor.title("Cadastrar Fornecedor")
    centralizar_janela(janela_fornecedor, 1100, 650)
    janela_fornecedor.focus_force()

    try:
        logo_path = os.path.join(basedir, "logo.png")
        logo = tk.PhotoImage(file=logo_path)
        logo = logo.subsample(3, 3)
        logo_label = tk.Label(janela_fornecedor, image=logo)
        logo_label.grid(row=0, column=0, columnspan=2, pady=5)
        janela_fornecedor.logo = logo
    except tk.TclError:
        print("Erro ao carregar a imagem do logotipo.")

    janela_fornecedor.grid_columnconfigure(0, weight=0)
    janela_fornecedor.grid_columnconfigure(1, weight=3)

    tk.Label(janela_fornecedor, text="CADASTRO DE FORNECEDORES", font=(
        "Arial", 18)).grid(row=1, column=0, columnspan=2, pady=20)

    tk.Label(janela_fornecedor, text="Nome do Fornecedor:").grid(
        row=2, column=0, padx=10, pady=10, sticky="w")
    nome_entry = tk.Entry(janela_fornecedor, width=150)
    nome_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    tk.Label(janela_fornecedor, text="CNPJ:").grid(
        row=3, column=0, padx=10, pady=10, sticky="w")
    cnpj_entry = tk.Entry(janela_fornecedor, width=150)
    cnpj_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    tk.Label(janela_fornecedor, text="Telefone:").grid(
        row=4, column=0, padx=10, pady=10, sticky="w")
    telefone_entry = tk.Entry(janela_fornecedor, width=150)
    telefone_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    tk.Label(janela_fornecedor, text="Email:").grid(
        row=5, column=0, padx=10, pady=10, sticky="w")
    email_entry = tk.Entry(janela_fornecedor, width=150)
    email_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")

    tk.Label(janela_fornecedor, text="Endereço:").grid(
        row=6, column=0, padx=10, pady=10, sticky="w")
    endereco_entry = tk.Entry(janela_fornecedor, width=150)
    endereco_entry.grid(row=6, column=1, padx=10, pady=10, sticky="w")

    frame_botoes = tk.Frame(janela_fornecedor)
    frame_botoes.grid(row=7, column=0, columnspan=2, pady=20)

    tk.Button(frame_botoes, text="Salvar",
              command=salvar_fornecedor).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Editar Fornecedor", command=lambda: editar_fornecedor(
        tree, atualizar_lista_fornecedores)).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Excluir Fornecedor", command=lambda: excluir_fornecedor(
        tree, atualizar_lista_fornecedores, janela_fornecedor)).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Voltar para Home",
              command=janela_fornecedor.destroy).pack(side="left", padx=10)

    tree = ttk.Treeview(janela_fornecedor, columns=(
        "nome", "cnpj", "telefone", "email", "endereco"), show='headings', height=10)
    tree.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    tree.column("nome", width=200, anchor='w')
    tree.column("cnpj", width=90, anchor='center')
    tree.column("telefone", width=90, anchor='center')
    tree.column("email", width=180, anchor='w')
    tree.column("endereco", width=250, anchor='w')

    tree.heading("nome", text="Nome do Fornecedor")
    tree.heading("cnpj", text="CNPJ")
    tree.heading("telefone", text="Telefone")
    tree.heading("email", text="Email")
    tree.heading("endereco", text="Endereço")

    janela_fornecedor.grid_rowconfigure(8, weight=1)
    janela_fornecedor.grid_columnconfigure(0, weight=0)

    atualizar_lista_fornecedores()


if __name__ == "__main__":
    criar_tabela_fornecedores()
    root = tk.Tk()
    root.title("Controle de Estoque de Componentes")
    centralizar_janela(root, 800, 500)
    tk.Button(root, text="Cadastrar Fornecedor",
              command=abrir_janela_cadastro_fornecedores).pack(pady=20)
    root.mainloop()

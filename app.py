import os
import tkinter as tk
from tkinter import PhotoImage, messagebox
import sqlite3
import sys


# Função para conectar ao banco de dados
def conectar_banco():
    try:
        # Caminho absoluto para garantir que o executável encontre o banco de dados
        conn = sqlite3.connect(caminho_banco)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror(
            "Erro", f"Erro ao conectar ao banco de dados App: {e}")
        return None


# Detecta se está rodando como executável ou como script Python
if getattr(sys, 'frozen', False):
    # Está rodando como um executável
    os.environ["ENVIRONMENT"] = "production"
else:
    # Está rodando como script Python normal
    os.environ["ENVIRONMENT"] = "development"

# Obtenha o caminho absoluto do diretório atual
basedir = os.path.dirname(os.path.abspath(__file__))

# Definir o caminho do banco de dados com base no ambiente
if os.environ.get("ENVIRONMENT") == "production":
    caminho_banco = "T:/SETOR PROJETOS/Inmes - Depto. Projetos/db/estoque.db"
else:
    caminho_banco = os.path.join(basedir, 'estoque.db')


# Ajuste da janela do app em relaçao a tela
def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")


def abrir_cadastro_fornecedores():
    import cadastro_fornecedores
    cadastro_fornecedores.abrir_janela_cadastro_fornecedores()


def abrir_cadastro_pecas():
    import cadastro_pecas
    cadastro_pecas.abrir_janela_cadastro_pecas(root)


def abrir_cadastro_clientes():
    import cadastro_clientes
    cadastro_clientes.abrir_janela_cadastro_clientes(root)


# Análise do processo
if os.environ.get("ENVIRONMENT") == "production":
    print("Modo Produção Ativado")
else:
    print("Modo Desenvolvimento Ativado")
# Fim da análise

# Criação da janela principal
root = tk.Tk()
root.title("Controle de Estoque")
root.geometry("800x500")
centralizar_janela(root, 800, 500)


# Adicionando logo
try:
    logo_path = os.path.join(basedir, "logo.png")
    logo = PhotoImage(file=logo_path)
    logo = logo.subsample(2, 2)
    tk.Label(root, image=logo).grid(row=0, column=0, columnspan=2, pady=15)
    root.logo = logo
except tk.TclError:
    print("Erro ao carregar a imagem do logotipo para a página principal.")


# Adicionando botões à janela principal
button_cadastrar_fornecedores = tk.Button(
    root, text="Gerenciar Fornecedores", width=20, command=abrir_cadastro_fornecedores)
button_cadastrar_fornecedores.grid(
    row=2, column=0, padx=10, pady=10, sticky="nsew")

button_cadastrar_pecas = tk.Button(
    root, text="Gerenciar Peças", width=20, command=abrir_cadastro_pecas)
button_cadastrar_pecas.grid(
    row=2, column=1, padx=10, pady=10, sticky="nsew")

button_cadastrar_clientes = tk.Button(
    root, text="Gerenciar Clientes", width=20, command=abrir_cadastro_clientes)
button_cadastrar_clientes.grid(
    row=3, column=0, padx=10, pady=10, sticky="nsew")


# Rodapé
rodape_texto = "Developed by: Icaro Quimaia Rodrigues"
rodape_label = tk.Label(root, text=rodape_texto, font=("Arial", 8), anchor='e')
rodape_label.grid(row=6, column=1, padx=10, pady=0, sticky="se")

# Ajustes de layout
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_rowconfigure(6, weight=1)

# Inicia a interface principal
root.mainloop()

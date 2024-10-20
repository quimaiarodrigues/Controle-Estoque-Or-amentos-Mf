import os
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
import sys
import re


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


def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x-10}+{y-30}")


def criar_tabelas():
    conn = conectar_banco()
    if conn:
        with conn:
            cursor = conn.cursor()

            # Cria a tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT NOT NULL UNIQUE,
                    telefone TEXT,
                    email TEXT,
                    endereco TEXT,
                    modelo TEXT,
                    placa TEXT UNIQUE,
                    ano_fabricacao TEXT,
                    marca TEXT
                )
            ''')


def formatar_cpf_ou_cnpj(cpf_cnpj):
    """Formata o valor como CPF ou CNPJ dependendo da quantidade de dígitos."""
    cpf_cnpj = re.sub(r'\D', '', cpf_cnpj)
    if len(cpf_cnpj) == 11:
        return f"{cpf_cnpj[:3]}.{cpf_cnpj[3:6]}.{cpf_cnpj[6:9]}-{cpf_cnpj[9:]}"
    elif len(cpf_cnpj) == 14:
        return f"{cpf_cnpj[:2]}.{cpf_cnpj[2:5]}.{cpf_cnpj[5:8]}/{cpf_cnpj[8:12]}-{cpf_cnpj[12:]}"
    return cpf_cnpj


def formatar_telefone(telefone):
    """Formata o telefone para o formato (##) #####-#### ou (##) ####-####"""
    telefone = re.sub(r'\D', '', telefone)
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone


def abrir_janela_cadastro_clientes(root):
    def salvar_cliente():
        nome = nome_entry.get().strip()
        cpf_cnpj = formatar_cpf_ou_cnpj(cpf_entry.get().strip())
        telefone = formatar_telefone(telefone_entry.get().strip())
        email = email_entry.get().strip()
        endereco = endereco_entry.get().strip()
        modelo = modelo_combobox.get()
        placa = placa_entry.get().strip()
        ano_fabricacao = ano_fabricacao_entry.get().strip()
        marca = marca_combobox.get()

        if nome and cpf_cnpj and placa:
            try:
                conn = conectar_banco()
                if conn:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO Clientes (nome, cpf, telefone, email, endereco, modelo, placa, ano_fabricacao, marca) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (nome, cpf_cnpj, telefone, email, endereco,
                             modelo, placa, ano_fabricacao, marca)
                        )
                        conn.commit()
                        atualizar_lista_clientes()
                        messagebox.showinfo(
                            "Sucesso", "Cliente cadastrado com sucesso.")
                        limpar_campos()
                        janela_clientes.focus_force()
            except sqlite3.IntegrityError:
                messagebox.showwarning(
                    "Aviso", "O CPF/CNPJ ou a Placa do cliente já existe.")
            janela_clientes.focus_force()
        else:
            messagebox.showwarning(
                "Aviso", "Preencha os campos obrigatórios (Nome, CPF/CNPJ e Placa).")
        janela_clientes.focus_force()

    def editar_cliente():
        selected_item = tree.selection()
        if selected_item:
            cliente = tree.item(selected_item)['values']
            nome, cpf_cnpj, telefone, email, endereco, modelo, placa, ano_fabricacao, marca = cliente

            nome_entry.delete(0, tk.END)
            nome_entry.insert(0, nome)
            cpf_entry.delete(0, tk.END)
            cpf_entry.insert(0, cpf_cnpj)
            telefone_entry.delete(0, tk.END)
            telefone_entry.insert(0, telefone)
            email_entry.delete(0, tk.END)
            email_entry.insert(0, email)
            endereco_entry.delete(0, tk.END)
            endereco_entry.insert(0, endereco)
            modelo_combobox.set(modelo)
            placa_entry.delete(0, tk.END)
            placa_entry.insert(0, placa)
            ano_fabricacao_entry.delete(0, tk.END)
            ano_fabricacao_entry.insert(0, ano_fabricacao)
            marca_combobox.set(marca)

            salvar_edicao_btn.config(state=tk.NORMAL)

    def salvar_edicao():
        novo_nome = nome_entry.get().strip()
        novo_cpf_cnpj = formatar_cpf_ou_cnpj(cpf_entry.get().strip())
        novo_telefone = formatar_telefone(telefone_entry.get().strip())
        novo_email = email_entry.get().strip()
        novo_endereco = endereco_entry.get().strip()
        novo_modelo = modelo_combobox.get()
        nova_placa = placa_entry.get().strip()
        novo_ano_fabricacao = ano_fabricacao_entry.get().strip()
        nova_marca = marca_combobox.get()

        selected_item = tree.selection()
        if selected_item:
            cpf_cnpj_original = tree.item(selected_item)['values'][1]

        if novo_nome and novo_cpf_cnpj and nova_placa:
            try:
                conn = conectar_banco()
                if conn:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE Clientes SET nome = ?, cpf = ?, telefone = ?, email = ?, endereco = ?, modelo = ?, placa = ?, ano_fabricacao = ?, marca = ? WHERE cpf = ?",
                            (novo_nome, novo_cpf_cnpj, novo_telefone, novo_email,
                             novo_endereco, novo_modelo, nova_placa, novo_ano_fabricacao, nova_marca, cpf_cnpj_original)
                        )
                        conn.commit()
                        atualizar_lista_clientes()
                        messagebox.showinfo(
                            "Sucesso", "Cliente atualizado com sucesso.")
                        limpar_campos()
                        salvar_edicao_btn.config(state=tk.DISABLED)
                        janela_clientes.focus_force()
            except sqlite3.IntegrityError:
                messagebox.showwarning(
                    "Aviso", "O CPF/CNPJ ou a Placa do cliente já existe.")
            janela_clientes.focus_force()
        else:
            messagebox.showwarning(
                "Aviso", "Preencha os campos obrigatórios (Nome, CPF/CNPJ e Placa).")
        janela_clientes.focus_force()

    def excluir_cliente():
        selected_item = tree.selection()
        if selected_item:
            cliente = tree.item(selected_item)['values']
            cpf_cnpj = cliente[1]

            confirm = messagebox.askyesno(
                "Confirmação", f"Deseja realmente excluir o cliente com CPF/CNPJ {cpf_cnpj}?")
            if confirm:
                try:
                    conn = conectar_banco()
                    if conn:
                        with conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "DELETE FROM Clientes WHERE cpf = ?", (cpf_cnpj,))
                            conn.commit()
                            atualizar_lista_clientes()
                            messagebox.showinfo(
                                "Sucesso", "Cliente excluído com sucesso.")
                            limpar_campos()
                            janela_clientes.focus_force()
                except sqlite3.Error as e:
                    messagebox.showerror(
                        "Erro", f"Erro ao excluir cliente: {e}")
        else:
            messagebox.showwarning(
                "Aviso", "Selecione um cliente para excluir.")
            janela_clientes.focus_force()

    def limpar_campos():
        nome_entry.delete(0, tk.END)
        cpf_entry.delete(0, tk.END)
        telefone_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        endereco_entry.delete(0, tk.END)
        modelo_combobox.set('')
        placa_entry.delete(0, tk.END)
        ano_fabricacao_entry.delete(0, tk.END)
        marca_combobox.set('')

    def atualizar_modelos(event):
        marca_selecionada = marca_combobox.get()
        modelos = modelos_por_marca.get(marca_selecionada, [])
        modelo_combobox['values'] = modelos
        modelo_combobox.set('')

    def atualizar_lista_clientes():
        for item in tree.get_children():
            tree.delete(item)
        conn = conectar_banco()
        if conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT nome, cpf, telefone, email, endereco, modelo, placa, ano_fabricacao, marca FROM Clientes ORDER BY nome"
                )
                clientes = cursor.fetchall()
                for cliente in clientes:
                    nome, cpf_cnpj, telefone, email, endereco, modelo, placa, ano_fabricacao, marca = cliente
                    cpf_cnpj_formatado = formatar_cpf_ou_cnpj(cpf_cnpj)
                    telefone_formatado = formatar_telefone(telefone)
                    tree.insert('', tk.END, values=(
                        nome, cpf_cnpj_formatado, telefone_formatado, email, endereco, modelo, placa, ano_fabricacao, marca))

    janela_clientes = tk.Toplevel(root)
    janela_clientes.title("Cadastro de Clientes")
    centralizar_janela(janela_clientes, 1350, 650)
    janela_clientes.focus_force()

    # Adicionar a logo
    try:
        logo_path = os.path.join(basedir, "logo.png")
        logo = PhotoImage(file=logo_path)
        logo = logo.subsample(2, 2)
        tk.Label(janela_clientes, image=logo).grid(
            row=0, column=0, columnspan=2, pady=15)
        janela_clientes.logo = logo
    except tk.TclError:
        print("Erro ao carregar a imagem do logotipo.")

    frame_campos = tk.Frame(janela_clientes)
    frame_campos.grid(row=1, column=0, padx=10, pady=10, sticky='w')

    tk.Label(frame_campos, text="Nome:").grid(
        row=0, column=0, padx=5, pady=5, sticky='e')
    nome_entry = tk.Entry(frame_campos, width=50)
    nome_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_campos, text="CPF/CNPJ:").grid(
        row=1, column=0, padx=5, pady=5, sticky='e')
    cpf_entry = tk.Entry(frame_campos, width=50)
    cpf_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_campos, text="Telefone:").grid(
        row=2, column=0, padx=5, pady=5, sticky='e')
    telefone_entry = tk.Entry(frame_campos, width=50)
    telefone_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_campos, text="Email:").grid(
        row=3, column=0, padx=5, pady=5, sticky='e')
    email_entry = tk.Entry(frame_campos, width=50)
    email_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(frame_campos, text="Endereço:").grid(
        row=4, column=0, padx=5, pady=5, sticky='e')
    endereco_entry = tk.Entry(frame_campos, width=50)
    endereco_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(frame_campos, text="Marca:").grid(
        row=0, column=2, padx=5, pady=5, sticky='e')

    modelos_por_marca = {
        "Toyota": [
            "Corolla", "Hilux", "Yaris", "Camry", "Rav4", "Land Cruiser", "Tacoma", "Avalon", "Sienna", "Supra",
            "4Runner", "Highlander", "Prius", "Sequoia", "Tundra", "Celica", "MR2", "Echo", "Matrix", "Venza",
            "C-HR", "FJ Cruiser", "Crown", "Alphard", "Fortuner", "Verso"
        ],
        "Ford": [
            "Fiesta", "Ranger", "EcoSport", "Focus", "Mustang", "F-150", "Fusion", "Escape", "Explorer", "Expedition",
            "Bronco", "Maverick", "Edge", "Transit", "Taurus", "C-Max", "Kuga", "F-250", "F-350", "F-450",
            "Galaxy", "S-Max", "Courier", "Ka", "Escort", "Mondeo", "Thunderbird", "Crown Victoria", "Fairlane"
        ],
        "Volkswagen": [
            "Gol", "Tiguan", "Jetta", "Passat", "T-Cross", "Polo", "Virtus", "Golf", "Touareg", "Amarok",
            "Fox", "Atlas", "ID.4", "Arteon", "Up", "Beetle", "Kombi", "Parati", "Voyage", "Santana",
            "Scirocco", "Sharan", "Transporter", "Caddy", "CrossFox", "Eos", "Vento", "ID. Buzz", "New Beetle"
        ],
        "Chevrolet": [
            "Onix", "Cruze", "S10", "Spin", "Tracker", "Equinox", "Blazer", "Trailblazer", "Suburban", "Tahoe",
            "Malibu", "Camaro", "Silverado", "Traverse", "Cobalt", "Prisma", "Opala", "Monza", "Astra", "Zafira",
            "Vectra", "Classic", "Montana", "Corvette", "Impala", "Avalanche", "Express", "Volt", "Chevette"
        ],
        "Honda": [
            "Civic", "HR-V", "Fit", "CR-V", "City", "Accord", "Odyssey", "Pilot", "Ridgeline", "Passport",
            "NSX", "Element", "Insight", "Prelude", "S2000", "Legend", "Jazz", "Integra", "Crossroad", "Stream",
            "HRR", "Crosstour", "Airwave", "Stepwgn", "Brio"
        ],
        "Fiat": [
            "Uno", "Argo", "Toro", "Mobi", "Cronos", "Strada", "500", "Punto", "Tipo", "Doblò",
            "Freemont", "Palio", "Linea", "Bravo", "Siena", "Fiorino", "Tempra", "Idea", "Panda", "Multipla",
            "Stilo", "Albea", "Croma", "Marea", "Ducato", "Punto Evo", "Qubo"
        ],
        "Hyundai": [
            "HB20", "Creta", "Tucson", "Santa Fe", "Elantra", "Sonata", "Kona", "Palisade", "Ioniq", "Veloster",
            "Accent", "Azera", "Genesis", "Venue", "Matrix", "Getz", "Terracan", "Xcent", "Veracruz", "Atos",
            "Galloper", "Porter", "Santamo", "Grandeur"
        ],
        "Nissan": [
            "Kicks", "Versa", "Frontier", "March", "Sentra", "Altima", "Maxima", "Murano", "Pathfinder", "GT-R",
            "Leaf", "370Z", "Rogue", "Armada", "X-Trail", "Titan", "Navara", "Qashqai", "Juke", "Cube",
            "Sunny", "Bluebird", "Laurel", "Cedric", "Terrano", "Stagea", "Silvia", "Skyline"
        ],
        "Jeep": [
            "Renegade", "Compass", "Wrangler", "Grand Cherokee", "Cherokee", "Gladiator", "Patriot", "Commander", "Wagoneer",
            "Liberty", "Trailhawk", "Trackhawk", "Willys", "CJ", "Scrambler", "J10", "Comanche", "XJ", "ZJ", "YJ"
        ],
        "Renault": [
            "Kwid", "Duster", "Sandero", "Captur", "Logan", "Clio", "Megane", "Koleos", "Scenic", "Twingo",
            "Zoe", "Trafic", "Master", "Alaskan", "Laguna", "Espace", "Fluence", "Modus", "Vel Satis", "Dauphine",
            "Arkana", "Kadjar", "Kaptur"
        ],
        "Peugeot": [
            "208", "2008", "3008", "408", "Expert", "5008", "508", "Partner", "Rifter", "Traveller",
            "307", "207", "4008", "206", "605", "406", "405", "607", "108", "308",
            "RCZ", "Bipper", "Boxer", "Expert Tepee"
        ],
        "Mitsubishi": [
            "L200", "ASX", "Pajero", "Outlander", "Eclipse Cross", "Mirage", "Montero", "Galant", "Lancer", "Triton",
            "Space Star", "Delica", "Endeavor", "Eclipse", "Diamante", "i-MiEV", "Attrage", "Starion", "Sigma", "RVR"
        ],
        "Kia": [
            "Sportage", "Picanto", "Sorento", "Cerato", "Optima", "Seltos", "Rio", "Stinger", "Carnival", "Telluride",
            "Soul", "Niro", "Cadenza", "Mohave", "Carens", "Sephia", "Amanti", "Borrego", "K900", "Spectra"
        ],
        "Mazda": [
            "CX-5", "Mazda3", "Mazda6", "CX-30", "CX-9", "MX-5 Miata", "CX-3", "RX-8", "Mazda2", "Mazda5",
            "BT-50", "Mazda MX-30", "Mazda RX-7", "Tribute", "Millenia", "MPV", "Mazda CX-7", "Mazda3 MPS"
        ],
        "Citroën": [
            "C3", "C4 Cactus", "C5 Aircross", "Berlingo", "C4", "C3 Aircross", "DS5", "C5 X", "DS7", "SpaceTourer",
            "C1", "C2", "Jumpy", "DS4", "Saxo", "Xsara", "C4 Picasso", "Evasion", "C6", "C8"
        ],
        "Subaru": [
            "Impreza", "Outback", "Forester", "XV", "WRX", "Legacy", "Ascent", "BRZ", "Levorg", "Tribeca",
            "Baja", "Crosstrek", "SVX", "Justy", "Liberty", "Loyale", "GL", "RX Turbo"
        ],
        "Chery": [
            "Tiggo 5x", "Arrizo 5", "Tiggo 7", "QQ", "Tiggo 8", "Arrizo 6", "Tiggo 3x", "Arrizo 3", "Tiggo 2", "Arrizo 7",
            "Tiggo 4", "eQ1", "Fulwin", "Cowin", "E5"
        ],
        "JAC": [
            "T40", "T50", "T60", "iEV20", "iEV40", "iEV60", "J6", "T8", "iEV330P", "J7", "JS4", "J5",
            "M3", "S2", "S5", "Refine", "J4", "M4", "S7"
        ],
        "Dodge": [
            "Journey", "Durango", "Charger", "Challenger", "Dart", "Ram 1500", "Ram 2500", "Ram 3500", "Nitro", "Viper",
            "Caliber", "Avenger", "Neon", "Magnum", "Intrepid", "Stratus", "Caravan"
        ],
        "RAM": [
            "1500", "2500", "3500", "ProMaster City", "ProMaster 1500", "ProMaster 2500", "ProMaster 3500"
        ],
        "Chrysler": [
            "300C", "Pacifica", "Voyager", "Aspen", "Crossfire", "Sebring", "Town & Country", "300M", "Neon", "Imperial"
        ],
        "GMC": [
            "Sierra", "Acadia", "Canyon", "Terrain", "Yukon", "Denali", "Envoy", "Savana", "Jimmy", "Safari",
            "Suburban", "Typhoon", "Hummer H3T"
        ],
        "Buick": [
            "Encore", "Enclave", "Regal", "LaCrosse", "Envision", "Verano", "Cascada", "Roadmaster", "Electra", "LeSabre",
            "Riviera", "Century", "Park Avenue", "Reatta", "Skyhawk"
        ],
        "Suzuki": [
            "Jimny", "Vitara", "Swift", "Celerio", "SX4", "S-Cross", "Alto", "Baleno", "Ignis", "Ertiga",
            "Grand Vitara", "Kizashi", "XL7", "APV", "Splash", "Wagon R", "Esteem", "Cultus"
        ],
    }

    marcas = sorted(modelos_por_marca.keys())
    marca_combobox = ttk.Combobox(frame_campos, values=marcas, width=47)
    marca_combobox.grid(row=0, column=3, padx=5, pady=5)
    marca_combobox.bind("<<ComboboxSelected>>", atualizar_modelos)

    tk.Label(frame_campos, text="Modelo:").grid(
        row=1, column=2, padx=5, pady=5, sticky='e')
    modelo_combobox = ttk.Combobox(frame_campos, width=47)
    modelo_combobox.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(frame_campos, text="Ano de Fabricação/Motorização:").grid(
        row=2, column=2, padx=5, pady=5, sticky='e')
    ano_fabricacao_entry = tk.Entry(frame_campos, width=50)
    ano_fabricacao_entry.grid(row=2, column=3, padx=5, pady=5)

    tk.Label(frame_campos, text="Placa:").grid(
        row=3, column=2, padx=5, pady=5, sticky='e')
    placa_entry = tk.Entry(frame_campos, width=50)
    placa_entry.grid(row=3, column=3, padx=5, pady=5)

    frame_botoes = tk.Frame(frame_campos)
    frame_botoes.grid(row=4, column=3, pady=10, sticky='w')

    tk.Button(frame_botoes, text="Salvar",
              command=salvar_cliente).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Editar",
              command=editar_cliente).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Excluir",
              command=excluir_cliente).pack(side=tk.LEFT, padx=5)
    salvar_edicao_btn = tk.Button(
        frame_botoes, text="Salvar Edição", command=salvar_edicao, state=tk.DISABLED)
    salvar_edicao_btn.pack(side=tk.LEFT, padx=5)

    tk.Button(frame_botoes, text="Voltar para Home",
              command=janela_clientes.destroy).pack(side="left", padx=10)

    tree = ttk.Treeview(janela_clientes, columns=(
        "nome", "cpf", "telefone", "email", "endereco", "modelo", "placa", "ano_fabricacao", "marca"), show='headings')
    tree.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

    tree.heading("nome", text="Nome")
    tree.heading("cpf", text="CPF/CNPJ")
    tree.heading("telefone", text="Telefone")
    tree.heading("email", text="Email")
    tree.heading("endereco", text="Endereço")
    tree.heading("modelo", text="Modelo")
    tree.heading("placa", text="Placa")
    tree.heading("ano_fabricacao", text="Ano de Fabricação")
    tree.heading("marca", text="Marca")

    tree.column("nome", width=150)
    tree.column("cpf", width=130, anchor='center')
    tree.column("telefone", width=130, anchor='center')
    tree.column("email", width=150)
    tree.column("endereco", width=150)
    tree.column("modelo", width=100)
    tree.column("placa", width=100, anchor='center')
    tree.column("ano_fabricacao", width=100, anchor='center')
    tree.column("marca", width=120)

    janela_clientes.grid_rowconfigure(6, weight=1)
    janela_clientes.grid_columnconfigure(0, weight=1)
    janela_clientes.grid_columnconfigure(1, weight=1)

    atualizar_lista_clientes()
    janela_clientes.mainloop()

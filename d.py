import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('estoque.db')
cursor = conn.cursor()
# Drop as tabelas, caso existam
cursor.execute('DROP TABLE IF EXISTS Fornecedores')
cursor.execute('DROP TABLE IF EXISTS Pecas')
# Criação das tabelas novamente
cursor.execute('''
        CREATE TABLE Fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT NOT NULL UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT
        )
    ''')
cursor.execute('''
        CREATE TABLE Pecas (
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
conn.commit()
conn.close()

print("Nova tabela 'Clientes' criada com sucesso.")

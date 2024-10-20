import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('estoque.db')
cursor = conn.cursor()

# Apagar a tabela antiga, caso exista
cursor.execute("DROP TABLE IF EXISTS Clientes")

# Criar a tabela nova com a estrutura desejada
cursor.execute('''
    CREATE TABLE Clientes (
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

# Confirmar as alterações e fechar a conexão
conn.commit()
conn.close()

print("Nova tabela 'Clientes' criada com sucesso.")

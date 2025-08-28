import sqlite3

# Conectar ao banco de dados (cria o arquivo se não existir)
conn = sqlite3.connect('machines.db')
cursor = conn.cursor()

# Comando para criar a tabela
create_table_query = '''
CREATE TABLE IF NOT EXISTS machines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    technician_name TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    ticket_number TEXT NOT NULL,
    location TEXT NOT NULL,
    demand TEXT,
    formatted TEXT,
    backup TEXT,
    tombamento TEXT,
    report_date TEXT
);
'''

# Executar o comando
cursor.execute(create_table_query)

# Salvar (commit) as mudanças
conn.commit()

# Fechar a conexão
conn.close()

print("Tabela 'machines' criada com sucesso.")

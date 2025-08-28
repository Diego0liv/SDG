from app import db, Equipamento, SaidaEquipamento  # Importando o app e os modelos do banco de dados
from flask import Flask

# Função para zerar os dados
def zerar_dados():
    try:
        # Remover todos os registros das tabelas
        Equipamento.query.delete()  # Exclui todos os registros da tabela Equipamento
        SaidaEquipamento.query.delete()  # Exclui todos os registros da tabela SaidaEquipamento
        
        # Commit para confirmar as mudanças no banco
        db.session.commit()

        print("Dados zerados com sucesso!")
    except Exception as e:
        db.session.rollback()  # Caso ocorra algum erro, desfaz as alterações
        print(f"Erro ao zerar os dados: {str(e)}")

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    # Inicializa o Flask app (importante para usar o contexto do banco de dados)
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laboratorio.db'  # Defina o URI do banco de dados
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)  # Inicializa o banco de dados com o Flask app

    # Chama a função para zerar os dados
    with app.app_context():
        zerar_dados()

from flask import Flask, render_template, request, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.pdfgen import canvas
from io import BytesIO

# Configuração do banco de dados SQLite
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laboratorio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Equipamento
class Equipamento(db.Model):
    __tablename__ = 'entrada_equipamentos'  # Garantir que o nome da tabela seja o mesmo
    id = db.Column(db.Integer, primary_key=True)
    numero_equipamento = db.Column(db.String(255), nullable=False)
    numero_chamado = db.Column(db.String(255), nullable=False)
    nome_tecnico = db.Column(db.String(255), nullable=False)
    defeito = db.Column(db.String(255), nullable=False)
    formatacao = db.Column(db.Boolean, nullable=False)
    backup = db.Column(db.Boolean, nullable=False)
    data_entrada = db.Column(db.Date, nullable=False)  # Data de entrada do equipamento

    def __init__(self, numero_equipamento, numero_chamado, nome_tecnico, defeito, formatacao, backup, data_entrada):
        self.numero_equipamento = numero_equipamento
        self.numero_chamado = numero_chamado
        self.nome_tecnico = nome_tecnico
        self.defeito = defeito
        self.formatacao = formatacao
        self.backup = backup
        self.data_entrada = data_entrada

# Modelo de Saída de Equipamento
class SaidaEquipamento(db.Model):
    __tablename__ = 'saida_equipamentos'  # Nome da tabela no banco de dados

    id = db.Column(db.Integer, primary_key=True)
    numero_equipamento = db.Column(db.String(255), nullable=False)
    numero_chamado = db.Column(db.String(255), nullable=False)
    tecnico_responsavel = db.Column(db.String(255), nullable=False)
    servicos_realizados = db.Column(db.String(255), nullable=True)
    destino = db.Column(db.String(255), nullable=False)
    data_saida = db.Column(db.Date, nullable=False)  # Data de saída

    def __init__(self, numero_equipamento, numero_chamado, tecnico_responsavel, servicos_realizados, destino, data_saida):
        self.numero_equipamento = numero_equipamento
        self.numero_chamado = numero_chamado
        self.tecnico_responsavel = tecnico_responsavel
        self.servicos_realizados = servicos_realizados
        self.destino = destino
        self.data_saida = data_saida


# Rota para a página principal
@app.route('/')
def index():
    return render_template('index.html')


# Rota para o cadastro de equipamentos (entrada)
@app.route('/entrada', methods=['GET', 'POST'])
def entrada():
    if request.method == 'POST':
        numero_equipamento = request.form['numero_equipamento']
        numero_chamado = request.form['numero_chamado']
        nome_tecnico = request.form['nome_tecnico']
        defeito = request.form['defeito']
        formatacao = 'formatacao' in request.form  # Verifica se foi marcado
        backup = 'backup' in request.form  # Verifica se foi marcado
        data_entrada = datetime.today().date()  # Data de entrada é o dia atual

        # Criação de um novo equipamento e salvamento no banco
        novo_equipamento = Equipamento(
            numero_equipamento=numero_equipamento,
            numero_chamado=numero_chamado,
            nome_tecnico=nome_tecnico,
            defeito=defeito,
            formatacao=formatacao,
            backup=backup,
            data_entrada=data_entrada
        )
        db.session.add(novo_equipamento)
        db.session.commit()  # Salva no banco de dados

        return render_template('entrada.html', message="Equipamento cadastrado com sucesso!")

    return render_template('entrada.html')


# Rota para o relatório de entrada de equipamentos
@app.route('/relatorio_entrada', methods=['GET', 'POST'])
def relatorio_entrada():
    equipamentos = []
    data_inicio = data_fim = None
    hoje = datetime.today()  # Variável para a data atual

    if request.method == 'POST':
        filtro_periodo = request.form['filtro_periodo']

        if filtro_periodo == 'dia':
            data_inicio = datetime.today().date()
            data_fim = data_inicio
        elif filtro_periodo == 'semana':
            data_inicio = (datetime.today() - timedelta(days=datetime.today().weekday())).date()
            data_fim = data_inicio + timedelta(days=6)
        elif filtro_periodo == 'mes':
            data_inicio = datetime.today().replace(day=1).date()  # Primeiro dia do mês
            next_month = datetime.today().replace(day=28) + timedelta(days=4)  # Vai para o próximo mês
            data_fim = next_month - timedelta(days=next_month.day)  # Ajusta para o último dia do mês atual

        # Consulta os equipamentos com base no período selecionado
        equipamentos = Equipamento.query.filter(
            Equipamento.data_entrada.between(data_inicio, data_fim)
        ).all()

    return render_template('relatorio_entrada.html', equipamentos=equipamentos, data_inicio=data_inicio, data_fim=data_fim, hoje=hoje)


# Rota para exportar o relatório de entrada em PDF
@app.route('/relatorio_entrada/baixar', methods=['GET'])
def baixar_relatorio_entrada():
    # Recupera todos os equipamentos cadastrados
    equipamentos = Equipamento.query.all()

    # Criando um buffer de memória para o PDF
    buffer = BytesIO()

    # Criando o documento PDF
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    c.setFont("Helvetica", 10)
    
    # Cabeçalho do relatório
    c.drawString(100, 550, 'Relatório de Entrada de Equipamentos')
    c.drawString(100, 535, f'Data: {datetime.today().date()}')

    # Desenhando o título das colunas
    c.drawString(50, 500, 'Tombamento')
    c.drawString(150, 500, 'Chamado')
    c.drawString(225, 500, 'Técnico')
    c.drawString(320, 500, 'Defeito')
    c.drawString(750, 500, 'Data de Entrada')

    y_position = 480  # Começo das linhas de dados

    # Preenchendo os dados do relatório
    for equipamento in equipamentos:
        # Antes de desenhar a linha, verifique se há espaço suficiente
        if y_position < 80:
            c.showPage()  # Cria uma nova página
            y_position = 500  # Reseta a posição para o topo da nova página
        
        c.drawString(50, y_position, equipamento.numero_equipamento)
        c.drawString(150, y_position, equipamento.numero_chamado)
        c.drawString(225, y_position, equipamento.nome_tecnico)
        c.drawString(320, y_position, equipamento.defeito)
        c.drawString(760, y_position, str(equipamento.data_entrada))

        y_position -= 20  # Desce para a próxima linha

    # Salvando o PDF no buffer
    c.save()

    # Retornando o PDF como resposta para o download
    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf', headers={'Content-Disposition': 'attachment; filename=relatorio_entrada.pdf'})



# Rota para o cadastro de saída de equipamentos
@app.route('/saida', methods=['GET', 'POST'])
def saida():
    if request.method == 'POST':
        numero_equipamento = request.form['numero_equipamento']
        numero_chamado = request.form['numero_chamado']
        tecnico_responsavel = request.form['tecnico_responsavel']
        destino = request.form['destino']
        
        # Obtendo os serviços realizados a partir dos checkboxes
        servicos_realizados = ', '.join(request.form.getlist('servicos'))  # Junta os serviços em uma string

        data_saida = datetime.today().date()  # A data de saída é o dia atual

        # Criação de um novo equipamento de saída e salvamento no banco de dados
        novo_equipamento_saida = SaidaEquipamento(
            numero_equipamento=numero_equipamento,
            numero_chamado=numero_chamado,
            tecnico_responsavel=tecnico_responsavel,
            servicos_realizados=servicos_realizados,
            destino=destino,
            data_saida=data_saida
        )
        db.session.add(novo_equipamento_saida)
        db.session.commit()  # Salva no banco de dados

        return render_template('saida.html', message="Equipamento registrado para saída com sucesso!")

    return render_template('saida.html')


# Rota para o relatório de saída de equipamentos
@app.route('/relatorio_saida', methods=['GET', 'POST'])
def relatorio_saida():
    equipamentos_saida = []
    
    if request.method == 'POST':
        # Lógica de filtragem ou processamento de dados enviados via POST
        pass
    
    # Recupera todos os equipamentos cadastrados para saída
    equipamentos_saida = SaidaEquipamento.query.all()

    # Se for uma solicitação POST, cria o PDF e retorna o arquivo
    if request.method == 'POST':
        # Criando um buffer de memória para o PDF
        buffer = BytesIO()

        # Criando o documento PDF
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        c.setFont("Helvetica", 10)

        # Cabeçalho do relatório
        c.drawString(100, 550, 'Relatório de Saída de Equipamentos')
        c.drawString(100, 535, f'Data: {datetime.today().date()}')

        # Desenhando o título das colunas
        c.drawString(50, 500, 'Tombamento')
        c.drawString(150, 500, 'Chamado')
        c.drawString(220, 500, 'Técnico')
        c.drawString(320, 500, 'Defeito')
        c.drawString(700, 500, 'Data de Saída')

        y_position = 480  # Começo das linhas de dados

        # Preenchendo os dados do relatório
        for equipamento in equipamentos_saida:
            c.drawString(50, y_position, equipamento.numero_equipamento)
            c.drawString(150, y_position, equipamento.numero_chamado)
            c.drawString(220, y_position, equipamento.tecnico_responsavel)
            c.drawString(320, y_position, equipamento.servicos_realizados)
            c.drawString(700, y_position, str(equipamento.data_saida))

            y_position -= 20  # Desce para a próxima linha

            # Se o conteúdo ultrapassar uma página, insere uma nova página
            if y_position < 80:
                c.showPage()
                y_position = 750

        c.save()

        # Preparando o conteúdo para download
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="relatorio_saida.pdf", mimetype="application/pdf")
    
    # Se for uma solicitação GET, apenas exibe a página com os equipamentos
    return render_template('relatorio_saida.html', equipamentos_saida=equipamentos_saida)


if __name__ == '__main__':
    # Utiliza o contexto da aplicação para criar as tabelas
    with app.app_context():
        db.create_all()  # Cria todas as tabelas no banco de dados, incluindo 'entrada_equipamentos' e 'saida_equipamentos'
    app.run(debug=True)

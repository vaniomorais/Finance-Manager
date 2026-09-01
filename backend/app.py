from flask import Flask, jsonify, request
from flask_cors import CORS
from models.models import db, User, Transaction
from flasgger import Swagger
from pydantic import ValidationError
from schemas import UserCreate, TransactionCreate

# CONFIGURAÇÃO INICIAL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
swagger = Swagger(app)
db.init_app(app)

# CONSTANTES

TRANSACTION_TYPES = {
    'INCOME': 'income',
    'EXPENSE': 'expense'
}

# FUNÇÕES AUXILIARES

def calculate_summary(transactions):
    # Calcula resumo financeiro (renda, despesas, saldo) a partir de uma lista de transações.

    income = sum(t.amount for t in transactions if t.type == TRANSACTION_TYPES['INCOME'])
    expenses = sum(t.amount for t in transactions if t.type == TRANSACTION_TYPES['EXPENSE'])
    balance = income - expenses
    
    return {
        'income': income,
        'expenses': expenses,
        'balance': balance
    }


def handle_validation_error(e):
    # Converte erro de validação do Pydantic em resposta JSON estruturada.

    error_details = [{'field': err['loc'][0], 'message': err['msg']} for err in e.errors()]
    return jsonify({
        'error': 'Erro na validação dos dados',
        'details': error_details
    }), 400


# ROTAS DA API - USUÁRIOS

@app.route('/users', methods=['GET'])
def get_users():
    """
    Lista todos os usuários com seus saldos calculados.
    ---
    tags:
      - Usuários
    responses:
      200:
        description: Lista de usuários com saldos
      500:
        description: Erro no servidor
    """
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            user_dict = user.to_dict()
            # Calcula o saldo do usuário usando função auxiliar
            summary = calculate_summary(user.transactions)
            user_dict['balance'] = summary['balance']
            user_dict['transaction_count'] = len(user.transactions)
            users_data.append(user_dict)
        
        return jsonify(users_data), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuários: {str(e)}'}), 500


@app.route('/users', methods=['POST'])
def create_user():
    """
    Cria um novo usuário com dados validados.
    ---
    tags:
      - Usuários
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            name:
              type: string
              description: Nome do usuário
              required: true
            initials:
              type: string
              description: Iniciais do nome
              required: true
            avatar_color:
              type: string
              description: Cor hexadecimal do avatar
              required: true
    responses:
      201:
        description: Usuário criado com sucesso
      400:
        description: Erro na validação dos dados
      500:
        description: Erro no servidor
    """
    try:
        data = request.get_json()
        user_data = UserCreate(**data)
        
        new_user = User(
            name=user_data.name,
            initials=user_data.initials,
            avatar_color=user_data.avatar_color
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(new_user.to_dict()), 201
    
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500


# ROTAS DA API - TRANSAÇÕES

@app.route('/transactions', methods=['GET'])
def get_all_transactions():
    """
    Retorna todas as transações do grupo familiar com resumo consolidado.
    ---
    tags:
      - Transações
    responses:
      200:
        description: Todas as transações com balanço financeiro do grupo familiar
      500:
        description: Erro no servidor
    """
    try:
        all_transactions = Transaction.query.all()
        
        # Calcula resumo usando função auxiliar
        summary = calculate_summary(all_transactions)
        
        # Monta lista de transações com dados do membro
        transactions_with_member = []
        for t in all_transactions:
            tx_dict = t.to_dict()
            tx_dict['member_name'] = t.user.name
            transactions_with_member.append(tx_dict)
        
        return jsonify({
            'summary': summary,
            'transactions': transactions_with_member,
            'transaction_count': len(all_transactions)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transações: {str(e)}'}), 500


@app.route('/users/<int:user_id>/transactions', methods=['GET'])
def get_user_transactions(user_id):
    """
    Retorna as transações e resumo financeiro de um usuário específico.
    ---
    tags:
      - Transações
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Transações e resumo do usuário
      404:
        description: Usuário não encontrado
      500:
        description: Erro no servidor
    """
    try:
        user = User.query.get_or_404(user_id)
        
        # Calcula resumo usando função auxiliar
        summary = calculate_summary(user.transactions)
        
        return jsonify({
            'user': user.name,
            'summary': summary,
            'transactions': [t.to_dict() for t in user.transactions]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transações do usuário: {str(e)}'}), 500


@app.route('/users/<int:user_id>/transactions', methods=['POST'])
def create_transaction(user_id):
    """
    Cria uma nova transação para um usuário específico.
    ---
    tags:
      - Transações
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            title:
              type: string
              description: Título/descrição da transação
              required: true
            amount:
              type: number
              description: Valor da transação
              required: true
            type:
              type: string
              enum: ['income', 'expense']
              description: Tipo da transação
              required: true
            category:
              type: string
              description: Categoria da transação
              required: true
            date:
              type: string
              format: date
              description: Data da transação (YYYY-MM-DD)
              required: true
    responses:
      201:
        description: Transação criada com sucesso
      400:
        description: Erro na validação dos dados
      404:
        description: Usuário não encontrado
      500:
        description: Erro no servidor
    """
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validação com Pydantic
        transaction_data = TransactionCreate(**data)
        
        new_transaction = Transaction(
            title=transaction_data.title,
            amount=transaction_data.amount,
            type=transaction_data.type,
            category=transaction_data.category,
            date=transaction_data.date,
            user_id=user.id
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return jsonify(new_transaction.to_dict()), 201
    
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        return jsonify({'error': f'Erro ao criar transação: {str(e)}'}), 500


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Deleta um usuário e todas as suas transações associadas.
    ---
    tags:
      - Usuários
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Usuário deletado com sucesso
      404:
        description: Usuário não encontrado
      500:
        description: Erro no servidor
    """
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'Usuário {user.name} deletado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar usuário: {str(e)}'}), 500


@app.route('/transactions/<int:tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    """
    Deleta uma transação específica.
    ---
    tags:
      - Transações
    parameters:
      - name: tx_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Transação deletada com sucesso
      404:
        description: Transação não encontrada
      500:
        description: Erro no servidor
    """
    try:
        transaction = Transaction.query.get_or_404(tx_id)
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': f'Transação "{transaction.title}" deletada com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar transação: {str(e)}'}), 500

# INICIALIZAÇÃO DO APLICATIVO

if __name__ == '__main__':
    # Cria tabelas do banco de dados se não existirem
    with app.app_context():
        db.create_all()
    
    # Inicia servidor em modo debug
    app.run(debug=True, host='127.0.0.1', port=5000)
    
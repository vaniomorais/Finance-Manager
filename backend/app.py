from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import NotFound
from models.models import db, User, Transaction
from flask_swagger_ui import get_swaggerui_blueprint
from pydantic import ValidationError
from schemas import UserCreate, TransactionCreate
from openapi_spec import openapi_spec

# CONFIGURAÇÃO INICIAL DO APP E BANCO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

OPENAPI_URL = '/openapi.json'
SWAGGER_URL = '/docs'

swagger_ui = get_swaggerui_blueprint(
  SWAGGER_URL,
  OPENAPI_URL,
  config={'app_name': 'Finance Manager API'}
)
app.register_blueprint(swagger_ui, url_prefix=SWAGGER_URL)


@app.route(OPENAPI_URL, methods=['GET'])
def get_openapi_spec():
  return jsonify(openapi_spec)

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


def validation_error(e):
    # Converte erro de validação do Pydantic em resposta JSON.

    error_details = [{'field': err['loc'][0], 'message': err['msg']} for err in e.errors()]
    return jsonify({
        'error': 'Erro na validação dos dados',
        'details': error_details
    }), 400


# ROTAS DA API - USUÁRIOS

@app.route('/users', methods=['GET'])
def get_users():
    #Lista todos os usuários com seus saldos calculados.
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
    #Cria um novo usuário com dados validados.
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
        return validation_error(e)
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500


# ROTAS DA API - TRANSAÇÕES

@app.route('/transactions', methods=['GET'])
def get_all_transactions():
    
    #Retorna todas as transações do grupo familiar com resumo consolidado.
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
            'transaction_count': len(all_transactions)}), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transações: {str(e)}'}), 500


@app.route('/users/<int:user_id>/transactions', methods=['GET'])
def get_user_transactions(user_id):
    #Retorna as transações e resumo financeiro de um usuário específico.
    try:
        user = User.query.get_or_404(user_id)
        
        # Calcula resumo usando função auxiliar
        summary = calculate_summary(user.transactions)
        
        return jsonify({
            'user': user.name,
            'summary': summary,
            'transactions': [t.to_dict() for t in user.transactions]
        }), 200
    
    except NotFound:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transações do usuário: {str(e)}'}), 500


@app.route('/users/<int:user_id>/transactions', methods=['POST'])
def create_transaction(user_id):
    #Cria uma nova transação para um usuário específico.
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
        return validation_error(e)
    except NotFound:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao criar transação: {str(e)}'}), 500


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
  # Deleta um usuário e todas as suas transações associadas.
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'Usuário {user.name} deletado com sucesso'}), 200
    except NotFound:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar usuário: {str(e)}'}), 500


@app.route('/transactions/<int:tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
   # Deleta uma transação específica.
    try:
        transaction = Transaction.query.get_or_404(tx_id)
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': f'Transação "{transaction.title}" deletada com sucesso'}), 200
    except NotFound:
        return jsonify({'error': 'Transação não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar transação: {str(e)}'}), 500

# INICIALIZAÇÃO DO APLICATIVO

if __name__ == '__main__':
    # Cria tabelas do banco de dados se não existirem
    with app.app_context():
        db.create_all()
    
    # Inicia servidor em modo debug
    app.run(debug=True, host='127.0.0.1', port=5000)
    
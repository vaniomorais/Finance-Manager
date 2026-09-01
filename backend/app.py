from flask import Flask, jsonify, request
from flask_cors import CORS
from models.models import db, User, Transaction
from flasgger import Swagger
from pydantic import ValidationError
from schemas import UserCreate, TransactionCreate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
swagger = Swagger(app)
db.init_app(app)

# ROTAS DA API (ENDPOINTS)
@app.route('/users', methods=['GET'])
def get_users():
    """Lista todos os usuários com seus saldos.
    ---
    tags:
      - Usuários
    responses:
      200:
        description: Lista de usuários com saldos
    """
    users = User.query.all()
    users_data = []
    
    for user in users:
        user_dict = user.to_dict()
        # Calcula o saldo do usuário
        income = sum(t.amount for t in user.transactions if t.type == 'income')
        expenses = sum(t.amount for t in user.transactions if t.type == 'expense')
        user_dict['balance'] = income - expenses
        users_data.append(user_dict)
    
    return jsonify(users_data), 200


@app.route('/users', methods=['POST'])
def create_user():
    """Cria um novo usuário.
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
              required: true
            initials:
              type: string
              required: true
            avatar_color:
              type: string
    responses:
      201:
        description: Usuário criado com sucesso
      400:
        description: Erro na validação
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
        error_details = [{'field': err['loc'][0], 'message': err['msg']} for err in e.errors()]
        return jsonify({'error': 'Erro na validação dos dados', 'details': error_details}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/transactions', methods=['GET'])
def get_all_transactions():
    """Retorna todas as transações do grupo familiar com resumo consolidado.
    ---
    tags:
      - Transações
    responses:
      200:
        description: Todas as transações com balanço financeiro do grupo familiar
    """
    all_transactions = Transaction.query.all()
    
    income = sum(t.amount for t in all_transactions if t.type == 'income')
    expenses = sum(t.amount for t in all_transactions if t.type == 'expense')
    balance = income - expenses
    
    transactions_with_member = []
    for t in all_transactions:
        tx_dict = t.to_dict()
        tx_dict['member_name'] = t.user.name
        #tx_dict['member_initials'] = t.user.initials
        #tx_dict['member_color'] = t.user.avatar_color
        transactions_with_member.append(tx_dict)
    
    return jsonify({
        'summary': {
            'income': income,
            'expenses': expenses,
            'balance': balance
        },
        'transactions': transactions_with_member,
        'transaction_count': len(all_transactions)
    }), 200


@app.route('/users/<int:user_id>/transactions', methods=['GET'])
def get_user_transactions(user_id):
    """Retorna as transações e resumo financeiro de um usuário.
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
    """
    user = User.query.get_or_404(user_id)
    
    income = sum(t.amount for t in user.transactions if t.type == 'income')
    expenses = sum(t.amount for t in user.transactions if t.type == 'expense')
    balance = income - expenses
    
    return jsonify({
        'user': user.name,
        'summary': {
            'income': income,
            'expenses': expenses,
            'balance': balance
        },
        'transactions': [t.to_dict() for t in user.transactions]
    }), 200


@app.route('/users/<int:user_id>/transactions', methods=['POST'])
def create_transaction(user_id):
    """Cria uma nova transação para um usuário.
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
            amount:
              type: number
            type:
              type: string
              enum: ['income', 'expense']
            category:
              type: string
            date:
              type: string
              format: date
          required: ['title', 'amount', 'type', 'category']
    responses:
      201:
        description: Transação criada com sucesso
      400:
        description: Erro na validação
      404:
        description: Usuário não encontrado
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
        error_details = [{'field': err['loc'][0], 'message': err['msg']} for err in e.errors()]
        return jsonify({'error': 'Erro na validação dos dados', 'details': error_details}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deleta um usuário e suas transações.
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
    """
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


@app.route('/transactions/<int:tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    """Deleta uma transação de um usuário.
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
    """
    transaction = Transaction.query.get_or_404(tx_id)
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transação deletada com sucesso'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
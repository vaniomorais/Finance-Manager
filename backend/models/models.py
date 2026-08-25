from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

def calculate_balance(transactions):
    """Calcula o saldo total baseado nas transações."""
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    return income - expenses

db = SQLAlchemy()
    
# MODELOS DE BANCO DE DADOS
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    initials = db.Column(db.String(3), nullable=False)
    avatar_color = db.Column(db.String(20), nullable=True)
    
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        balance = calculate_balance(self.transactions)
        
        return {
            'id': self.id,
            'name': self.name,
            'initials': self.initials,
            'avatar_color': self.avatar_color,
            'transaction_count': len(self.transactions),
            'balance': balance
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' ou 'expense'
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'type': self.type,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'user_id': self.user_id
        }

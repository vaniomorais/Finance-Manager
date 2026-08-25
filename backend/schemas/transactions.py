"""Schemas para validação de dados de transações."""

from pydantic import BaseModel, Field, field_validator
import datetime
from typing import Literal


class TransactionCreate(BaseModel):
    """Schema para criação de nova transação."""
    title: str = Field(..., min_length=1, max_length=100, description="Título da transação")
    amount: float = Field(..., gt=0, description="Valor da transação (deve ser maior que zero)")
    type: Literal['income', 'expense'] = Field(..., description="Tipo de transação")
    category: str = Field(..., min_length=1, max_length=50, description="Categoria da transação")
    date: datetime.date = Field(..., description="Data da transação em formato YYYY-MM-DD")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Valida e normaliza o título."""
        if not v or not v.strip():
            raise ValueError('Título não pode estar vazio')
        return v.strip()
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Valida e normaliza a categoria."""
        if not v or not v.strip():
            raise ValueError('Categoria não pode estar vazia')
        return v.strip()
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Valida o valor da transação."""
        if v <= 0:
            raise ValueError('O valor deve ser maior que zero')
        return round(v, 2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Salário",
                "amount": 3000.00,
                "type": "income",
                "category": "Trabalho",
                "date": "2024-08-25"
            }
        }


class TransactionResponse(BaseModel):
    """Schema para resposta de transação."""
    id: int
    title: str
    amount: float
    type: Literal['income', 'expense']
    category: str
    date: str
    user_id: int
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Salário",
                "amount": 3000.00,
                "type": "income",
                "category": "Trabalho",
                "date": "2024-08-25",
                "user_id": 1
            }
        }


class TransactionSummary(BaseModel):
    """Schema para resumo de transações do usuário."""
    income: float
    expenses: float
    balance: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "income": 5000.00,
                "expenses": 2500.00,
                "balance": 2500.00
            }
        }

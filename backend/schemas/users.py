"""Schemas para validação de dados de usuários."""

from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    """Schema para criação de novo usuário."""
    name: str = Field(..., min_length=1, max_length=100, description="Nome do usuário")
    initials: str = Field(..., min_length=1, max_length=3, description="Iniciais do usuário")
    avatar_color: str = Field(default="#81E6D9", max_length=20, description="Cor do avatar em formato hex ou nome")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Valida e normaliza o nome."""
        if not v or not v.strip():
            raise ValueError('Nome não pode estar vazio')
        return v.strip()
    
    @field_validator('initials')
    @classmethod
    def validate_initials(cls, v):
        """Valida e normaliza as iniciais."""
        if not v or not v.strip():
            raise ValueError('Iniciais não podem estar vazias')
        return v.strip().upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "João Silva",
                "initials": "JS",
                "avatar_color": "#81E6D9"
            }
        }


class UserResponse(BaseModel):
    """Schema para resposta de usuário."""
    id: int
    name: str
    initials: str
    avatar_color: str
    transaction_count: int
    balance: float
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "João Silva",
                "initials": "JS",
                "avatar_color": "#81E6D9",
                "transaction_count": 5,
                "balance": 150.00
            }
        }

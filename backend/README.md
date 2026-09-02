# Finance Manager - Backend

API REST para gerenciamento de finanças pessoais e familiares.

## 📋 Sobre

O Finance Manager Backend é uma aplicação desenvolvida em Flask que fornece endpoints para gerenciar usuários, transações financeiras (receitas e despesas) e cálculo de saldos. A API utiliza SQLite para persistência de dados e Swagger para documentação interativa.

## 🎯 Funcionalidades

- ✅ Cadastra um novo usuário/membro da familia.
- ✅ Cadastro de transações (receitas e despesas)
- ✅ Consulta Todos os usuários/membros
- ✅ Consulta todas as transações e balanço financeiro familiar
- ✅ Consulta transações por user ID e seu balanço financeiro
- ✅ Excluir usuários/membros
- ✅ Excluir transações
- ✅ Validação de dados com Pydantic
- ✅ Documentação interativa com Swagger

## 🛠️ Tecnologias

- **Flask** 2.3.3 - Framework web
- **Flask-SQLAlchemy** 3.0.5 - ORM para banco de dados
- **Flask-CORS** 4.0.0 - Suporte a CORS
- **Flasgger** 0.9.7.1 - Documentação Swagger
- **Pydantic** 2.13.4 - Validação de dados
- **SQLite** - Banco de dados

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/vaniomorais/financemanager-backend
cd finance-manager/backend
```

2. **Crie um ambiente virtual** (recomendado)
```bash

python -m venv venv
venv\Scripts\activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

## 🚀 Uso

### Acessar a Documentação Swagger

Abra seu navegador e acesse:
```
http://localhost:5000/apidocs
```

Ali você encontrará toda a documentação interativa dos endpoints e poderá testar cada um deles.

### Endpoints Principais

#### Usuários

- **GET** `/users` - Listar todos os usuários
- **POST** `/users` - Criar novo usuário
- **DELETE** `/users/{user_id}` - Deletar usuário

#### Transações

- **GET** `/transactions` - Listar todas as transações
- **GET** `/transactions` - Listar as transações por ID de usuário
- **POST** `/transactions` - Criar nova transação
- **DELETE** `/transactions/{transaction_id}` - Deletar transação

### Exemplo de Requisição (cURL)

```bash
# Criar um novo usuário
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva"}'

# Listar usuários
curl -X GET http://localhost:5000/users

# Criar uma transação
curl -X POST http://localhost:5000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "type": "income",
    "amount": 1000.00,
    "description": "Salário"
  }'
```

## 📁 Estrutura do Projeto

```
backend/
├── app.py                 # Aplicação principal e rotas
├── requirements.txt       # Dependências do projeto
├── models/
│   └── models.py         # Definição de modelos (User, Transaction)
├── schemas/
│   ├── __init__.py
│   ├── users.py          # Schema de validação de usuários
│   └── transactions.py   # Schema de validação de transações
├── instance/
│   └── finance.db        # Banco de dados SQLite
└── README.md             # Este arquivo
```

## 🔧 Configuração

### Variáveis de Ambiente

Você pode criar um arquivo `.env` para configurar a aplicação:

```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URI=sqlite:///finance.db
```

### Banco de Dados

O banco de dados SQLite é criado automaticamente na primeira execução. Para resetar o banco:

```bash
# Delete o arquivo finance.db na pasta instance/
rm instance/finance.db

# Reinicie a aplicação
python app.py
```

## 👨‍💻 Autor

Desenvolvido como parte do MVP da sprint 01 da da Pós-Graduação em Desenvolvimento Full Stack da PUC Rio.


**Último update:** setembro de 2026

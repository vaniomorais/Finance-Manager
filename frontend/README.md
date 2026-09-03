# Finance Manager - Frontend

Interface web para gerenciamento de finanças pessoais e familiares.

## 📋 Sobre

O Finance Manager Frontend é uma aplicação web desenvolvida em HTML, CSS e JavaScript vanilla, para gerenciamento finaceiro pessoal e/ou familiar. Permite gerenciar membros da família e o controle de gastos de cada um, com o registro das receitas e despesas, apurando a situação financeira (superavit ou deficit) de cada membro bem como do grupo familiar.

## Funcionalidades

- Visualização de membros da família
- Adição e remoção de membros
- Registro de transações (receitas e despesas)
- Visualização de transações por membro
- Cálculo automático de saldos
- Interface intuitiva
- Cards Modais para interações principais
- Validação de dados.

## Tecnologias

- **HTML5** - Estrutura semântica
- **CSS3** - Estilos
- **JavaScript (Vanilla)** - Interatividade
- **Fetch API** - Comunicação com backend

## Instalação

### Pré-requisitos

- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Backend do Finance Manager rodando em `http://localhost:5000`
- Python 3.8+ (para executar o servidor local)

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/vaniomorais/financemanager-frontend
cd finance-manager/frontend
```

2. **Inicie um servidor local** (escolha uma opção)

  **Opção 1: Usando Python (recomendado)**
  ```bash
  python app.py
  ```

  **Opção 2: abrindo o arquivo 'index.html'**

## Como Usar

### 1. Gerenciar Membros
- Na seção "Household Members", clique em "Add Member" para adicionar novos membros da família
- Cada membro possui um saldo que é atualizado automaticamente com as transações
- Remova membros clicando no botão de deletar

### 2. Registrar Transações
- Clique no nome de um membro familiar e em "Add Transaction" para abrir o modal "New Transaction"
- Selecione o tipo (Expense ou Income)
- Insira description, amount, date e select category
- Clique em "Save Transaction" para registrar

### 3. Visualizar Transações
- Clique em "Family Transactions" para ver todas as transações do grupo familiar
- Clique no nome de um membro para ver suas transações individuais
- As transações são exibidas com data, tipo, valor e descrição

### 4. Consultar Documentação da API
- Acesse diretamente
- URL: `http://localhost:5000/apidocs`

## Estrutura do Projeto

```
frontend/
├── index.html          # Página principal
├── styles.css          # Estilos da aplicação
├── script.js           # Lógica e interatividade
└── README.md           # Este arquivo
```

Todos os estilos podem ser personalizados no arquivo `styles.css`. As cores principais são definidas no início do arquivo como variáveis CSS:

```css
:root {
  --primary-color: #6366f1;
  --secondary-color: #ec4899;
  /* ... outras cores */
}
```

## Integração com Backend

O frontend se comunica com o backend através da API REST. Certifique-se de que:

1. O backend está rodando em `http://localhost:5000`
2. CORS está habilitado no backend (já configurado por padrão)
3. O banco de dados do backend contém os dados

## Testes Manuais

### Fluxo Básico de Teste

1. Abra a aplicação
2. Clique em "Add Member" e crie um novo membro
3. Clique em "New Transaction" e registre uma receita
4. Clique em "New Transaction" e registre uma despesa
5. Verifique se o saldo foi atualizado corretamente
6. Abra "Family Transactions" para visualizar as transações de todos os membros familiares

## Troubleshooting

### Problema: "Erro ao conectar com a API"

**Solução:**
1. Verifique se o backend está rodando em `http://localhost:5000`
2. Verifique se CORS está habilitado
3. Abra o console do navegador (F12) para ver mensagens de erro
4. Verifique se a URL da API está correta no arquivo `script.js`

### Problema: "Dados não aparecem"

**Solução:**
1. Verifique se o backend tem dados no banco de dados
2. Atualize a página (F5)
3. Limpe o cache do navegador (Ctrl+Shift+Delete)
4. Verifique as requisições de rede no Developer Tools (F12 > Network)

## Autor

Desenvolvido como parte do MVP da sprint 01 da Pós-Graduação em Desenvolvimento Full Stack.

**Último update:** setembro de 2026

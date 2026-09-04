// Configuração da URL da API (localhost)
let API_URL = 'http://127.0.0.1:5000';


// CONSTANTES

const BALANCE_CLASSES = {
    positive: 'balance-positive',
    negative: 'balance-negative'
};

const TRANSACTION_TYPES = {
    income: 'income',
    expense: 'expense'
};

const ICONS = {
    income: '↙',
    expense: '↗'
};

const COLORS = {
    teal: '#81E6D9',
    pink: '#F8A5A5',
    purple: '#D8A8E8',
    blue: '#63B3ED',
    yellow: '#F5D76E',
    green: '#A8ECC8'
};

const COLOR_ARRAY = Object.values(COLORS);


// ESTADO GLOBAL

const state = {
    activeUserId: null,
    activeUserInitials: '',
    activeUserColor: '',
    selectedColor: null,
    deleteItem: {
        id: null,
        isTransaction: false
    }
};

// INICIALIZAÇÃO

document.addEventListener("DOMContentLoaded", async () => {
    fetchUsers();
});

// FUNÇÕES AUXILIARES - FORMATAÇÃO E CONVERSÃO

// CSS para estilizar saldo (positivo/negativo)
function getBalanceClass(balance) {
    return balance >= 0 ? BALANCE_CLASSES.positive : BALANCE_CLASSES.negative;
}

// Exibição sinal (+ ou -)
function getBalancePrefix(balance) {
    return balance >= 0 ? '+' : '';
}


// Prefixo para transação baseado no tipo
function getTransactionPrefix(type) {
    return type === TRANSACTION_TYPES.income ? '+' : '-';
}

// Ícone visual para o tipo de transação
function getTransactionIcon(type) {
    return ICONS[type] || ICONS.expense;
}

// CSS do ícone para o tipo de transação
function getTransactionIconClass(type) {
    return type === TRANSACTION_TYPES.income ? 'icon-income' : 'icon-expense';
}

// Formata valor em moeda para 2 casas decimais
function formatCurrency(value) {
    return Math.abs(value).toFixed(2);
}


// Gera as iniciais do nome (usado para avatar)
function generateInitials(name) {
    const parts = name.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}


// Data atual
function getTodayDate() {
    return new Date().toISOString().split('T')[0];
}

// FUNÇÕES AUXILIARES - INTERFACE E MODAIS

// Alterna visibilidade de um modal
function setModalDisplay(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = show ? 'flex' : 'none';
    }
}


// Atualiza e exibe modal de erro
function showErrorModal(message) {
    document.getElementById('error-message').innerText = message;
    setModalDisplay('error-modal', true);
}

// Fecha modal de erro
function closeErrorModal() {
    setModalDisplay('error-modal', false);
}


// Atualiza summary box (renda, despesas, saldo)
function updateSummaryBox(summaryData, balanceElementId, incomeElementId, expenseElementId, containerSelector) {
    const balanceEl = document.getElementById(balanceElementId);
    const incomeEl = document.getElementById(incomeElementId);
    const expenseEl = document.getElementById(expenseElementId);
    
    if (incomeEl) incomeEl.innerText = `+$${formatCurrency(summaryData.income)}`;
    if (expenseEl) expenseEl.innerText = `-$${formatCurrency(summaryData.expenses)}`;
    
    if (balanceEl) {
        const balanceClass = getBalanceClass(summaryData.balance);
        const balancePrefix = getBalancePrefix(summaryData.balance);
        balanceEl.innerText = `${balancePrefix}$${formatCurrency(summaryData.balance)}`;
        balanceEl.className = balanceClass;
    }
    
    const balanceBox = document.querySelector(containerSelector);
    if (balanceBox) {
        balanceBox.classList.remove('balance-positive-bg', 'balance-negative-bg');
        if (summaryData.balance >= 0) {
            balanceBox.classList.add('balance-positive-bg');
        } else {
            balanceBox.classList.add('balance-negative-bg');
        }
    }
}

// GERENCIAMENTO DE USUÁRIOS

//Busca lista de usuários da API
async function fetchUsers() {
    try {
        const response = await fetch(`${API_URL}/users`);
        if (!response.ok) throw new Error('Falha ao buscar usuários');
        
        const users = await response.json();
        updateUserList(users);
    } catch (error) {
        console.error("Erro ao buscar usuários:", error);
        showErrorModal('Error loading members. Check your connection.');
    }
}

// Atualiza a lista de usuários na interface
function updateUserList(users) {
    document.getElementById('member-count').innerText = `${users.length} members registered`;
    const container = document.getElementById('users-container');
    container.innerHTML = '';
    
    users.forEach(user => {
        const row = createUserRow(user);
        container.appendChild(row);
    });
}

// Cria as linhas da lista de usuários
function createUserRow(user) {
    const row = document.createElement('div');
    row.className = 'user-row';
    row.onclick = () => openUserModal(user.id, user.initials, user.avatar_color);
    
    const balanceClass = getBalanceClass(user.balance);
    const balancePrefix = getBalancePrefix(user.balance);
    const balanceLabel = user.balance >= 0 ? 'SURPLUS' : 'DEFICIT';
    
    row.innerHTML = `
        <div class="avatar" style="background-color: ${user.avatar_color};">${user.initials}</div>
        <div class="user-info">
            <p class="user-name">${user.name}</p>
            <p class="user-meta">${user.transaction_count} transactions</p>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div class="user-balance">
                <span class="${balanceClass}">${balancePrefix}$${formatCurrency(user.balance)}</span>
                <p class="user-meta" style="font-size: 0.65rem;">${balanceLabel}</p>
            </div>
            <div class="action-icons">
                <span class="icon-btn">❯</span>
                <span class="icon-btn icon-delete" onclick="openDeleteModal(event, '${user.name}', null, ${user.id}, false)">🗑️</span>
            </div>
        </div>
    `;
    
    return row;
}

// GERENCIAMENTO DE TRANSAÇÕES - MODAL DO USUÁRIO

// Abre modal com dados e transações de um usuário específico
async function openUserModal(userId, initials, avatarColor) {
    state.activeUserId = userId;
    state.activeUserInitials = initials;
    state.activeUserColor = avatarColor;
    
    try {
        const response = await fetch(`${API_URL}/users/${userId}/transactions`);
        if (!response.ok) throw new Error('Falha ao buscar transações');
        
        const data = await response.json();
        updateUserTransactionModal(data, initials, avatarColor);
        setModalDisplay('transaction-modal', true);
    } catch (error) {
        console.error("Erro ao abrir modal:", error);
        showErrorModal('Error loading transactions.');
    }
}

// Atualiza conteúdo do modal de transações do usuário
function updateUserTransactionModal(data, initials, avatarColor) {
    // Atualiza cabeçalho
    document.getElementById('modal-avatar').innerText = initials;
    document.getElementById('modal-avatar').style.backgroundColor = avatarColor;
    document.getElementById('modal-user-name').innerText = data.user;
    document.getElementById('modal-tx-count').innerText = `${data.transactions.length} transactions`;
    
    // Atualiza summary box (renda, despesas, saldo) com IDs específicos do modal do usuário
    updateSummaryBox(data.summary, 'modal-balance', 'modal-income', 'modal-expenses', '.summary-box-balance');
    
    // Atualiza lista de transações
    updateTransactionListUI(data.transactions, 'modal-tx-list', false);
}

// Fecha modal de transações do usuário
function closeModal() {
    setModalDisplay('transaction-modal', false);
    // Atualiza a lista de usuários ao fechar
    fetchUsers();
}

// GERENCIAMENTO DE TRANSAÇÕES - TODAS AS TRANSAÇÕES

// Abre modal com a lista de todas as transações de todos os usuários
async function openAllTransactionsModal() {
    try {
        const response = await fetch(`${API_URL}/transactions`);
        if (!response.ok) throw new Error('Falha ao buscar transações');
        
        const data = await response.json();
        updateAllTransactionsModal(data);
        setModalDisplay('all-transactions-modal', true);
    } catch (error) {
        console.error("Erro ao abrir modal de todas as transações:", error);
        showErrorModal('Error loading family transactions.');
    }
}

// Fecha modal de todas as transações
function closeAllTransactionsModal() {
    setModalDisplay('all-transactions-modal', false);
}

// Atualiza conteúdo do modal com todas as transações
function updateAllTransactionsModal(data) {
    // Atualiza contagem de transações
    document.getElementById('all-tx-count').innerText = `${data.transaction_count} transactions`;
    
    // Atualiza summary box (renda, despesas, saldo) com IDs específicos do modal de todas as transações
    updateSummaryBox(data.summary, 'all-modal-balance', 'all-modal-income', 'all-modal-expenses', '#all-transactions-modal .summary-box-balance');
    
    // Atualiza lista de transações
    updateTransactionListUI(data.transactions, 'all-tx-list', true);
}

// FUNÇÕES AUXILIARES DE TRANSAÇÕES

function updateTransactionListUI(transactions, containerId, showMemberName = false) {
    const txContainer = document.getElementById(containerId);
    txContainer.innerHTML = '';
    
    transactions.forEach(tx => {
        const row = createTransactionRowElement(tx, showMemberName);
        txContainer.appendChild(row);
    });
}


// Cria linhas da lista de transações
function createTransactionRowElement(tx, showMemberName = false) {
    const isIncome = tx.type === TRANSACTION_TYPES.income;
    const iconClass = getTransactionIconClass(tx.type);
    const iconSymbol = getTransactionIcon(tx.type);
    const amountClass = getBalanceClass(isIncome ? 1 : -1);
    const amountPrefix = getTransactionPrefix(tx.type);
    
    const row = document.createElement('div');
    row.className = 'tx-row';
    
    const metadata = showMemberName 
        ? `${tx.member_name} • ${tx.category} • ${tx.date}`
        : `${tx.category} • ${tx.date}`;
    
    row.innerHTML = `
        <div class="tx-icon ${iconClass}">${iconSymbol}</div>
        <div class="user-info">
            <p class="user-name">${tx.title}</p>
            <p class="user-meta">${metadata}</p>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <span class="${amountClass}" style="font-weight:bold;">${amountPrefix}$${formatCurrency(tx.amount)}</span>
            ${showMemberName ? '' : `<div class="action-icons">
                <span class="icon-btn icon-delete" onclick="openDeleteModal(event, '${tx.title}', '${amountPrefix}$${formatCurrency(tx.amount)}', ${tx.id}, true)">🗑️</span>
            </div>`}
        </div>
    `;
    
    return row;
}

// GERENCIAMENTO DE EXCLUSÃO

// Abre modal de confirmação para deletar usuário ou transação
function openDeleteModal(event, itemName, itemValue, itemId, isTransaction) {
    event.stopPropagation();
    
    state.deleteItem.id = itemId;
    state.deleteItem.isTransaction = isTransaction;
    
    const itemType = isTransaction ? 'Transaction' : 'Member';
    
    document.getElementById('delete-item-type').innerText = itemType;
    document.getElementById('delete-item-name').innerText = itemName;
    
    const valueSpan = document.getElementById('delete-item-value');
    valueSpan.innerText = itemValue ? ` (${itemValue})` : '';
    
    setModalDisplay('delete-confirmation-modal', true);
}

// Fecha modal de exclusão
function closeDeleteModal() {
    setModalDisplay('delete-confirmation-modal', false);
}

// Confirmação da deleção de usuário ou transação
async function confirmDelete() {
    const { id, isTransaction } = state.deleteItem;
    
    if (!id) return;
    
    try {
        const endpoint = isTransaction 
            ? `${API_URL}/transactions/${id}`
            : `${API_URL}/users/${id}`;
        
        const response = await fetch(endpoint, { method: 'DELETE' });
        
        if (!response.ok) throw new Error('Falha ao deletar');
        
        closeDeleteModal();
        
        if (isTransaction) {
            // Atualiza o modal do usuário
            openUserModal(state.activeUserId, state.activeUserInitials, state.activeUserColor);
        } else {
            // Atualiza a lista principal
            fetchUsers();
        }
    } catch (error) {
        console.error('Erro ao excluir:', error);
        showErrorModal('Error deleting item.');
    }
}

// INCLUSÃO DE NOVOS USUÁRIOS

// Abre modal para adicionar novo usuário
function openAddMemberModal() {
    document.getElementById('new-member-name').value = '';
    state.selectedColor = COLOR_ARRAY[0]; // Seleciona a primeira cor como padrão
    highlightSelectedColor(COLOR_ARRAY[0]);
    setModalDisplay('add-member-modal', true);
}

// Fecha modal de adição de usuário
function closeAddMemberModal() {
    setModalDisplay('add-member-modal', false);
}

// Envia novo usuário para a API
async function submitNewMember() {
    const nameInput = document.getElementById('new-member-name').value.trim();
    
    if (!nameInput) {
        showErrorModal("Please enter the member's name.");
        return;
    }

    if (!state.selectedColor) {
        showErrorModal("Please select a color for the avatar.");
        return;
    }

    const initials = generateInitials(nameInput);

    try {
        const response = await fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: nameInput,
                initials: initials,
                avatar_color: state.selectedColor
            })
        });

        if (response.ok) {
            closeAddMemberModal();
            fetchUsers();
        } else {
            showErrorModal("Error adding member.");
        }
    } catch (error) {
        console.error("Error:", error);
        showErrorModal("Error connecting to the server.");
    }
}

// Define a cor selecionada
function selectColor(color) {
    state.selectedColor = color;
    highlightSelectedColor(color);
}

// Destaca a cor selecionada
function highlightSelectedColor(color) {
    const colorButtons = document.querySelectorAll('.color-option');
    colorButtons.forEach(btn => {
        if (btn.style.backgroundColor === color || btn.getAttribute('data-color') === color) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    });
}

// INCLUSÃO DE TRANSAÇÕES

// Abre modal adicionar nova transação
function openAddTxModal() {
    document.getElementById('new-tx-title').value = '';
    document.getElementById('new-tx-amount').value = '';
    document.getElementById('new-tx-category').value = '';
    document.getElementById('new-tx-type').value = TRANSACTION_TYPES.expense;
    document.getElementById('new-tx-date').value = getTodayDate();
    
    // Botão expense selecionado por padrão
    selectTransactionType('expense');
    
    setModalDisplay('add-tx-modal', true);
}

// Fecha modal de adiçionar transação
function closeAddTxModal() {
    setModalDisplay('add-tx-modal', false);
}

// Define tipo de transação selecionado
function selectTransactionType(type) {
    document.getElementById('new-tx-type').value = type;
    
    const expenseBtn = document.getElementById('tx-type-expense-btn');
    const incomeBtn = document.getElementById('tx-type-income-btn');
    
    if (type === 'expense') {
        expenseBtn.classList.add('active');
        incomeBtn.classList.remove('active');
    } else {
        incomeBtn.classList.add('active');
        expenseBtn.classList.remove('active');
    }
}

// Envia nova transação para a API
async function submitNewTransaction() {
    const title = document.getElementById('new-tx-title').value.trim();
    const amount = document.getElementById('new-tx-amount').value;
    const type = document.getElementById('new-tx-type').value;
    const category = document.getElementById('new-tx-category').value.trim();
    const date = document.getElementById('new-tx-date').value;
    
    if (!title || !amount || !category || !date) {
        showErrorModal("Please fill in all fields.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/users/${state.activeUserId}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                amount: parseFloat(amount),
                type,
                category,
                date
            })
        });

        if (response.ok) {
            closeAddTxModal();
            // Atualiza a tela principal e o modal do usuário
            await fetchUsers();
            openUserModal(state.activeUserId, state.activeUserInitials, state.activeUserColor);
        } else {
            showErrorModal("Error adding transaction.");
        }
    } catch (error) {
        console.error("Erro:", error);
        showErrorModal("Error connecting to the server.");
    }
}
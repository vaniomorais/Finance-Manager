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

document.addEventListener("DOMContentLoaded", async () => {
    fetchUsers();
});

// FUNÇÕES HELPER

function getBalanceClass(balance) {
    return balance >= 0 ? BALANCE_CLASSES.positive : BALANCE_CLASSES.negative;
}

function getBalancePrefix(balance) {
    return balance >= 0 ? '+' : '';
}

function getTransactionPrefix(type) {
    return type === TRANSACTION_TYPES.income ? '+' : '-';
}

function getTransactionIcon(type) {
    return ICONS[type] || ICONS.expense;
}

function getTransactionIconClass(type) {
    return type === TRANSACTION_TYPES.income ? 'icon-income' : 'icon-expense';
}

function formatCurrency(value) {
    return Math.abs(value).toFixed(2);
}

function setModalDisplay(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = show ? 'flex' : 'none';
    }
}

// GERENCIAMENTO DE MODAIS E ERROS

function showErrorModal(message) {
    document.getElementById('error-message').innerText = message;
    setModalDisplay('error-modal', true);
}

function closeErrorModal() {
    setModalDisplay('error-modal', false);
}

// GERENCIAMENTO DE USUÁRIOS

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

function updateUserList(users) {
    document.getElementById('member-count').innerText = `${users.length} members registered`;
    const container = document.getElementById('users-container');
    container.innerHTML = '';
    
    users.forEach(user => {
        const row = createUserRow(user);
        container.appendChild(row);
    });
}

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

async function openUserModal(userId, initials, avatarColor) {
    state.activeUserId = userId;
    state.activeUserInitials = initials;
    state.activeUserColor = avatarColor;
    
    try {
        const response = await fetch(`${API_URL}/users/${userId}/transactions`);
        if (!response.ok) throw new Error('Falha ao buscar transações');
        
        const data = await response.json();
        updateTransactionModal(data, initials, avatarColor);
        setModalDisplay('transaction-modal', true);
    } catch (error) {
        console.error("Erro ao abrir modal:", error);
        showErrorModal('Error loading transactions.');
    }
}

function updateTransactionModal(data, initials, avatarColor) {
    // Atualiza cabeçalho
    document.getElementById('modal-avatar').innerText = initials;
    document.getElementById('modal-avatar').style.backgroundColor = avatarColor;
    document.getElementById('modal-user-name').innerText = data.user;
    document.getElementById('modal-tx-count').innerText = `${data.transactions.length} transactions`;
    
    // Atualiza summary boxes
    document.getElementById('modal-income').innerText = `+$${formatCurrency(data.summary.income)}`;
    document.getElementById('modal-expenses').innerText = `-$${formatCurrency(data.summary.expenses)}`;
    
    const balanceEl = document.getElementById('modal-balance');
    const balanceClass = getBalanceClass(data.summary.balance);
    const balancePrefix = getBalancePrefix(data.summary.balance);
    balanceEl.innerText = `${balancePrefix}$${formatCurrency(data.summary.balance)}`;
    balanceEl.className = balanceClass;
    
    // Atualiza cor de fundo do balance box
    const balanceBox = document.querySelector('.summary-box-balance');
    balanceBox.classList.remove('balance-positive-bg', 'balance-negative-bg');
    if (data.summary.balance >= 0) {
        balanceBox.classList.add('balance-positive-bg');
    } else {
        balanceBox.classList.add('balance-negative-bg');
    }
    
    // Atualiza lista de transações
    updateTransactionList(data.transactions);
}

function updateTransactionList(transactions) {
    const txContainer = document.getElementById('modal-tx-list');
    txContainer.innerHTML = '';
    
    transactions.forEach(tx => {
        const row = createTransactionRow(tx);
        txContainer.appendChild(row);
    });
}

function createTransactionRow(tx) {
    const isIncome = tx.type === TRANSACTION_TYPES.income;
    const iconClass = getTransactionIconClass(tx.type);
    const iconSymbol = getTransactionIcon(tx.type);
    const amountClass = getBalanceClass(isIncome ? 1 : -1);
    const amountPrefix = getTransactionPrefix(tx.type);
    
    const row = document.createElement('div');
    row.className = 'tx-row';
    row.innerHTML = `
        <div class="tx-icon ${iconClass}">${iconSymbol}</div>
        <div class="user-info">
            <p class="user-name">${tx.title}</p>
            <p class="user-meta">${tx.category} • ${tx.date}</p>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <span class="${amountClass}" style="font-weight:bold;">${amountPrefix}$${formatCurrency(tx.amount)}</span>
            <div class="action-icons">
                <span class="icon-btn icon-delete" onclick="openDeleteModal(event, '${tx.title}', '${amountPrefix}$${formatCurrency(tx.amount)}', ${tx.id}, true)">🗑️</span>
            </div>
        </div>
    `;
    
    return row;
}

function closeModal() {
    setModalDisplay('transaction-modal', false);
    // Atualiza a lista de usuários para refletir mudanças de saldo
    fetchUsers();
}


// GERENCIAMENTO DE EXCLUSÃO

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

function closeDeleteModal() {
    setModalDisplay('delete-confirmation-modal', false);
}

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


// GERENCIAMENTO DE MEMBROS

function openAddMemberModal() {
    document.getElementById('new-member-name').value = '';
    state.selectedColor = COLOR_ARRAY[0]; // Seleciona a primeira cor como padrão
    highlightSelectedColor(COLOR_ARRAY[0]);
    setModalDisplay('add-member-modal', true);
}

function closeAddMemberModal() {
    setModalDisplay('add-member-modal', false);
}

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

function selectColor(color) {
    state.selectedColor = color;
    highlightSelectedColor(color);
}

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

function generateInitials(name) {
    const parts = name.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}

// GERENCIAMENTO DE TRANSAÇÕES

function openAddTxModal() {
    document.getElementById('new-tx-title').value = '';
    document.getElementById('new-tx-amount').value = '';
    document.getElementById('new-tx-category').value = '';
    document.getElementById('new-tx-type').value = TRANSACTION_TYPES.expense;
    document.getElementById('new-tx-date').value = getTodayDate();
    
    // Reset type buttons to expense
    selectTransactionType('expense');
    
    setModalDisplay('add-tx-modal', true);
}

function closeAddTxModal() {
    setModalDisplay('add-tx-modal', false);
}

function getTodayDate() {
    return new Date().toISOString().split('T')[0];
}

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
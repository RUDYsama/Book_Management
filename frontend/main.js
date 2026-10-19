// Lab 9.6 & 9.7: Environment Variable
const API_URL = import.meta.env.VITE_API_URL || 'https://bookstore-api-39ko.onrender.com';
document.getElementById('backendUrlDisplay').innerText = API_URL;

let currentUser = null;
let accessToken = localStorage.getItem('access_token') || null;

window.quickFill = (email, pwd) => {
  document.getElementById('emailInput').value = email;
  document.getElementById('passwordInput').value = pwd;
};

window.handleLogin = async (e) => {
  e.preventDefault();
  const alertEl = document.getElementById('loginAlert');
  alertEl.classList.add('d-none');

  const email = document.getElementById('emailInput').value;
  const password = document.getElementById('passwordInput').value;

  try {
    const res = await fetch(`${API_URL}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (!res.ok) {
      alertEl.innerText = data.message || 'Login failed';
      alertEl.classList.remove('d-none');
      return;
    }

    accessToken = data.access;
    currentUser = data.user;
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('current_user', JSON.stringify(currentUser));

    renderAuthenticatedView();
    loadBooks();
  } catch (err) {
    alertEl.innerText = 'Network error: ' + err.message;
    alertEl.classList.remove('d-none');
  }
};

window.logout = () => {
  accessToken = null;
  currentUser = null;
  localStorage.removeItem('access_token');
  localStorage.removeItem('current_user');
  document.getElementById('loginSection').classList.remove('d-none');
  document.getElementById('mainSection').classList.add('d-none');
  document.getElementById('userBadge').classList.add('d-none');
  document.getElementById('logoutBtn').classList.add('d-none');
};

function renderAuthenticatedView() {
  document.getElementById('loginSection').classList.add('d-none');
  document.getElementById('mainSection').classList.remove('d-none');

  const badge = document.getElementById('userBadge');
  const roleColors = {
    admin: 'bg-danger',
    editor: 'bg-primary',
    manager: 'bg-warning text-dark',
    viewer: 'bg-secondary'
  };
  const color = roleColors[currentUser.role] || 'bg-secondary';
  badge.innerHTML = `<span class="badge ${color} badge-role">${currentUser.name} (${currentUser.role})</span>`;
  badge.classList.remove('d-none');
  document.getElementById('logoutBtn').classList.remove('d-none');
}

async function loadBooks() {
  const tbody = document.getElementById('booksTableBody');
  try {
    const res = await fetch(`${API_URL}/api/books/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const books = await res.json();
    if (!books || books.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">ไม่พบข้อมูลหนังสือ</td></tr>';
      return;
    }

    tbody.innerHTML = books.map(b => `
      <tr>
        <td class="fw-bold">${b.id}</td>
        <td>${b.title}</td>
        <td>${b.author}</td>
        <td><span class="badge bg-light text-dark border">${b.category}</span></td>
        <td>฿${parseFloat(b.price).toFixed(2)}</td>
        <td>${b.stock}</td>
        <td class="text-end">
          <button class="btn btn-outline-danger btn-sm" onclick="handleDeleteBook(${b.id})">
            <i class="bi bi-trash"></i> ลบ (Admin)
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">เกิดข้อผิดพลาด: ${err.message}</td></tr>`;
  }
}

window.handleDeleteBook = async (id) => {
  if (!confirm(`ต้องการลบหนังสือ ID: ${id} หรือไม่? (ทดสอบ RBAC)`)) return;

  const actionAlert = document.getElementById('actionAlert');
  actionAlert.className = 'alert d-none';

  try {
    const res = await fetch(`${API_URL}/api/books/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (res.status === 204 || res.status === 200) {
      actionAlert.className = 'alert alert-success';
      actionAlert.innerText = `ลบหนังสือ ID ${id} สำเร็จ! (คุณเป็น Admin)`;
      loadBooks();
    } else if (res.status === 403) {
      actionAlert.className = 'alert alert-danger';
      actionAlert.innerText = `403 Forbidden: สิทธิ์ของคุณ (${currentUser.role}) ไม่มีสิทธิ์ลบหนังสือ! เฉพาะ Admin เท่านั้น`;
    } else if (res.status === 401) {
      actionAlert.className = 'alert alert-warning';
      actionAlert.innerText = '401 Unauthorized: Session หมดอายุ กรุณาเข้าสู่ระบบใหม่';
      logout();
    } else {
      const data = await res.json().catch(() => ({}));
      actionAlert.className = 'alert alert-danger';
      actionAlert.innerText = `Error (${res.status}): ${data.message || 'ลบไม่สำเร็จ'}`;
    }
  } catch (err) {
    actionAlert.className = 'alert alert-danger';
    actionAlert.innerText = 'Network error: ' + err.message;
  }
};

window.handleAddBook = async (e) => {
  e.preventDefault();
  const title = document.getElementById('newTitle').value;
  const author = document.getElementById('newAuthor').value;
  const price = parseFloat(document.getElementById('newPrice').value);
  const stock = parseInt(document.getElementById('newStock').value);
  const category = document.getElementById('newCategory').value;

  const actionAlert = document.getElementById('actionAlert');
  actionAlert.className = 'alert d-none';

  try {
    const res = await fetch(`${API_URL}/api/books/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ title, author, price, stock, category })
    });

    const modal = bootstrap.Modal.getInstance(document.getElementById('addBookModal'));
    if (modal) modal.hide();

    if (res.status === 201) {
      actionAlert.className = 'alert alert-success';
      actionAlert.innerText = `เพิ่มหนังสือ "${title}" สำเร็จ!`;
      document.getElementById('addBookForm').reset();
      loadBooks();
    } else if (res.status === 403) {
      actionAlert.className = 'alert alert-danger';
      actionAlert.innerText = `403 Forbidden: บทบาท (${currentUser.role}) ไม่มีสิทธิ์เพิ่มหนังสือ!`;
    } else {
      const data = await res.json().catch(() => ({}));
      actionAlert.className = 'alert alert-danger';
      actionAlert.innerText = `Error (${res.status}): ${data.message || 'บันทึกไม่สำเร็จ'}`;
    }
  } catch (err) {
    actionAlert.className = 'alert alert-danger';
    actionAlert.innerText = 'Network error: ' + err.message;
  }
};

// Auto restore session if available
const savedUser = localStorage.getItem('current_user');
if (accessToken && savedUser) {
  try {
    currentUser = JSON.parse(savedUser);
    renderAuthenticatedView();
    loadBooks();
  } catch (e) {
    logout();
  }
}

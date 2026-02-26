/**
 * admin.js — Admin Panel SPA Logic
 * Handles all admin panel interactions: login, CRUD, UI asset editing.
 */
(function () {
    'use strict';

    // ─── State ─────────────────────────────────────────────────────────────
    let currentAdminSection = 'dashboard';
    let csrfToken = null;

    // ─── Init ───────────────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        fetchCsrfToken();
    });

    async function fetchCsrfToken() {
        try {
            const res = await fetch('/auth/csrf-token');
            const data = await res.json();
            csrfToken = data.csrf_token;
        } catch (e) {
            console.warn('[Admin] Could not fetch CSRF token');
        }
    }

    // ─── API Helper ─────────────────────────────────────────────────────────
    window.adminApi = {
        async request(method, url, body = null) {
            const opts = {
                method,
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
            };
            if (body) {
                if (csrfToken) body.csrf_token = csrfToken;
                opts.body = JSON.stringify(body);
            }
            const res = await fetch(url, opts);
            const data = await res.json();
            if (!res.ok) throw new Error(data.message || 'Request failed');
            return data;
        },
        get: (url) => window.adminApi.request('GET', url),
        post: (url, body) => window.adminApi.request('POST', url, body),
        put: (url, body) => window.adminApi.request('PUT', url, body),
        delete: (url) => window.adminApi.request('DELETE', url, {}),
    };

    // ─── Admin Login ────────────────────────────────────────────────────────
    window.adminLogin = async function () {
        const username = document.getElementById('admin-username')?.value?.trim();
        const password = document.getElementById('admin-password')?.value;
        const errEl = document.getElementById('admin-login-error');
        const btn = document.getElementById('admin-login-btn');

        if (!username || !password) {
            if (errEl) errEl.textContent = 'Please enter username and password.';
            return;
        }

        if (btn) { btn.disabled = true; btn.textContent = 'Signing in...'; }
        if (errEl) errEl.textContent = '';

        try {
            const data = await adminApi.post('/auth/admin-login', { username, password });
            if (data.success) {
                window.switchPage('admin');
                loadAdminDashboard();
            }
        } catch (e) {
            if (errEl) errEl.textContent = e.message;
        } finally {
            if (btn) { btn.disabled = false; btn.textContent = 'Sign In'; }
        }
    };

    // ─── Dashboard ──────────────────────────────────────────────────────────
    window.loadAdminDashboard = async function () {
        try {
            const data = await adminApi.get('/admin/stats');
            const s = data.stats;
            const fill = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
            fill('stat-products', s.products);
            fill('stat-categories', s.categories);
            fill('stat-orders', s.orders);
            fill('stat-users', s.users);
            fill('stat-banners', s.banners);
            fill('stat-ui-assets', s.ui_assets);
        } catch (e) {
            console.warn('[Admin] Could not load stats:', e.message);
        }
    };

    // ─── Section Navigation ──────────────────────────────────────────────────
    window.showAdminSection = function (section) {
        currentAdminSection = section;
        document.querySelectorAll('.admin-section').forEach(el => el.classList.remove('active'));
        const target = document.getElementById('admin-section-' + section);
        if (target) target.classList.add('active');

        document.querySelectorAll('.admin-nav-item').forEach(el => {
            el.classList.toggle('active', el.dataset.section === section);
        });

        if (section === 'dashboard') loadAdminDashboard();
        if (section === 'products') loadAdminProducts();
        if (section === 'categories') loadAdminCategories();
        if (section === 'banners') loadAdminBanners();
        if (section === 'ui-assets') loadAdminUIAssets();
        if (section === 'orders') loadAdminOrders();
    };

    // ─── Products ────────────────────────────────────────────────────────────
    window.loadAdminProducts = async function () {
        const container = document.getElementById('admin-products-table-body');
        if (!container) return;
        container.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#6B7280;">Loading...</td></tr>';
        try {
            const data = await adminApi.get('/admin/products');
            if (!data.products.length) {
                container.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#6B7280;">No products yet.</td></tr>';
                return;
            }
            container.innerHTML = data.products.map(p => `
                <tr>
                    <td><img src="${p.image || 'https://via.placeholder.com/48'}" width="48" height="48" style="border-radius:8px;object-fit:cover;" onerror="this.src='https://via.placeholder.com/48'"></td>
                    <td style="font-weight:500;max-width:200px;">${p.name}</td>
                    <td>$${p.price.toFixed(2)}</td>
                    <td>${p.stock ?? '-'}</td>
                    <td><span class="admin-tag ${p.tag || ''}">${p.tag || 'none'}</span></td>
                    <td>★ ${p.rating}</td>
                    <td>
                        <button class="admin-btn admin-btn-sm" onclick="editProduct(${p.id})">Edit</button>
                        <button class="admin-btn admin-btn-sm admin-btn-danger" onclick="deleteProduct(${p.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            container.innerHTML = `<tr><td colspan="7" style="color:red;padding:20px;">${e.message}</td></tr>`;
        }
    };

    window.deleteProduct = async function (id) {
        if (!confirm('Delete this product?')) return;
        try {
            await adminApi.delete(`/admin/products/${id}`);
            showAdminToast('Product deleted');
            loadAdminProducts();
        } catch (e) {
            showAdminToast(e.message, true);
        }
    };

    window.showProductModal = function (product = null) {
        const modal = document.getElementById('product-modal');
        if (!modal) return;
        document.getElementById('pm-id').value = product?.id || '';
        document.getElementById('pm-name').value = product?.name || '';
        document.getElementById('pm-description').value = product?.description || '';
        document.getElementById('pm-price').value = product?.price || '';
        document.getElementById('pm-old-price').value = product?.old_price || '';
        document.getElementById('pm-stock').value = product?.stock ?? 10;
        document.getElementById('pm-brand').value = product?.brand || '';
        document.getElementById('pm-image').value = product?.image || '';
        document.getElementById('pm-tag').value = product?.tag || '';
        document.getElementById('pm-featured').checked = product?.is_featured || false;
        modal.classList.add('active');
    };

    window.editProduct = async function (id) {
        try {
            const data = await adminApi.get(`/api/products/${id}`);
            showProductModal(data.product);
        } catch (e) {
            showAdminToast(e.message, true);
        }
    };

    window.saveProduct = async function () {
        const id = document.getElementById('pm-id').value;
        const body = {
            name: document.getElementById('pm-name').value,
            description: document.getElementById('pm-description').value,
            price: parseFloat(document.getElementById('pm-price').value),
            old_price: parseFloat(document.getElementById('pm-old-price').value) || null,
            stock: parseInt(document.getElementById('pm-stock').value),
            brand: document.getElementById('pm-brand').value,
            image: document.getElementById('pm-image').value,
            tag: document.getElementById('pm-tag').value,
            is_featured: document.getElementById('pm-featured').checked,
        };
        try {
            if (id) {
                await adminApi.put(`/admin/products/${id}`, body);
                showAdminToast('Product updated');
            } else {
                await adminApi.post('/admin/products', body);
                showAdminToast('Product created');
            }
            document.getElementById('product-modal')?.classList.remove('active');
            loadAdminProducts();
        } catch (e) {
            showAdminToast(e.message, true);
        }
    };

    // ─── Categories ───────────────────────────────────────────────────────────
    window.loadAdminCategories = async function () {
        const container = document.getElementById('admin-categories-grid');
        if (!container) return;
        container.innerHTML = '<p style="color:#6B7280;">Loading...</p>';
        try {
            const data = await adminApi.get('/admin/categories');
            container.innerHTML = data.categories.map(c => `
                <div class="admin-cat-card">
                    <img src="${c.image_url || 'https://via.placeholder.com/80'}" width="80" height="80" style="border-radius:12px;object-fit:cover;" onerror="this.src='https://via.placeholder.com/80'">
                    <div class="admin-cat-info">
                        <div style="font-weight:600;">${c.name}</div>
                        <div style="font-size:12px;color:#6B7280;">/${c.slug}</div>
                    </div>
                    <div style="display:flex;gap:8px;">
                        <button class="admin-btn admin-btn-sm" onclick="editCategoryPrompt(${c.id}, '${c.name}', '${c.slug}', '${c.image_url || ''}')">Edit</button>
                        <button class="admin-btn admin-btn-sm admin-btn-danger" onclick="deleteCategory(${c.id})">Del</button>
                    </div>
                </div>
            `).join('') || '<p style="color:#6B7280;">No categories yet.</p>';
        } catch (e) {
            container.innerHTML = `<p style="color:red;">${e.message}</p>`;
        }
    };

    window.editCategoryPrompt = function (id, name, slug, imageUrl) {
        const newName = prompt('Category name:', name);
        if (!newName) return;
        const newImage = prompt('Image URL:', imageUrl);
        adminApi.put(`/admin/categories/${id}`, { name: newName, image_url: newImage })
            .then(() => { showAdminToast('Category updated'); loadAdminCategories(); })
            .catch(e => showAdminToast(e.message, true));
    };

    window.deleteCategory = function (id) {
        if (!confirm('Delete this category?')) return;
        adminApi.delete(`/admin/categories/${id}`)
            .then(() => { showAdminToast('Category deleted'); loadAdminCategories(); })
            .catch(e => showAdminToast(e.message, true));
    };

    window.createCategoryFromForm = async function () {
        const name = document.getElementById('new-cat-name')?.value?.trim();
        const slug = document.getElementById('new-cat-slug')?.value?.trim();
        const image = document.getElementById('new-cat-image')?.value?.trim();
        if (!name || !slug) { showAdminToast('Name and slug required', true); return; }
        try {
            await adminApi.post('/admin/categories', { name, slug, image_url: image });
            showAdminToast('Category created');
            loadAdminCategories();
        } catch (e) { showAdminToast(e.message, true); }
    };

    // ─── Banners ──────────────────────────────────────────────────────────────
    window.loadAdminBanners = async function () {
        const container = document.getElementById('admin-banners-list');
        if (!container) return;
        container.innerHTML = '<p style="color:#6B7280;">Loading...</p>';
        try {
            const data = await adminApi.get('/admin/banners');
            container.innerHTML = data.banners.map(b => `
                <div class="admin-banner-card" style="background:${b.bg_gradient || '#1F2937'}">
                    <div style="flex:1;">
                        <div style="color:white;font-weight:700;font-size:16px;">${b.title.replace('\n', ' ')}</div>
                        <div style="color:rgba(255,255,255,0.7);font-size:13px;">${b.subtitle || ''}</div>
                        <div style="color:white;font-size:12px;margin-top:6px;">Button: ${b.button_text}</div>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:6px;">
                        <button class="admin-btn admin-btn-sm" style="background:rgba(255,255,255,0.2);color:white;border:1px solid rgba(255,255,255,0.3);" onclick="editBannerPrompt(${b.id}, '${encodeURIComponent(b.title)}', '${encodeURIComponent(b.subtitle || '')}', '${encodeURIComponent(b.image_url || '')}', '${encodeURIComponent(b.button_text || '')}')">Edit</button>
                        <button class="admin-btn admin-btn-sm admin-btn-danger" onclick="deleteBanner(${b.id})">Delete</button>
                    </div>
                </div>
            `).join('') || '<p style="color:#6B7280;">No banners yet.</p>';
        } catch (e) {
            container.innerHTML = `<p style="color:red;">${e.message}</p>`;
        }
    };

    window.editBannerPrompt = function (id, title, subtitle, imageUrl, btnText) {
        const t = prompt('Banner title:', decodeURIComponent(title));
        if (!t) return;
        const sub = prompt('Subtitle:', decodeURIComponent(subtitle));
        const img = prompt('Image URL:', decodeURIComponent(imageUrl));
        const btn = prompt('Button text:', decodeURIComponent(btnText));
        adminApi.put(`/admin/banners/${id}`, { title: t, subtitle: sub, image_url: img, button_text: btn })
            .then(() => { showAdminToast('Banner updated'); loadAdminBanners(); })
            .catch(e => showAdminToast(e.message, true));
    };

    window.deleteBanner = function (id) {
        if (!confirm('Delete this banner?')) return;
        adminApi.delete(`/admin/banners/${id}`)
            .then(() => { showAdminToast('Banner deleted'); loadAdminBanners(); })
            .catch(e => showAdminToast(e.message, true));
    };

    // ─── UI Assets Editor ─────────────────────────────────────────────────────
    window.loadAdminUIAssets = async function () {
        const container = document.getElementById('admin-ui-assets-container');
        if (!container) return;
        container.innerHTML = '<p style="color:#6B7280;padding:20px;">Loading UI assets...</p>';
        try {
            const data = await adminApi.get('/admin/ui-assets');
            // Group by section
            const grouped = {};
            data.assets.forEach(a => {
                if (!grouped[a.section]) grouped[a.section] = [];
                grouped[a.section].push(a);
            });

            let html = '';
            for (const [section, assets] of Object.entries(grouped)) {
                html += `<div class="ui-asset-section">
                    <div class="ui-asset-section-title">${section.replace(/_/g, ' ').toUpperCase()}</div>
                    ${assets.map(a => `
                        <div class="ui-asset-row" id="uia-row-${a.key}">
                            <div class="ui-asset-label">
                                <span>${a.label}</span>
                                ${a.description ? `<small>${a.description}</small>` : ''}
                            </div>
                            <div class="ui-asset-input-wrap">
                                ${a.asset_type === 'image'
                        ? `<div style="display:flex;gap:8px;align-items:center;">
                                         <img id="uia-preview-${a.key}" src="${a.value || ''}" width="48" height="48" style="border-radius:8px;object-fit:cover;border:1px solid #E5E7EB;" onerror="this.src='https://via.placeholder.com/48'">
                                         <input type="text" class="admin-input" id="uia-${a.key}" value="${escHtml(a.value || '')}" style="flex:1;" placeholder="Image URL" oninput="document.getElementById('uia-preview-${a.key}').src=this.value">
                                       </div>`
                        : `<input type="text" class="admin-input" id="uia-${a.key}" value="${escHtml(a.value || '')}" style="width:100%;">`
                    }
                            </div>
                            <button class="admin-btn admin-btn-sm" onclick="saveUIAsset('${a.key}')">Save</button>
                        </div>
                    `).join('')}
                </div>`;
            }
            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p style="color:red;padding:20px;">${e.message}</p>`;
        }
    };

    window.saveUIAsset = async function (key) {
        const input = document.getElementById(`uia-${key}`);
        if (!input) return;
        try {
            await adminApi.put(`/admin/ui-assets/${key}`, { value: input.value });
            showAdminToast('Saved! Refresh page to see changes.');
            // Invalidate cache
            sessionStorage.removeItem('em_ui_config');
        } catch (e) {
            showAdminToast(e.message, true);
        }
    };

    window.saveAllUIAssets = async function () {
        const inputs = document.querySelectorAll('[id^="uia-"]');
        const updates = [];
        inputs.forEach(input => {
            const key = input.id.replace('uia-', '');
            if (!key.includes('preview')) updates.push({ key, value: input.value });
        });
        try {
            await adminApi.put('/admin/ui-assets', { updates });
            showAdminToast(`Saved ${updates.length} UI assets! Refresh page to see changes.`);
            sessionStorage.removeItem('em_ui_config');
        } catch (e) {
            showAdminToast(e.message, true);
        }
    };

    // ─── Orders ───────────────────────────────────────────────────────────────
    window.loadAdminOrders = async function () {
        const container = document.getElementById('admin-orders-table-body');
        if (!container) return;
        container.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#6B7280;">Loading...</td></tr>';
        try {
            const data = await adminApi.get('/admin/orders');
            if (!data.orders.length) {
                container.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#6B7280;">No orders yet.</td></tr>';
                return;
            }
            container.innerHTML = data.orders.map(o => `
                <tr>
                    <td>#${o.id}</td>
                    <td>${o.user_id ? 'User #' + o.user_id : 'Guest'}</td>
                    <td>$${o.total_amount.toFixed(2)}</td>
                    <td><span class="order-status status-${o.status}">${o.status}</span></td>
                    <td>${new Date(o.created_at).toLocaleDateString()}</td>
                    <td>
                        <select class="admin-input" style="padding:4px 8px;font-size:12px;" onchange="updateOrderStatus(${o.id}, this.value)">
                            ${['pending', 'processing', 'shipped', 'delivered', 'cancelled'].map(s =>
                `<option value="${s}" ${o.status === s ? 'selected' : ''}>${s}</option>`
            ).join('')}
                        </select>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            container.innerHTML = `<tr><td colspan="5" style="color:red;padding:20px;">${e.message}</td></tr>`;
        }
    };

    window.updateOrderStatus = async function (id, status) {
        try {
            await adminApi.put(`/admin/orders/${id}`, { status });
            showAdminToast(`Order #${id} → ${status}`);
        } catch (e) {
            showAdminToast(e.message, true);
        }
    };

    // ─── Admin Logout ─────────────────────────────────────────────────────────
    window.adminLogout = async function () {
        try {
            await fetch('/auth/logout', { method: 'POST', credentials: 'same-origin' });
            window.switchPage('home');
        } catch (e) {
            window.switchPage('home');
        }
    };

    // ─── Helpers ──────────────────────────────────────────────────────────────
    function showAdminToast(message, isError = false) {
        if (window.showToast) {
            window.showToast(message, isError ? 'error' : 'success');
        } else {
            alert(message);
        }
    }

    function escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    // Close modals on overlay click
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.classList.remove('active');
        }
    });

})();

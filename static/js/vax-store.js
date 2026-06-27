const API = {
    products: '/api/products/',
    categories: '/api/categories/',
    brands: '/api/brands/',
    stats: '/api/products/stats/',
    login: '/api/auth/login/',
    register: '/api/auth/register/',
    me: '/api/auth/me/',
    orders: '/api/orders/'
};

const SKATE_CATEGORIES = ['Decks', 'Complete Skateboards', 'Trucks', 'Wheels', 'Bearings', 'Parts'];
const CLOTHES_CATEGORIES = ['Shoes', 'T-Shirts', 'Outerwear', 'Pants', 'Shorts', 'Headwear'];

let products = [];
let categories = [];
let brands = [];
let currentProduct = null;
let currentFilters = { department: '', categoryName: '', brandId: '', recommended: false };
let accessToken = localStorage.getItem('vax_access') || '';
let currentUser = null;
let cart = JSON.parse(localStorage.getItem('vax_cart') || '[]');

const $ = (id) => document.getElementById(id);

function money(value) { return `$${Number(value || 0).toFixed(2)}`; }
function authHeaders() { return accessToken ? { Authorization: `Bearer ${accessToken}` } : {}; }
function imageUrl(value) { return value || ''; }
function getResults(data) { return data.results || data; }

async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);
    let data = {};
    try { data = await response.json(); } catch (e) {}
    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
    return data;
}

function showMessage(text, type = 'success') {
    const box = $('messageBox');
    box.textContent = text;
    box.classList.remove('hidden');
    box.style.background = type === 'error' ? 'rgba(255,77,77,.14)' : 'rgba(247,255,0,.10)';
    box.style.borderColor = type === 'error' ? 'rgba(255,77,77,.35)' : 'rgba(247,255,0,.35)';
    setTimeout(() => box.classList.add('hidden'), 3500);
}

function startVaxVideo() {
    const video = $('vaxLocalVideo');
    if (!video) return;
    video.muted = true;
    video.loop = true;
    const playPromise = video.play();
    if (playPromise && typeof playPromise.catch === 'function') {
        playPromise.catch(() => {});
    }
}

function enterShop() {
    $('intro').style.display = 'none';
    $('shopHeader').classList.remove('hidden-header');
    $('shop').classList.remove('hidden-shop');
    sessionStorage.setItem('vax_entered', '1');
    startVaxVideo();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function init() {
    if (sessionStorage.getItem('vax_entered') === '1') enterShop();
    updateCartUI();
    await loadMe();
    await loadCategories();
    await loadBrands();
    await loadProducts();
}

async function loadMe() {
    if (!accessToken) return;
    try {
        currentUser = await fetchJSON(API.me, { headers: authHeaders() });
        $('loginOpenBtn').textContent = currentUser.username;
        $('loginOpenBtn').title = 'Open profile';
        $('registerOpenBtn').textContent = 'Logout';
        if (currentUser.role === 'manager') $('adminPanelBtn').classList.remove('hidden');
    } catch (error) {
        accessToken = '';
        currentUser = null;
        localStorage.removeItem('vax_access');
        $('loginOpenBtn').textContent = 'Login';
        $('loginOpenBtn').title = '';
        $('registerOpenBtn').textContent = 'Register';
        $('adminPanelBtn').classList.add('hidden');
    }
}

async function loadCategories() {
    try {
        categories = getResults(await fetchJSON(API.categories));
        renderCategorySelect();
    } catch (error) { console.log(error); }
}

async function loadBrands() {
    try {
        brands = getResults(await fetchJSON(API.brands));
        renderBrandMenus();
    } catch (error) { console.log(error); }
}

function renderCategorySelect() {
    const select = $('categorySelect');
    select.innerHTML = '<option value="">All categories</option>';
    categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = `${c.name} (${c.department})`;
        select.appendChild(opt);
    });
}

function renderBrandMenus() {
    const brandLinks = $('brandLinks');
    const brandSelect = $('brandSelect');
    brandLinks.innerHTML = '';
    brandSelect.innerHTML = '<option value="">All brands</option>';
    if (!brands.length) brandLinks.innerHTML = '<p style="color:#aaa;margin:0">Add brands in admin panel.</p>';
    brands.forEach(brand => {
        const b = document.createElement('button');
        b.textContent = brand.name;
        b.onclick = () => {
            currentFilters = { department: '', categoryName: '', brandId: brand.id, recommended: false };
            $('brandSelect').value = brand.id;
            $('collectionTitle').textContent = brand.name;
            applyFilterVisibility('brand');
            loadProducts();
        };
        brandLinks.appendChild(b);
        const opt = document.createElement('option');
        opt.value = brand.id;
        opt.textContent = brand.name;
        brandSelect.appendChild(opt);
    });
}

function categoryByName(name, department) {
    return categories.find(c => c.name.toLowerCase() === String(name).toLowerCase() && (!department || c.department === department));
}

function applyFilterVisibility(mode) {
    // All fields stay visible; placeholders explain different category needs.
    if (mode === 'clothes') $('sizeInput').placeholder = 'Size e.g. S, M, L, 42';
    else if (mode === 'brand') $('sizeInput').placeholder = 'Size / product kind optional';
    else $('sizeInput').placeholder = 'Size e.g. 8.25, 52mm';
}

async function loadProducts() {
    const grid = $('productsGrid');
    grid.innerHTML = '<div class="message">Loading VAX products...</div>';
    const params = new URLSearchParams();
    params.set('status', 'published');
    if (currentFilters.department) params.set('department', currentFilters.department);

    let categoryId = $('categorySelect').value;
    if (currentFilters.categoryName) {
        const cat = categoryByName(currentFilters.categoryName, currentFilters.department);
        if (cat) categoryId = cat.id;
    }
    if (categoryId) params.set('category', categoryId);

    if (currentFilters.brandId || $('brandSelect').value) params.set('brand', currentFilters.brandId || $('brandSelect').value);
    if ($('searchInput').value.trim()) params.set('search', $('searchInput').value.trim());
    if ($('minPriceInput').value) params.set('price__gte', $('minPriceInput').value);
    if ($('maxPriceInput').value) params.set('price__lte', $('maxPriceInput').value);
    if ($('sizeInput').value.trim()) params.set('size__icontains', $('sizeInput').value.trim());
    if ($('sortSelect').value) params.set('ordering', $('sortSelect').value);

    try {
        products = getResults(await fetchJSON(`${API.products}?${params}`));
        renderProducts();
    } catch (error) {
        grid.innerHTML = '';
        showMessage(error.message, 'error');
    }
}

function renderProducts() {
    const grid = $('productsGrid');
    grid.innerHTML = '';
    if (!products.length) {
        grid.innerHTML = '<div class="message">No products in this collection yet. Add them from admin panel.</div>';
        return;
    }
    products.forEach(product => {
        const main = imageUrl(product.main_image);
        const hover = imageUrl(product.hover_image);
        const card = document.createElement('article');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="product-image-wrap">
                ${main ? `<img class="main-img ${hover ? 'has-hover' : ''}" src="${main}" alt="${escapeHtml(product.title)}">` : '<div class="fake-product-img"><div class="fake-board"></div></div>'}
                ${hover ? `<img class="hover-img" src="${hover}" alt="${escapeHtml(product.title)} hover">` : ''}
            </div>
            <h3>${escapeHtml(product.title)}</h3>
            <div class="card-meta">
                <span>${escapeHtml(product.brand_name || 'VAX')}</span>
                <span class="card-price">${money(product.price)}</span>
            </div>
        `;
        card.addEventListener('click', () => openProduct(product.id));
        grid.appendChild(card);
    });
}

function escapeHtml(str) {
    return String(str || '').replace(/[&<>'"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[ch]));
}

function openProduct(id) {
    const product = products.find(p => p.id === id);
    if (!product) return;
    currentProduct = product;
    const imgs = [product.main_image, product.hover_image, product.detail_image_1, product.detail_image_2, ...(product.media || []).map(m => m.file)].filter(Boolean);
    $('detailMainImage').src = imgs[0] || '';
    $('detailMainImage').alt = product.title;
    $('detailThumbs').innerHTML = '';
    imgs.forEach(src => {
        const btn = document.createElement('button');
        btn.innerHTML = `<img src="${src}" alt="${escapeHtml(product.title)}">`;
        btn.onclick = () => $('detailMainImage').src = src;
        $('detailThumbs').appendChild(btn);
    });
    $('detailBrand').textContent = product.brand_name || product.category_name || 'VAX SHOP';
    $('detailTitle').textContent = product.title;
    $('detailPrice').textContent = money(product.price);
    $('detailSize').textContent = product.size ? `Size: ${product.size} • Stock: ${product.stock}` : `Stock: ${product.stock}`;
    $('detailDescription').textContent = product.description;
    $('productModal').classList.remove('hidden');
}

function closeProduct() { $('productModal').classList.add('hidden'); currentProduct = null; }

function addToCart(product) {
    if (!product) return;
    const existing = cart.find(i => i.id === product.id);
    if (existing) existing.quantity += 1;
    else cart.push({ id: product.id, title: product.title, price: product.price, image: product.main_image, quantity: 1 });
    saveCart();
    showMessage(`${product.title} added to cart`);
}

function saveCart() { localStorage.setItem('vax_cart', JSON.stringify(cart)); updateCartUI(); }
function updateCartUI() {
    $('cartCount').textContent = cart.reduce((sum, i) => sum + i.quantity, 0);
    const wrap = $('cartItems');
    wrap.innerHTML = '';
    if (!cart.length) wrap.innerHTML = '<p style="color:#aaa">Your cart is empty.</p>';
    cart.forEach(item => {
        const row = document.createElement('div');
        row.className = 'cart-item';
        row.innerHTML = `
            <div><h4>${escapeHtml(item.title)}</h4><p>${money(item.price)} × ${item.quantity}</p></div>
            <div class="qty"><button onclick="changeQty(${item.id}, -1)">−</button><span>${item.quantity}</span><button onclick="changeQty(${item.id}, 1)">+</button></div>
        `;
        wrap.appendChild(row);
    });
    const total = cart.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0);
    $('cartTotal').textContent = money(total);
}
function changeQty(id, amount) {
    const item = cart.find(i => i.id === id);
    if (!item) return;
    item.quantity += amount;
    if (item.quantity <= 0) cart = cart.filter(i => i.id !== id);
    saveCart();
}
window.changeQty = changeQty;

function openCart() { $('cartDrawer').classList.add('open'); $('overlay').classList.remove('hidden'); }
function closeCart() { $('cartDrawer').classList.remove('open'); $('overlay').classList.add('hidden'); }

function openAuth(mode = 'login') {
    $('authModal').classList.remove('hidden');
    mode === 'register' ? showRegister() : showLogin();
}
function closeAuth() { $('authModal').classList.add('hidden'); }
function showLogin() { $('loginForm').classList.remove('hidden'); $('registerForm').classList.add('hidden'); $('loginTab').classList.add('active'); $('registerTab').classList.remove('active'); }
function showRegister() { $('registerForm').classList.remove('hidden'); $('loginForm').classList.add('hidden'); $('registerTab').classList.add('active'); $('loginTab').classList.remove('active'); }

async function login(e) {
    e.preventDefault();
    try {
        const data = await fetchJSON(API.login, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: $('loginUsername').value, password: $('loginPassword').value }) });
        accessToken = data.access;
        localStorage.setItem('vax_access', accessToken);
        await loadMe();
        closeAuth();
        showMessage('Logged in');
    } catch (error) { showMessage(error.message, 'error'); }
}

async function register(e) {
    e.preventDefault();
    try {
        await fetchJSON(API.register, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: $('registerUsername').value, email: $('registerEmail').value, password: $('registerPassword').value, role: 'customer' }) });
        showMessage('Account created. Login now.');
        showLogin();
    } catch (error) { showMessage(error.message, 'error'); }
}

function logout() {
    accessToken = '';
    currentUser = null;
    localStorage.removeItem('vax_access');
    $('loginOpenBtn').textContent = 'Login';
    $('loginOpenBtn').title = '';
    $('registerOpenBtn').textContent = 'Register';
    $('adminPanelBtn').classList.add('hidden');
    closeProfile();
    showMessage('Logged out');
}

async function checkout() {
    if (!cart.length) return showMessage('Cart is empty', 'error');
    if (!accessToken) { openAuth('login'); return showMessage('Login before checkout', 'error'); }
    const shipping = $('shippingAddress').value.trim();
    if (!shipping) return showMessage('Enter shipping address', 'error');


    try {
        const order = await fetchJSON(API.orders, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...authHeaders() },
            body: JSON.stringify({
                shipping_address: shipping,
                items: cart.map(i => ({ product_id: i.id, quantity: i.quantity }))
            })
        });
        cart = [];
        saveCart();
        $('shippingAddress').value = '';
        closeCart();
        await loadProducts();
        await loadPurchaseHistory();
        showMessage(`Order #${order.id} created`);
    } catch (error) { showMessage(error.message, 'error'); }
}

function openProfile() {
    if (!currentUser) {
        openAuth('login');
        return showMessage('Login to open profile', 'error');
    }
    $('profileUsername').value = currentUser.username || '';
    $('profileEmail').value = currentUser.email || '';
    $('profileModal').classList.remove('hidden');
    loadPurchaseHistory();
}

function closeProfile() {
    const modal = $('profileModal');
    if (modal) modal.classList.add('hidden');
}

async function saveProfile(event) {
    event.preventDefault();
    if (!accessToken) return showMessage('Login first', 'error');

    try {
        currentUser = await fetchJSON(API.me, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', ...authHeaders() },
            body: JSON.stringify({
                username: $('profileUsername').value.trim(),
                email: $('profileEmail').value.trim()
            })
        });
        $('loginOpenBtn').textContent = currentUser.username;
        showMessage('Profile updated');
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function loadPurchaseHistory() {
    const list = $('purchaseHistoryList');
    if (!list) return;
    if (!accessToken) {
        list.innerHTML = '<p class="muted-small">Login to see your orders.</p>';
        return;
    }

    list.innerHTML = '<p class="muted-small">Loading orders...</p>';

    try {
        const data = await fetchJSON(API.orders, { headers: authHeaders() });
        const orders = getResults(data);

        if (!orders.length) {
            list.innerHTML = '<p class="muted-small">No purchases yet.</p>';
            return;
        }

        list.innerHTML = '';
        orders.forEach(order => {
            const orderDate = order.created_at ? new Date(order.created_at).toLocaleString() : '';
            const items = (order.items || []).map(item => `
                <li>
                    <span>${escapeHtml(item.product_title || 'Product')}</span>
                    <strong>${item.quantity} × ${money(item.unit_price)}</strong>
                </li>
            `).join('');

            const card = document.createElement('article');
            card.className = 'history-order';
            card.innerHTML = `
                <div class="history-order-top">
                    <div>
                        <h4>Order #${order.id}</h4>
                        <p>${escapeHtml(orderDate)}</p>
                    </div>
                    <span>${escapeHtml(order.status || 'paid')}</span>
                </div>
                <ul class="history-items">${items || '<li>No items found</li>'}</ul>
                <div class="history-total">Total: <strong>${money(order.total_price)}</strong></div>
            `;
            list.appendChild(card);
        });
    } catch (error) {
        list.innerHTML = `<p class="muted-small">${escapeHtml(error.message)}</p>`;
    }
}

function resetFilters() {
    $('searchInput').value = '';
    $('categorySelect').value = '';
    $('brandSelect').value = '';
    $('minPriceInput').value = '';
    $('maxPriceInput').value = '';
    $('sizeInput').value = '';
    $('sortSelect').value = '-created_at';
    currentFilters = { department: '', categoryName: '', brandId: '', recommended: false };
    $('collectionTitle').textContent = 'All products';
    applyFilterVisibility('all');
    loadProducts();
}

let searchTimer;
['searchInput', 'minPriceInput', 'maxPriceInput', 'sizeInput'].forEach(id => $(id).addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(loadProducts, 350); }));
['categorySelect', 'brandSelect', 'sortSelect'].forEach(id => $(id).addEventListener('change', () => { currentFilters.categoryName = ''; currentFilters.brandId = ''; currentFilters.recommended = false; loadProducts(); }));

document.querySelectorAll('[data-category-name]').forEach(btn => btn.addEventListener('click', () => {
    const department = btn.dataset.collection;
    const name = btn.dataset.categoryName;
    currentFilters = { department, categoryName: name, brandId: '', recommended: false };
    $('collectionTitle').textContent = name;
    $('brandSelect').value = '';
    $('categorySelect').value = '';
    applyFilterVisibility(department);
    loadProducts();
}));

document.querySelectorAll('[data-collection]').forEach(btn => btn.addEventListener('click', () => {
    if (btn.dataset.categoryName) return;
    const department = btn.dataset.collection;
    currentFilters = { department, categoryName: '', brandId: '', recommended: false };
    $('collectionTitle').textContent = department === 'skate' ? 'All skate' : 'All clothes';
    applyFilterVisibility(department);
    loadProducts();
}));


$('enterShopBtn').addEventListener('click', enterShop);
$('showAllBtn').addEventListener('click', () => { currentFilters = { department: '', categoryName: '', brandId: '', recommended: false }; $('collectionTitle').textContent = 'All products'; applyFilterVisibility('all'); loadProducts(); });
$('resetFiltersBtn').addEventListener('click', resetFilters);
$('cartOpenBtn').addEventListener('click', openCart);
$('cartCloseBtn').addEventListener('click', closeCart);
$('overlay').addEventListener('click', closeCart);
$('loginOpenBtn').addEventListener('click', () => currentUser ? openProfile() : openAuth('login'));
$('registerOpenBtn').addEventListener('click', () => currentUser ? logout() : openAuth('register'));
$('adminPanelBtn').addEventListener('click', () => window.location.href = '/admin-panel/');
$('authCloseBtn').addEventListener('click', closeAuth);
$('loginTab').addEventListener('click', showLogin);
$('registerTab').addEventListener('click', showRegister);
$('loginForm').addEventListener('submit', login);
$('registerForm').addEventListener('submit', register);
$('productCloseBtn').addEventListener('click', closeProduct);
$('detailAddCartBtn').addEventListener('click', () => { addToCart(currentProduct); closeProduct(); openCart(); });
$('checkoutBtn').addEventListener('click', checkout);
$('profileCloseBtn').addEventListener('click', closeProfile);
$('profileForm').addEventListener('submit', saveProfile);
$('reloadOrdersBtn').addEventListener('click', loadPurchaseHistory);
$('logoHome').addEventListener('click', resetFilters);


function setupStableDropdowns() {
    const header = document.getElementById('shopHeader');
    const layer = document.getElementById('navDropdownLayer');
    const triggers = Array.from(document.querySelectorAll('[data-menu-target]'));
    const panels = Array.from(document.querySelectorAll('[data-menu-panel]'));

    if (!header || !layer || !triggers.length || !panels.length) return;

    let activePanelId = null;
    let closeTimer = null;

    function placeLayer() {
        const rect = header.getBoundingClientRect();
        layer.style.top = `${Math.max(0, rect.bottom)}px`;
    }

    function cancelClose() {
        if (closeTimer) {
            clearTimeout(closeTimer);
            closeTimer = null;
        }
    }

    function scheduleClose(delay = 350) {
        cancelClose();
        closeTimer = setTimeout(closeMenus, delay);
    }

    function closeMenus() {
        cancelClose();
        panels.forEach(panel => panel.classList.remove('is-open'));
        triggers.forEach(trigger => {
            trigger.classList.remove('menu-active');
            trigger.setAttribute('aria-expanded', 'false');
        });
        layer.setAttribute('aria-hidden', 'true');
        activePanelId = null;
    }

    function openMenu(panelId) {
        cancelClose();
        placeLayer();
        panels.forEach(panel => panel.classList.toggle('is-open', panel.id === panelId));
        triggers.forEach(trigger => {
            const active = trigger.dataset.menuTarget === panelId;
            trigger.classList.toggle('menu-active', active);
            trigger.setAttribute('aria-expanded', active ? 'true' : 'false');
        });
        layer.setAttribute('aria-hidden', 'false');
        activePanelId = panelId;
    }

    // Hover/click opens. Leaving the navbar starts a delay, so you can move down into the dropdown.
    header.addEventListener('mouseenter', cancelClose);
    header.addEventListener('mouseleave', () => scheduleClose(700));

    triggers.forEach(trigger => {
        trigger.setAttribute('aria-haspopup', 'true');
        trigger.setAttribute('aria-expanded', 'false');

        trigger.addEventListener('mouseenter', () => openMenu(trigger.dataset.menuTarget));
        trigger.addEventListener('focus', () => openMenu(trigger.dataset.menuTarget));
        trigger.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            openMenu(trigger.dataset.menuTarget);
        });
    });

    panels.forEach(panel => {
        panel.addEventListener('mouseenter', () => {
            cancelClose();
            openMenu(panel.id);
        });

        // This is the requested behavior: once the mouse leaves the dropdown, it disappears.
        panel.addEventListener('mouseleave', () => scheduleClose(250));

        panel.addEventListener('mousedown', event => event.stopPropagation());
        panel.addEventListener('click', event => {
            event.stopPropagation();
            const clickedOption = event.target.closest('button');
            if (clickedOption) {
                closeMenus();
            }
        });
    });

    document.addEventListener('mousedown', event => {
        if (
            event.target.closest('[data-menu-target]') ||
            event.target.closest('[data-menu-panel]')
        ) {
            return;
        }
        closeMenus();
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') closeMenus();
    });

    window.addEventListener('resize', () => {
        if (activePanelId) placeLayer();
    });
}

setupStableDropdowns();
init();

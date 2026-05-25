const API_BASE = "";
const ORDER_STATUSES = ["new", "confirmed", "paid", "shipped", "delivered", "cancelled"];

const text = {
    requestError: "\u041f\u043e\u043c\u0438\u043b\u043a\u0430 \u0437\u0430\u043f\u0438\u0442\u0443",
    guest: "\u0413\u0456\u0441\u0442\u044c",
    user: "\u041a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447",
    noProducts: "\u0422\u043e\u0432\u0430\u0440\u0456\u0432 \u043f\u043e\u043a\u0438 \u043d\u0435\u043c\u0430\u0454. \u0417\u0430\u043f\u0443\u0441\u0442\u0438 seed.py \u0430\u0431\u043e \u0434\u043e\u0434\u0430\u0439 \u0442\u043e\u0432\u0430\u0440 \u044f\u043a \u0430\u0434\u043c\u0456\u043d.",
    noPhoto: "\u0411\u0435\u0437 \u0444\u043e\u0442\u043e",
    addToCart: "\u0414\u043e\u0434\u0430\u0442\u0438 \u0432 \u043a\u043e\u0448\u0438\u043a",
    loginRequired: "\u041f\u043e\u0442\u0440\u0456\u0431\u0435\u043d \u0432\u0445\u0456\u0434",
    noDescription: "\u041e\u043f\u0438\u0441 \u0432\u0456\u0434\u0441\u0443\u0442\u043d\u0456\u0439",
    stock: "\u041d\u0430 \u0441\u043a\u043b\u0430\u0434\u0456",
    loginForCart: "\u0423\u0432\u0456\u0439\u0434\u0456\u0442\u044c, \u0449\u043e\u0431 \u0431\u0430\u0447\u0438\u0442\u0438 \u043a\u043e\u0448\u0438\u043a.",
    emptyCart: "\u041a\u043e\u0448\u0438\u043a \u043f\u043e\u0440\u043e\u0436\u043d\u0456\u0439.",
    quantity: "\u041a\u0456\u043b\u044c\u043a\u0456\u0441\u0442\u044c",
    total: "\u0420\u0430\u0437\u043e\u043c",
    loginDone: "\u0412\u0445\u0456\u0434 \u0432\u0438\u043a\u043e\u043d\u0430\u043d\u043e.",
    accountCreated: "\u0410\u043a\u0430\u0443\u043d\u0442 \u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043e.",
    loggedOut: "\u0412\u0438 \u0432\u0438\u0439\u0448\u043b\u0438 \u0437 \u0430\u043a\u0430\u0443\u043d\u0442\u0430.",
    addedToCart: "\u0422\u043e\u0432\u0430\u0440 \u0434\u043e\u0434\u0430\u043d\u043e \u0432 \u043a\u043e\u0448\u0438\u043a.",
    removedFromCart: "\u0422\u043e\u0432\u0430\u0440 \u0432\u0438\u0434\u0430\u043b\u0435\u043d\u043e \u0437 \u043a\u043e\u0448\u0438\u043a\u0430.",
    cartUpdated: "\u041a\u043e\u0448\u0438\u043a \u043e\u043d\u043e\u0432\u043b\u0435\u043d\u043e.",
    orderCreated: "\u0417\u0430\u043c\u043e\u0432\u043b\u0435\u043d\u043d\u044f",
    created: "\u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043e",
    productCreated: "\u0422\u043e\u0432\u0430\u0440 \u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043e.",
    statusUpdated: "\u0421\u0442\u0430\u0442\u0443\u0441 \u0437\u043c\u0456\u043d\u0435\u043d\u043e.",
    noOrders: "No orders yet.",
};

const state = {
    token: localStorage.getItem("shopToken"),
    currentUser: null,
    products: [],
    cart: [],
    orders: [],
};

const elements = {
    userEmail: document.querySelector("#userEmail"),
    logoutBtn: document.querySelector("#logoutBtn"),
    loginTab: document.querySelector("#loginTab"),
    registerTab: document.querySelector("#registerTab"),
    loginForm: document.querySelector("#loginForm"),
    registerForm: document.querySelector("#registerForm"),
    productsGrid: document.querySelector("#productsGrid"),
    cartList: document.querySelector("#cartList"),
    message: document.querySelector("#message"),
    orderForm: document.querySelector("#orderForm"),
    refreshProductsBtn: document.querySelector("#refreshProductsBtn"),
    refreshCartBtn: document.querySelector("#refreshCartBtn"),
    adminPanel: document.querySelector("#adminPanel"),
    adminOrdersPanel: document.querySelector("#adminOrdersPanel"),
    productForm: document.querySelector("#productForm"),
    ordersList: document.querySelector("#ordersList"),
    refreshOrdersBtn: document.querySelector("#refreshOrdersBtn"),
};

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function authHeaders() {
    return state.token ? { Authorization: `Bearer ${state.token}` } : {};
}

async function request(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...authHeaders(),
            ...options.headers,
        },
    });

    let data = null;
    const bodyText = await response.text();
    if (bodyText) {
        data = JSON.parse(bodyText);
    }

    if (!response.ok) {
        const detail = data?.detail;
        const message = Array.isArray(detail)
            ? detail.map((item) => item.msg).join(", ")
            : detail || text.requestError;
        throw new Error(message);
    }

    return data;
}

function showMessage(message, isError = false) {
    elements.message.textContent = message;
    elements.message.classList.toggle("error", isError);
    elements.message.classList.remove("hidden");
    window.setTimeout(() => elements.message.classList.add("hidden"), 4500);
}

function formatPrice(value) {
    return new Intl.NumberFormat("uk-UA", {
        style: "currency",
        currency: "UAH",
        maximumFractionDigits: 2,
    }).format(value);
}

function setAuthView(user = null) {
    state.currentUser = user;
    elements.userEmail.textContent = user?.email || (state.token ? text.user : text.guest);
    elements.logoutBtn.classList.toggle("hidden", !state.token);
    elements.adminPanel.classList.toggle("hidden", !user?.is_admin);
    elements.adminOrdersPanel.classList.toggle("hidden", !user?.is_admin);
}

function switchAuthTab(mode) {
    const isLogin = mode === "login";
    elements.loginTab.classList.toggle("active", isLogin);
    elements.registerTab.classList.toggle("active", !isLogin);
    elements.loginForm.classList.toggle("hidden", !isLogin);
    elements.registerForm.classList.toggle("hidden", isLogin);
}

function renderProducts() {
    if (!state.products.length) {
        elements.productsGrid.innerHTML = `<p class="muted">${text.noProducts}</p>`;
        return;
    }

    elements.productsGrid.innerHTML = state.products.map((product) => {
        const image = product.image_url
            ? `<img src="${escapeHtml(product.image_url)}" alt="${escapeHtml(product.name)}">`
            : `<span>${text.noPhoto}</span>`;
        const disabled = product.stock <= 0 || !state.token ? "disabled" : "";
        const buttonText = state.token ? text.addToCart : text.loginRequired;

        return `
            <article class="product-card">
                <div class="product-image">${image}</div>
                <div class="product-body">
                    <div>
                        <h3 class="product-title">${escapeHtml(product.name)}</h3>
                        <p class="product-description">${escapeHtml(product.description || text.noDescription)}</p>
                    </div>
                    <div class="product-meta">
                        <span class="price">${formatPrice(product.price)}</span>
                        <span class="stock">${text.stock}: ${product.stock}</span>
                    </div>
                    <button type="button" ${disabled} data-add-product="${product.id}">${buttonText}</button>
                </div>
            </article>
        `;
    }).join("");
}

function cartTotal() {
    return state.cart.reduce((total, item) => total + item.product.price * item.quantity, 0);
}

function renderCart() {
    if (!state.token) {
        elements.cartList.innerHTML = `<p class="muted">${text.loginForCart}</p>`;
        return;
    }

    if (!state.cart.length) {
        elements.cartList.innerHTML = `<p class="muted">${text.emptyCart}</p>`;
        return;
    }

    const itemsHtml = state.cart.map((item) => `
        <div class="cart-item">
            <div>
                <strong>${escapeHtml(item.product.name)}</strong>
                <small>${formatPrice(item.product.price)} x ${item.quantity}</small>
                <div class="quantity-row">
                    <input type="number" min="1" max="${item.product.stock}" value="${item.quantity}" data-quantity-input="${item.id}">
                    <button class="ghost" type="button" data-update-item="${item.id}">${text.quantity}</button>
                </div>
            </div>
            <button class="danger" type="button" data-remove-item="${item.id}">X</button>
        </div>
    `).join("");

    elements.cartList.innerHTML = `
        ${itemsHtml}
        <p><strong>${text.total}: ${formatPrice(cartTotal())}</strong></p>
    `;
}

function renderOrders() {
    if (!state.orders.length) {
        elements.ordersList.innerHTML = `<p class="muted">${text.noOrders}</p>`;
        return;
    }

    elements.ordersList.innerHTML = state.orders.map((order) => {
        const options = ORDER_STATUSES.map((status) => (
            `<option value="${status}" ${status === order.status ? "selected" : ""}>${status}</option>`
        )).join("");

        return `
            <div class="order-item">
                <div>
                    <strong>#${order.id} - ${escapeHtml(order.customer_name)}</strong>
                    <small>${escapeHtml(order.phone)} | ${formatPrice(order.total_price)} | ${escapeHtml(order.address)}</small>
                </div>
                <select data-order-status="${order.id}">${options}</select>
            </div>
        `;
    }).join("");
}

async function loadProducts() {
    elements.refreshProductsBtn.disabled = true;
    try {
        state.products = await request("/products/");
        renderProducts();
    } catch (error) {
        showMessage(error.message, true);
    } finally {
        elements.refreshProductsBtn.disabled = false;
    }
}

async function loadCart() {
    if (!state.token) {
        state.cart = [];
        renderCart();
        return;
    }

    elements.refreshCartBtn.disabled = true;
    try {
        state.cart = await request("/cart/");
        renderCart();
    } catch (error) {
        showMessage(error.message, true);
    } finally {
        elements.refreshCartBtn.disabled = false;
    }
}

async function loadOrders() {
    if (!state.currentUser?.is_admin) {
        return;
    }

    try {
        state.orders = await request("/orders/admin/all");
        renderOrders();
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function loadMe() {
    if (!state.token) {
        setAuthView();
        return;
    }

    try {
        const user = await request("/auth/me");
        setAuthView(user);
    } catch {
        state.token = null;
        localStorage.removeItem("shopToken");
        setAuthView();
    }
}

async function login(email, password) {
    const data = await request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
    });
    state.token = data.access_token;
    localStorage.setItem("shopToken", state.token);
    await loadMe();
    await loadCart();
    await loadOrders();
    renderProducts();
}

elements.loginTab.addEventListener("click", () => switchAuthTab("login"));
elements.registerTab.addEventListener("click", () => switchAuthTab("register"));

elements.loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        await login(
            document.querySelector("#loginEmail").value,
            document.querySelector("#loginPassword").value,
        );
        showMessage(text.loginDone);
    } catch (error) {
        showMessage(error.message, true);
    }
});

elements.registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.querySelector("#registerEmail").value;
    const password = document.querySelector("#registerPassword").value;

    try {
        await request("/auth/register", {
            method: "POST",
            body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
        });
        await login(email, password);
        showMessage(text.accountCreated);
    } catch (error) {
        showMessage(error.message, true);
    }
});

elements.logoutBtn.addEventListener("click", () => {
    state.token = null;
    state.currentUser = null;
    state.cart = [];
    state.orders = [];
    localStorage.removeItem("shopToken");
    setAuthView();
    renderCart();
    renderProducts();
    showMessage(text.loggedOut);
});

elements.productsGrid.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-add-product]");
    if (!button) {
        return;
    }

    try {
        await request("/cart/add", {
            method: "POST",
            body: JSON.stringify({
                product_id: Number(button.dataset.addProduct),
                quantity: 1,
            }),
        });
        await loadCart();
        showMessage(text.addedToCart);
    } catch (error) {
        showMessage(error.message, true);
    }
});

elements.cartList.addEventListener("click", async (event) => {
    const removeButton = event.target.closest("[data-remove-item]");
    const updateButton = event.target.closest("[data-update-item]");

    try {
        if (removeButton) {
            await request(`/cart/remove/${removeButton.dataset.removeItem}`, {
                method: "DELETE",
            });
            await loadCart();
            showMessage(text.removedFromCart);
        }

        if (updateButton) {
            const input = document.querySelector(`[data-quantity-input="${updateButton.dataset.updateItem}"]`);
            await request(`/cart/${updateButton.dataset.updateItem}`, {
                method: "PUT",
                body: JSON.stringify({ quantity: Number(input.value) }),
            });
            await loadCart();
            showMessage(text.cartUpdated);
        }
    } catch (error) {
        showMessage(error.message, true);
    }
});

elements.orderForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        const order = await request("/orders/", {
            method: "POST",
            body: JSON.stringify({
                customer_name: document.querySelector("#customerName").value,
                phone: document.querySelector("#customerPhone").value,
                address: document.querySelector("#customerAddress").value,
            }),
        });
        elements.orderForm.reset();
        await loadProducts();
        await loadCart();
        await loadOrders();
        showMessage(`${text.orderCreated} #${order.id} ${text.created}.`);
    } catch (error) {
        showMessage(error.message, true);
    }
});

elements.productForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await request("/products/", {
            method: "POST",
            body: JSON.stringify({
                name: document.querySelector("#productName").value,
                description: document.querySelector("#productDescription").value,
                price: Number(document.querySelector("#productPrice").value),
                category: document.querySelector("#productCategory").value,
                image_url: document.querySelector("#productImageUrl").value,
                stock: Number(document.querySelector("#productStock").value),
            }),
        });
        elements.productForm.reset();
        await loadProducts();
        showMessage(text.productCreated);
    } catch (error) {
        showMessage(error.message, true);
    }
});

elements.ordersList.addEventListener("change", async (event) => {
    const select = event.target.closest("[data-order-status]");
    if (!select) {
        return;
    }

    try {
        await request(`/orders/${select.dataset.orderStatus}/status`, {
            method: "PUT",
            body: JSON.stringify({ status: select.value }),
        });
        await loadOrders();
        await loadProducts();
        showMessage(text.statusUpdated);
    } catch (error) {
        showMessage(error.message, true);
    }
});

elements.refreshProductsBtn.addEventListener("click", loadProducts);
elements.refreshCartBtn.addEventListener("click", loadCart);
elements.refreshOrdersBtn.addEventListener("click", loadOrders);

async function init() {
    await loadProducts();
    await loadMe();
    await loadCart();
    await loadOrders();
}

init();

const API_BASE = 'https://east.albion-online-data.com';
const ICON_BASE = 'https://render.albiononline.com/v1/item';

function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

function formatNumber(value) {
    return new Intl.NumberFormat('ko-KR').format(value);
}

let ITEM_DB = null;
let KO_TO_ID = null;
let ID_TO_NAME = null;
const FAVORITES_KEY = 'favorites';

async function loadItemDb() {
    if (ITEM_DB) return ITEM_DB;
    const res = await fetch('/item_db.json');
    if (!res.ok) throw new Error('item_db not found');
    ITEM_DB = await res.json();
    KO_TO_ID = {};
    ID_TO_NAME = {};
    Object.entries(ITEM_DB).forEach(([itemId, names]) => {
        const ko = names.ko || '';
        if (ko) {
            KO_TO_ID[ko] = itemId;
            ID_TO_NAME[itemId] = ko;
        }
    });
    return ITEM_DB;
}

function normalize(text) {
    return text.toLowerCase().replace(/\s+/g, '');
}

function getFavorites() {
    try {
        const raw = localStorage.getItem(FAVORITES_KEY);
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function setFavorites(list) {
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(list));
    window.dispatchEvent(new CustomEvent('favorites:changed'));
}

function isFavorite(itemId) {
    return getFavorites().includes(itemId);
}

function toggleFavorite(itemId) {
    const list = getFavorites();
    const idx = list.indexOf(itemId);
    if (idx >= 0) {
        list.splice(idx, 1);
    } else {
        list.unshift(itemId);
    }
    setFavorites(list);
    return list;
}

function updateFavoriteButton(button, itemId) {
    const active = isFavorite(itemId);
    button.dataset.active = active ? 'true' : 'false';
    button.setAttribute('aria-pressed', active ? 'true' : 'false');
    button.textContent = active ? '★ 즐겨찾기' : '☆ 즐겨찾기';
}

async function resolveItem(query) {
    await loadItemDb();
    const q = query.trim();
    const qNorm = normalize(q);

    const upper = q.toUpperCase();
    if (upper.startsWith('T') && upper.includes('_') && ITEM_DB[upper]) {
        return upper;
    }
    if (upper.startsWith('T') && upper.includes('_')) {
        return upper;
    }

    if (KO_TO_ID[q]) return KO_TO_ID[q];
    for (const [ko, itemId] of Object.entries(KO_TO_ID)) {
        if (normalize(ko) === qNorm) return itemId;
    }

    const partial = Object.entries(KO_TO_ID).filter(([ko]) => normalize(ko).includes(qNorm));
    if (partial.length === 1) return partial[0][1];
    return null;
}

async function searchItems(keyword, limit = 15) {
    await loadItemDb();
    const kw = normalize(keyword);
    const results = [];
    const seen = new Set();

    for (const [itemId, names] of Object.entries(ITEM_DB)) {
        if (results.length >= limit) break;
        if (seen.has(itemId)) continue;
        const ko = names.ko || '';
        const en = names.en || '';
        if (normalize(ko).includes(kw) || normalize(en).includes(kw) || itemId.toLowerCase().includes(kw)) {
            const display = ko || en || itemId;
            results.push({ name: display, id: itemId, icon: `${ICON_BASE}/${itemId}.png?size=64&quality=1` });
            seen.add(itemId);
        }
    }

    return results;
}

function renderSearchResults(dropdown, results) {
    dropdown.innerHTML = '';
    if (!results.length) {
        const empty = document.createElement('div');
        empty.className = 'search-empty';
        empty.textContent = '검색 결과가 없습니다.';
        dropdown.appendChild(empty);
        dropdown.style.display = 'block';
        return;
    }

    results.forEach(item => {
        const row = document.createElement('div');
        row.className = 'search-item';
        row.dataset.id = item.id;

        const img = document.createElement('img');
        img.src = item.icon;
        img.alt = item.name;

        const meta = document.createElement('div');
        meta.className = 'search-meta';

        const name = document.createElement('span');
        name.className = 'search-name';
        name.textContent = item.name;

        const id = document.createElement('span');
        id.className = 'search-id';
        id.textContent = item.id;

        meta.appendChild(name);
        meta.appendChild(id);
        const fav = document.createElement('button');
        fav.className = 'favorite-toggle';
        fav.type = 'button';
        fav.title = '즐겨찾기';
        fav.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleFavorite(item.id);
            fav.dataset.active = isFavorite(item.id) ? 'true' : 'false';
            window.dispatchEvent(new CustomEvent('favorites:changed'));
        });
        fav.dataset.active = isFavorite(item.id) ? 'true' : 'false';

        row.appendChild(img);
        row.appendChild(meta);
        row.appendChild(fav);
        dropdown.appendChild(row);
    });

    dropdown.style.display = 'block';
}

function initSearchAutocomplete(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;

    const doSearch = debounce(async () => {
        const query = input.value.trim();
        if (!query) {
            dropdown.style.display = 'none';
            dropdown.innerHTML = '';
            return;
        }
        const results = await searchItems(query, 15);
        renderSearchResults(dropdown, results);
    }, 250);

    input.addEventListener('input', doSearch);

    input.addEventListener('keydown', async (e) => {
        if (e.key !== 'Enter') return;
        const query = input.value.trim();
        if (!query) return;
        const id = await resolveItem(query);
        if (id) {
            window.location.href = `/prices.html?item=${encodeURIComponent(id)}`;
        } else {
            renderSearchResults(dropdown, []);
        }
    });

    dropdown.addEventListener('click', (e) => {
        const item = e.target.closest('.search-item');
        if (!item) return;
        const id = item.dataset.id;
        if (e.target.closest('.favorite-toggle')) return;
        window.location.href = `/prices.html?item=${encodeURIComponent(id)}`;
    });

    document.addEventListener('click', (e) => {
        if (e.target === input || dropdown.contains(e.target)) return;
        dropdown.style.display = 'none';
    });
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof initSearchAutocomplete === 'function') {
        initSearchAutocomplete('nav-search-input', 'nav-search-results');
    }
});

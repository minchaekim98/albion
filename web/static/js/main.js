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

async function resolveItem(query) {
    const res = await fetch(`/api/resolve?q=${encodeURIComponent(query)}`);
    if (!res.ok) return null;
    const data = await res.json();
    return data.id || null;
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
        row.appendChild(img);
        row.appendChild(meta);
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
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!res.ok) return;
        const results = await res.json();
        renderSearchResults(dropdown, results);
    }, 250);

    input.addEventListener('input', doSearch);

    input.addEventListener('keydown', async (e) => {
        if (e.key !== 'Enter') return;
        const query = input.value.trim();
        if (!query) return;
        const id = await resolveItem(query);
        if (id) {
            window.location.href = `/prices/${id}`;
        } else {
            renderSearchResults(dropdown, []);
        }
    });

    dropdown.addEventListener('click', (e) => {
        const item = e.target.closest('.search-item');
        if (!item) return;
        const id = item.dataset.id;
        window.location.href = `/prices/${id}`;
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

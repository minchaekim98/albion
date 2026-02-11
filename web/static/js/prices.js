const loadingEl = document.getElementById('prices-loading');
const errorEl = document.getElementById('prices-error');
const contentEl = document.getElementById('prices-content');
const tableBody = document.getElementById('price-table-body');
const historyCitySelect = document.getElementById('history-city');
const historyEmpty = document.getElementById('history-empty');

let historyChart = null;

function formatNumber(value) {
    return new Intl.NumberFormat('ko-KR').format(value);
}

function formatPrice(value) {
    if (!value || value <= 0) return '-';
    return formatNumber(value);
}

function formatDate(value) {
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '-';
    return date.toLocaleString('ko-KR');
}

function showState(state) {
    loadingEl.style.display = state === 'loading' ? 'flex' : 'none';
    errorEl.style.display = state === 'error' ? 'block' : 'none';
    contentEl.style.display = state === 'content' ? 'block' : 'none';
}

async function loadPrices() {
    try {
        showState('loading');
        const res = await fetch(`/api/prices/${ITEM_ID}`);
        if (!res.ok) throw new Error('failed');
        const data = await res.json();
        renderPriceTable(data);
        showState('content');
        await loadHistory(historyCitySelect.value);
    } catch (err) {
        showState('error');
    }
}

function renderPriceTable(data) {
    const byCity = {};
    data.forEach(row => {
        const city = row.city || row.location;
        if (city) byCity[city] = row;
    });

    tableBody.innerHTML = '';
    CITIES.forEach(city => {
        const row = byCity[city] || {};
        const tr = document.createElement('tr');

        const cityCell = document.createElement('td');
        cityCell.textContent = CITY_NAMES_KR[city] || city;
        tr.appendChild(cityCell);

        const sellPrice = document.createElement('td');
        sellPrice.textContent = formatPrice(row.sell_price_min);
        tr.appendChild(sellPrice);

        const sellDate = document.createElement('td');
        sellDate.textContent = formatDate(row.sell_price_min_date);
        tr.appendChild(sellDate);

        const buyPrice = document.createElement('td');
        buyPrice.textContent = formatPrice(row.buy_price_max);
        tr.appendChild(buyPrice);

        const buyDate = document.createElement('td');
        buyDate.textContent = formatDate(row.buy_price_max_date);
        tr.appendChild(buyDate);

        tableBody.appendChild(tr);
    });
}

async function loadHistory(city) {
    try {
        const res = await fetch(`/api/history/${ITEM_ID}?location=${encodeURIComponent(city)}&time_scale=6`);
        if (!res.ok) throw new Error('failed');
        const data = await res.json();
        const series = Array.isArray(data) && data.length ? (data[0].data || []) : [];

        const points = series.map(point => {
            const timestamp = point.timestamp || point.date;
            const price = point.avg_price ?? point.average_price ?? point.sell_price_avg ?? point.buy_price_avg ?? point.price ?? 0;
            return { timestamp, price };
        }).filter(p => p.timestamp && p.price > 0);

        if (!points.length) {
            historyEmpty.style.display = 'block';
            if (historyChart) {
                historyChart.destroy();
                historyChart = null;
            }
            return;
        }

        historyEmpty.style.display = 'none';
        const labels = points.map(p => new Date(p.timestamp).toLocaleDateString('ko-KR'));
        const prices = points.map(p => p.price);

        const ctx = document.getElementById('history-chart');
        if (historyChart) historyChart.destroy();

        historyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: '평균 가격',
                    data: prices,
                    borderColor: '#b85c00',
                    backgroundColor: 'rgba(184, 92, 0, 0.15)',
                    tension: 0.35,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: (value) => formatNumber(value)
                        }
                    }
                }
            }
        });
    } catch (err) {
        historyEmpty.style.display = 'block';
    }
}

historyCitySelect.addEventListener('change', (e) => {
    loadHistory(e.target.value);
});

loadPrices();

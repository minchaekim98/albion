const loadingEl = document.getElementById('gold-loading');
const errorEl = document.getElementById('gold-error');
const contentEl = document.getElementById('gold-content');
const rangeSelect = document.getElementById('gold-range');
const emptyEl = document.getElementById('gold-empty');

let goldChart = null;

function formatNumber(value) {
    return new Intl.NumberFormat('ko-KR').format(value);
}

function showState(state) {
    loadingEl.style.display = state === 'loading' ? 'flex' : 'none';
    errorEl.style.display = state === 'error' ? 'block' : 'none';
    contentEl.style.display = state === 'content' ? 'block' : 'none';
}

async function loadGold(count) {
    try {
        showState('loading');
        const res = await fetch(`/api/gold?count=${count}`);
        if (!res.ok) throw new Error('failed');
        const data = await res.json();

        if (!Array.isArray(data) || data.length === 0) {
            emptyEl.style.display = 'block';
            showState('content');
            return;
        }

        emptyEl.style.display = 'none';
        showState('content');

        const prices = data.map(d => d.price);
        const labels = data.map(d => new Date(d.timestamp).toLocaleDateString('ko-KR'));

        const current = prices[prices.length - 1];
        const high = Math.max(...prices);
        const low = Math.min(...prices);
        const change = current - prices[0];
        const changePct = prices[0] ? (change / prices[0]) * 100 : 0;

        document.getElementById('gold-current').textContent = formatNumber(current);
        document.getElementById('gold-high').textContent = formatNumber(high);
        document.getElementById('gold-low').textContent = formatNumber(low);
        document.getElementById('gold-change').textContent = `${formatNumber(change)} (${changePct.toFixed(2)}%)`;

        const ctx = document.getElementById('gold-chart');
        if (goldChart) goldChart.destroy();

        goldChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: '골드 가격',
                    data: prices,
                    borderColor: '#1f6f8b',
                    backgroundColor: 'rgba(31, 111, 139, 0.15)',
                    tension: 0.35,
                    fill: true
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
        showState('error');
    }
}

rangeSelect.addEventListener('change', (e) => {
    loadGold(e.target.value);
});

loadGold(rangeSelect.value);

const CITIES = [
  'Caerleon',
  'Bridgewatch',
  'Fort Sterling',
  'Lymhurst',
  'Martlock',
  'Thetford',
  'Brecilien'
];

const CITY_NAMES_KR = {
  'Caerleon': '카얼레온',
  'Bridgewatch': '브릿지워치',
  'Fort Sterling': '포트 스털링',
  'Lymhurst': '림허스트',
  'Martlock': '마트록',
  'Thetford': '씨어드',
  'Brecilien': '브레실리엔'
};

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

function parseDate(value) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  if (date.getFullYear() <= 1) return null;
  return date;
}

function formatDate(value) {
  const date = parseDate(value);
  if (!date) return '-';
  return date.toLocaleString('ko-KR');
}

function showState(state) {
  loadingEl.style.display = state === 'loading' ? 'flex' : 'none';
  errorEl.style.display = state === 'error' ? 'block' : 'none';
  contentEl.style.display = state === 'content' ? 'block' : 'none';
}

function rowScore(row) {
  const sell = row.sell_price_min || 0;
  const buy = row.buy_price_max || 0;
  const priceScore = Math.max(sell, buy);
  const sellDate = parseDate(row.sell_price_min_date);
  const buyDate = parseDate(row.buy_price_max_date);
  const timeScore = Math.max(sellDate ? sellDate.getTime() : 0, buyDate ? buyDate.getTime() : 0);
  return { priceScore, timeScore };
}

function renderPriceTable(data) {
  const byCity = {};
  data.forEach(row => {
    const city = row.city || row.location;
    if (!city) return;

    const current = byCity[city];
    if (!current) {
      byCity[city] = row;
      return;
    }

    const a = rowScore(current);
    const b = rowScore(row);
    if (b.priceScore > a.priceScore) {
      byCity[city] = row;
      return;
    }
    if (b.priceScore === a.priceScore && b.timeScore > a.timeScore) {
      byCity[city] = row;
    }
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

async function loadPrices(itemId) {
  try {
    showState('loading');
    const locations = CITIES.map(c => encodeURIComponent(c)).join(',');
    const res = await fetch(`${API_BASE}/api/v2/stats/prices/${itemId}?locations=${locations}`);
    if (!res.ok) throw new Error('failed');
    const data = await res.json();
    renderPriceTable(data);
    showState('content');
    await loadHistory(itemId, historyCitySelect.value);
  } catch (err) {
    showState('error');
  }
}

async function loadHistory(itemId, city) {
  try {
    const res = await fetch(`${API_BASE}/api/v2/stats/history/${itemId}?locations=${encodeURIComponent(city)}&time-scale=6`);
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
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { ticks: { callback: (value) => formatNumber(value) } }
        }
      }
    });
  } catch (err) {
    historyEmpty.style.display = 'block';
  }
}

function setItemHeader(itemId) {
  const itemName = (ID_TO_NAME && ID_TO_NAME[itemId]) || itemId;
  document.getElementById('item-name').textContent = itemName;
  document.getElementById('item-id').textContent = itemId;
  document.getElementById('item-icon').src = `${ICON_BASE}/${itemId}.png?size=128&quality=1`;
}

function getItemIdFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return params.get('item');
}

function initCitySelect() {
  historyCitySelect.innerHTML = '';
  CITIES.forEach(city => {
    const option = document.createElement('option');
    option.value = city;
    option.textContent = CITY_NAMES_KR[city] || city;
    historyCitySelect.appendChild(option);
  });
}

async function initPage() {
  const itemId = getItemIdFromQuery();
  if (!itemId) {
    showState('error');
    return;
  }

  await loadItemDb();
  setItemHeader(itemId);
  initCitySelect();
  const favButton = document.getElementById('favorite-button');
  if (favButton) {
    updateFavoriteButton(favButton, itemId);
    favButton.addEventListener('click', () => {
      toggleFavorite(itemId);
      updateFavoriteButton(favButton, itemId);
    });
  }
  historyCitySelect.addEventListener('change', (e) => loadHistory(itemId, e.target.value));
  loadPrices(itemId);
}

initPage();

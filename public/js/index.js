async function renderFavoriteItems() {
  await loadItemDb();
  const grid = document.getElementById('favorites-items');
  const empty = document.getElementById('favorites-empty');
  if (!grid) return;

  grid.innerHTML = '';
  const favorites = getFavorites();
  if (!favorites.length) {
    if (empty) empty.style.display = 'block';
    return;
  }
  if (empty) empty.style.display = 'none';

  favorites.forEach(itemId => {
    const name = (ID_TO_NAME && ID_TO_NAME[itemId]) || itemId;
    const card = document.createElement('a');
    card.className = 'item-card';
    card.href = `/prices.html?item=${encodeURIComponent(itemId)}`;

    const img = document.createElement('img');
    img.src = `${ICON_BASE}/${itemId}.png?size=128&quality=1`;
    img.alt = name;
    img.className = 'item-card-icon';
    img.loading = 'lazy';

    const title = document.createElement('span');
    title.className = 'item-card-name';
    title.textContent = name;

    const id = document.createElement('span');
    id.className = 'item-card-id';
    id.textContent = itemId;

    const fav = document.createElement('button');
    fav.className = 'favorite-toggle';
    fav.type = 'button';
    fav.title = '즐겨찾기 해제';
    fav.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleFavorite(itemId);
      renderFavoriteItems();
    });
    fav.dataset.active = 'true';

    card.appendChild(img);
    card.appendChild(title);
    card.appendChild(id);
    card.appendChild(fav);
    grid.appendChild(card);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  if (typeof initSearchAutocomplete === 'function') {
    initSearchAutocomplete('hero-search-input', 'hero-search-results');
  }
  renderFavoriteItems();
  window.addEventListener('favorites:changed', renderFavoriteItems);
});

const POPULAR_ITEMS = [
  'T4_BAG', 'T5_BAG', 'T6_BAG',
  'T4_POTION_HEAL', 'T6_POTION_HEAL',
  'T4_POTION_ENERGY', 'T6_POTION_ENERGY',
  'T3_MOUNT_HORSE', 'T5_MOUNT_ARMORED_HORSE', 'T3_MOUNT_OX',
  'T4_MAIN_SWORD', 'T4_2H_BOW', 'T4_MAIN_FIRESTAFF',
  'T4_HEAD_PLATE_SET1', 'T4_ARMOR_PLATE_SET1', 'T4_SHOES_PLATE_SET1',
  'T4_HEAD_LEATHER_SET1', 'T4_ARMOR_LEATHER_SET1',
  'T4_HEAD_CLOTH_SET1', 'T4_ARMOR_CLOTH_SET1',
  'T4_CAPEITEM_HERETIC'
];

async function renderPopularItems() {
  await loadItemDb();
  const grid = document.getElementById('popular-items');
  if (!grid) return;

  grid.innerHTML = '';
  POPULAR_ITEMS.forEach(itemId => {
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

    card.appendChild(img);
    card.appendChild(title);
    card.appendChild(id);
    grid.appendChild(card);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  if (typeof initSearchAutocomplete === 'function') {
    initSearchAutocomplete('hero-search-input', 'hero-search-results');
  }
  renderPopularItems();
});

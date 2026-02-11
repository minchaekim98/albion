const CATEGORIES = {
  weapon_melee: '근접 무기',
  weapon_ranged: '원거리 무기',
  weapon_magic: '마법 무기',
  armor: '방어구',
  accessory: '액세서리',
  mount: '탈것',
  resource: '자원',
  consumable: '소모품'
};

const SUBCATEGORIES = {
  weapon_melee: [
    ['검', 'MAIN_SWORD'],
    ['클레이모어', '2H_CLAYMORE'],
    ['쌍검', '2H_DUALSWORD'],
    ['도끼', 'MAIN_AXE'],
    ['그레이트 액스', '2H_AXE'],
    ['할버드', '2H_HALBERD'],
    ['메이스', 'MAIN_MACE'],
    ['해머', 'MAIN_HAMMER'],
    ['그레이트 해머', '2H_HAMMER'],
    ['폴해머', '2H_POLEHAMMER'],
    ['창', 'MAIN_SPEAR'],
    ['파이크', '2H_SPEAR'],
    ['글레이브', '2H_GLAIVE'],
    ['단검', 'MAIN_DAGGER'],
    ['쌍단검', '2H_DAGGERPAIR'],
    ['쿼터스태프', '2H_QUARTERSTAFF']
  ],
  weapon_ranged: [
    ['활', '2H_BOW'],
    ['롱보우', '2H_LONGBOW'],
    ['워보우', '2H_WARBOW'],
    ['석궁', '2H_CROSSBOW'],
    ['경량 석궁', 'MAIN_1HCROSSBOW'],
    ['대형 석궁', '2H_CROSSBOWLARGE'],
    ['반복 석궁', 'MAIN_REPEATINGCROSSBOW']
  ],
  weapon_magic: [
    ['불 지팡이', 'MAIN_FIRESTAFF'],
    ['그레이트 불 지팡이', '2H_FIRESTAFF'],
    ['얼음 지팡이', 'MAIN_FROSTSTAFF'],
    ['그레이트 얼음 지팡이', '2H_FROSTSTAFF'],
    ['아케인 지팡이', 'MAIN_ARCANESTAFF'],
    ['그레이트 아케인 지팡이', '2H_ARCANESTAFF'],
    ['신성 지팡이', 'MAIN_HOLYSTAFF'],
    ['그레이트 신성 지팡이', '2H_HOLYSTAFF'],
    ['자연 지팡이', 'MAIN_NATURESTAFF'],
    ['그레이트 자연 지팡이', '2H_NATURESTAFF'],
    ['저주 지팡이', 'MAIN_CURSEDSTAFF'],
    ['그레이트 저주 지팡이', '2H_CURSEDSTAFF']
  ],
  armor: [
    ['판금 투구', 'HEAD_PLATE_SET1'],
    ['판금 갑옷', 'ARMOR_PLATE_SET1'],
    ['판금 장화', 'SHOES_PLATE_SET1'],
    ['가죽 투구', 'HEAD_LEATHER_SET1'],
    ['가죽 갑옷', 'ARMOR_LEATHER_SET1'],
    ['가죽 장화', 'SHOES_LEATHER_SET1'],
    ['천 투구', 'HEAD_CLOTH_SET1'],
    ['천 로브', 'ARMOR_CLOTH_SET1'],
    ['천 신발', 'SHOES_CLOTH_SET1'],
    ['판금 투구 (아티팩트)', 'HEAD_PLATE_SET2'],
    ['판금 갑옷 (아티팩트)', 'ARMOR_PLATE_SET2'],
    ['판금 장화 (아티팩트)', 'SHOES_PLATE_SET2'],
    ['가죽 투구 (아티팩트)', 'HEAD_LEATHER_SET2'],
    ['가죽 갑옷 (아티팩트)', 'ARMOR_LEATHER_SET2'],
    ['가죽 장화 (아티팩트)', 'SHOES_LEATHER_SET2'],
    ['천 투구 (아티팩트)', 'HEAD_CLOTH_SET2'],
    ['천 로브 (아티팩트)', 'ARMOR_CLOTH_SET2'],
    ['천 신발 (아티팩트)', 'SHOES_CLOTH_SET2']
  ],
  accessory: [
    ['가방', 'BAG'],
    ['망토', 'CAPEITEM'],
    ['방패', 'OFF_SHIELD'],
    ['횃불', 'OFF_TORCH'],
    ['책', 'OFF_BOOK']
  ],
  mount: [
    ['말', 'MOUNT_HORSE'],
    ['갑옷 말', 'MOUNT_ARMORED_HORSE'],
    ['소', 'MOUNT_OX'],
    ['당나귀', 'MOUNT_MULE'],
    ['늑대', 'MOUNT_DIREWOLF'],
    ['곰', 'MOUNT_DIREBEAR'],
    ['매머드', 'MOUNT_MAMMOTH'],
    ['늪지 드래곤', 'MOUNT_SWAMPDRAGON'],
    ['사슴', 'MOUNT_STAG']
  ],
  resource: [
    ['광석', 'ORE'],
    ['금속 주괴', 'METALBAR'],
    ['나무', 'WOOD'],
    ['목재 판자', 'PLANKS'],
    ['가죽 원재료', 'HIDE'],
    ['가죽', 'LEATHER'],
    ['섬유', 'FIBER'],
    ['천', 'CLOTH'],
    ['돌', 'ROCK'],
    ['돌 블록', 'STONEBLOCK']
  ],
  consumable: [
    ['체력 포션', 'POTION_HEAL'],
    ['에너지 포션', 'POTION_ENERGY'],
    ['집중 포션', 'POTION_FOCUS'],
    ['스튜', 'MEAL_STEW'],
    ['샌드위치', 'MEAL_SANDWICH'],
    ['샐러드', 'MEAL_SALAD'],
    ['파이', 'MEAL_PIE'],
    ['수프', 'MEAL_SOUP'],
    ['오믈렛', 'MEAL_OMELETTE']
  ]
};

const TIERS = ['T3', 'T4', 'T5', 'T6', 'T7', 'T8'];

const categoryGrid = document.getElementById('category-grid');
const subcategoryPanel = document.getElementById('subcategory-panel');
const subcategoryGrid = document.getElementById('subcategory-grid');
const subcategoryTitle = document.getElementById('subcategory-title');
const tierPanel = document.getElementById('tier-panel');
const tierTitle = document.getElementById('tier-title');
const tierGrid = document.getElementById('tier-grid');

let currentPattern = '';

function renderCategories() {
  categoryGrid.innerHTML = '';
  Object.entries(CATEGORIES).forEach(([catId, catName]) => {
    const card = document.createElement('div');
    card.className = 'category-card';
    card.dataset.category = catId;

    const name = document.createElement('span');
    name.className = 'category-card-name';
    name.textContent = catName;

    const count = document.createElement('span');
    count.className = 'category-card-count';
    count.textContent = `${(SUBCATEGORIES[catId] || []).length}개`;

    card.appendChild(name);
    card.appendChild(count);
    categoryGrid.appendChild(card);
  });
}

function showSubcategories(catId, catName) {
  categoryGrid.style.display = 'none';
  tierPanel.style.display = 'none';
  subcategoryPanel.style.display = 'block';
  subcategoryTitle.textContent = catName;

  const subs = SUBCATEGORIES[catId] || [];
  subcategoryGrid.innerHTML = '';
  subs.forEach(([name, pattern]) => {
    const div = document.createElement('div');
    div.className = 'subcategory-card';
    div.dataset.pattern = pattern;
    div.textContent = name;
    subcategoryGrid.appendChild(div);
  });
}

function showTierSelect(name) {
  subcategoryPanel.style.display = 'none';
  tierPanel.style.display = 'block';
  tierTitle.textContent = `${name} - 티어 선택`;

  tierGrid.innerHTML = '';
  TIERS.forEach(tier => {
    const card = document.createElement('a');
    card.className = 'tier-card';
    card.dataset.tier = tier;
    card.href = `/prices.html?item=${encodeURIComponent(`${tier}_${currentPattern}`)}`;

    const span = document.createElement('span');
    span.className = 'tier-name';
    span.textContent = tier;

    card.appendChild(span);
    tierGrid.appendChild(card);
  });
}

categoryGrid.addEventListener('click', function(e) {
  const card = e.target.closest('.category-card');
  if (!card) return;
  const catId = card.dataset.category;
  const catName = CATEGORIES[catId];
  showSubcategories(catId, catName);
});

subcategoryGrid.addEventListener('click', function(e) {
  const card = e.target.closest('.subcategory-card');
  if (!card) return;
  currentPattern = card.dataset.pattern;
  const name = card.textContent;
  showTierSelect(name);
});

renderCategories();

const backToCategories = document.getElementById('back-to-categories');
const backToSubcategories = document.getElementById('back-to-subcategories');

backToCategories.addEventListener('click', function() {
  subcategoryPanel.style.display = 'none';
  tierPanel.style.display = 'none';
  categoryGrid.style.display = 'grid';
});

backToSubcategories.addEventListener('click', function() {
  tierPanel.style.display = 'none';
  subcategoryPanel.style.display = 'block';
});

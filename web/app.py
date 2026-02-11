"""알비온 온라인 시세 웹앱 - Flask 메인"""

import sys
import os
import time
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify
from items import search_items, resolve_item, ID_TO_NAME
from config import API_BASE_URL, CITIES, CITY_NAMES_KR
from categories import CATEGORIES, SUBCATEGORIES, TIERS

app = Flask(__name__)

_cache: dict[str, tuple[float, any]] = {}

CACHE_TTL = {
    "prices": 180,
    "gold": 300,
    "history": 600,
}


def cache_get(key: str) -> any:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL.get(key.split(":")[0], 300):
            return data
        del _cache[key]
    return None


def cache_set(key: str, data: any):
    _cache[key] = (time.time(), data)


ICON_BASE = "https://render.albiononline.com/v1/item"


def item_icon_url(item_id: str, size: int = 128) -> str:
    return f"{ICON_BASE}/{item_id}.png?size={size}&quality=1"


POPULAR_ITEMS = [
    "T4_BAG", "T5_BAG", "T6_BAG",
    "T4_POTION_HEAL", "T6_POTION_HEAL",
    "T4_POTION_ENERGY", "T6_POTION_ENERGY",
    "T3_MOUNT_HORSE", "T5_MOUNT_ARMORED_HORSE", "T3_MOUNT_OX",
    "T4_MAIN_SWORD", "T4_2H_BOW", "T4_MAIN_FIRESTAFF",
    "T4_HEAD_PLATE_SET1", "T4_ARMOR_PLATE_SET1", "T4_SHOES_PLATE_SET1",
    "T4_HEAD_LEATHER_SET1", "T4_ARMOR_LEATHER_SET1",
    "T4_HEAD_CLOTH_SET1", "T4_ARMOR_CLOTH_SET1",
    "T4_CAPEITEM_HERETIC",
]


@app.route("/")
def index():
    popular = []
    for item_id in POPULAR_ITEMS:
        name = ID_TO_NAME.get(item_id, item_id)
        popular.append({
            "id": item_id,
            "name": name,
            "icon": item_icon_url(item_id, 128),
        })
    return render_template("index.html", popular_items=popular)


@app.route("/prices/<item_id>")
def prices(item_id):
    item_id = item_id.upper()
    name = ID_TO_NAME.get(item_id, item_id)
    return render_template(
        "prices.html",
        item_id=item_id,
        item_name=name,
        icon_url=item_icon_url(item_id, 128),
        cities=CITIES,
        city_names_kr=CITY_NAMES_KR,
    )


@app.route("/gold")
def gold():
    return render_template("gold.html")


@app.route("/categories")
def categories():
    return render_template(
        "categories.html",
        categories=CATEGORIES,
        subcategories=SUBCATEGORIES,
        tiers=TIERS,
    )


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if len(q) < 1:
        return jsonify([])

    results = search_items(q, limit=15)
    return jsonify([
        {
            "name": name,
            "id": item_id,
            "icon": item_icon_url(item_id, 64),
        }
        for name, item_id in results
    ])


@app.route("/api/prices/<item_id>")
def api_prices(item_id):
    item_id = item_id.upper()
    cache_key = f"prices:{item_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    locations_param = ",".join(CITIES)
    url = f"{API_BASE_URL}/api/v2/stats/prices/{item_id}?locations={locations_param}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        data = []

    cache_set(cache_key, data)
    return jsonify(data)


@app.route("/api/gold")
def api_gold():
    count = request.args.get("count", "72", type=str)
    cache_key = f"gold:{count}"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    url = f"{API_BASE_URL}/api/v2/stats/gold?count={count}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        data = []

    cache_set(cache_key, data)
    return jsonify(data)


@app.route("/api/history/<item_id>")
def api_history(item_id):
    item_id = item_id.upper()
    location = request.args.get("location", "Caerleon")
    time_scale = request.args.get("time_scale", "6")
    cache_key = f"history:{item_id}:{location}:{time_scale}"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    url = (
        f"{API_BASE_URL}/api/v2/stats/history/{item_id}"
        f"?locations={location}&time-scale={time_scale}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        data = []

    cache_set(cache_key, data)
    return jsonify(data)


@app.route("/api/resolve")
def api_resolve():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"id": None})
    item_id = resolve_item(q)
    return jsonify({"id": item_id})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

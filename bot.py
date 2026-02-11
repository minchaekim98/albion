"""알비온 온라인 디스코드 시세 봇"""

import os
from datetime import datetime, timezone

import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv

from api import fetch_gold, fetch_history, fetch_prices
from categories import CATEGORIES, SUBCATEGORIES, TIERS
from config import CITIES, CITY_NAMES_KR, EMBED_COLOR
from items import ID_TO_NAME, ITEM_DB, resolve_item, search_items

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 아이템 아이콘 URL (Albion Online Render API)
ITEM_ICON_URL = "https://render.albiononline.com/v1/item/{item_id}.png?size=64"

# 도시별 이모지
CITY_EMOJI = {
    "카를레온": "🟡",
    "브릿지워치": "🟠",
    "포트스털링": "⚪",
    "림허스트": "🟢",
    "마트락": "🔵",
    "뎃포드": "🟣",
    "브레실리엔": "🌿",
}


class AlbionBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.session: aiohttp.ClientSession | None = None
        self._synced = False

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

    async def on_ready(self):
        if not self._synced:
            for guild in self.guilds:
                try:
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync(guild=guild)
                except Exception:
                    pass
            self._synced = True
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="albion | /sise",
            )
        )

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()


bot = AlbionBot()


def format_price(price: int) -> str:
    """가격을 보기 좋게 포맷팅한다."""
    if price >= 1_000_000:
        return f"{price / 1_000_000:.1f}M"
    if price >= 1_000:
        return f"{price / 1_000:.1f}K"
    return str(price)


def make_bar(value: int, max_value: int, length: int = 12) -> str:
    """텍스트 프로그레스 바를 만든다."""
    if max_value == 0:
        return "░" * length
    filled = round(value / max_value * length)
    filled = min(filled, length)
    return "█" * filled + "░" * (length - filled)


# ──────────────────────────────────────────────
# /시세 [아이템명]
# ──────────────────────────────────────────────
@bot.tree.command(name="시세", description="아이템의 전 도시 매매 가격을 조회합니다")
@app_commands.describe(아이템="아이템 이름 또는 ID (예: T4 가방, T4_BAG)")
async def cmd_price(interaction: discord.Interaction, 아이템: str):
    item_id = resolve_item(아이템)
    if not item_id:
        await interaction.response.send_message(
            f"**`{아이템}`** 에 해당하는 아이템을 찾을 수 없습니다.\n"
            f"`/검색 {아이템}` 으로 아이템을 검색해보세요.",
            ephemeral=True,
        )
        return

    await interaction.response.defer()

    data = await fetch_prices(bot.session, item_id)
    if not data:
        await interaction.followup.send("시세 데이터를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.")
        return

    display_name = ID_TO_NAME.get(item_id, item_id)

    # 도시별 가격 정리
    sell_data = []  # (도시한글명, 가격)
    buy_data = []   # (도시한글명, 가격)

    for entry in data:
        city = entry.get("city", "Unknown")
        city_kr = CITY_NAMES_KR.get(city, city)
        sell_min = entry.get("sell_price_min", 0)
        buy_max = entry.get("buy_price_max", 0)

        if sell_min > 0:
            sell_data.append((city_kr, sell_min))
        if buy_max > 0:
            buy_data.append((city_kr, buy_max))

    sell_data.sort(key=lambda x: x[1])
    buy_data.sort(key=lambda x: x[1], reverse=True)

    # ── 임베드 구성 ──
    embed = discord.Embed(color=EMBED_COLOR, timestamp=datetime.now(timezone.utc))
    embed.set_author(
        name=f"{display_name}",
        icon_url=ITEM_ICON_URL.format(item_id=item_id),
    )
    embed.set_thumbnail(url=ITEM_ICON_URL.format(item_id=item_id))

    # 판매 최저가
    if sell_data:
        max_sell = sell_data[-1][1]
        lines = []
        for i, (city, price) in enumerate(sell_data):
            emoji = CITY_EMOJI.get(city, "⚪")
            bar = make_bar(price, max_sell)
            tag = " ← **최저**" if i == 0 else ""
            lines.append(f"{emoji} {city:<6} `{bar}` **{price:>10,}**{tag}")
        embed.add_field(
            name="💰 판매 최저가 (Sell Order)",
            value="\n".join(lines),
            inline=False,
        )
    else:
        embed.add_field(name="💰 판매 최저가", value="```등록된 판매 주문 없음```", inline=False)

    # 구매 최고가
    if buy_data:
        max_buy = buy_data[0][1]
        lines = []
        for i, (city, price) in enumerate(buy_data):
            emoji = CITY_EMOJI.get(city, "⚪")
            bar = make_bar(price, max_buy)
            tag = " ← **최고**" if i == 0 else ""
            lines.append(f"{emoji} {city:<6} `{bar}` **{price:>10,}**{tag}")
        embed.add_field(
            name="🛒 구매 최고가 (Buy Order)",
            value="\n".join(lines),
            inline=False,
        )
    else:
        embed.add_field(name="🛒 구매 최고가", value="```등록된 구매 주문 없음```", inline=False)

    # 하단 요약
    summary_parts = []
    if sell_data:
        summary_parts.append(f"최저 판매 **{sell_data[0][0]}** {sell_data[0][1]:,}")
    if buy_data:
        summary_parts.append(f"최고 구매 **{buy_data[0][0]}** {buy_data[0][1]:,}")
    if sell_data and buy_data:
        diff = sell_data[0][1] - buy_data[0][1]
        if diff > 0:
            summary_parts.append(f"차익 **{diff:,}**")
        else:
            summary_parts.append(f"역마진 **{abs(diff):,}**")

    if summary_parts:
        embed.add_field(name="📋 요약", value=" ・ ".join(summary_parts), inline=False)

    embed.set_footer(text=f"아이템 ID: {item_id}  •  Albion Online Data Project")
    await interaction.followup.send(embed=embed)


# ──────────────────────────────────────────────
# /골드
# ──────────────────────────────────────────────
@bot.tree.command(name="골드", description="현재 골드-실버 시세를 조회합니다")
async def cmd_gold(interaction: discord.Interaction):
    await interaction.response.defer()

    data = await fetch_gold(bot.session, count=24)
    if not data:
        await interaction.followup.send("골드 시세 데이터를 가져올 수 없습니다.")
        return

    prices = [e.get("price", 0) for e in data if e.get("price", 0) > 0]
    timestamps = [e.get("timestamp", "") for e in data if e.get("price", 0) > 0]

    if not prices:
        await interaction.followup.send("골드 시세 데이터가 비어있습니다.")
        return

    current = prices[-1]
    high = max(prices)
    low = min(prices)

    embed = discord.Embed(color=0xFFD700, timestamp=datetime.now(timezone.utc))
    embed.set_author(name="골드 시세", icon_url="https://render.albiononline.com/v1/item/GOLD_BAR.png?size=64")

    # 현재가 크게 표시
    embed.description = f"## 1 골드 = {current:,} 실버"

    # 변동률
    if len(prices) >= 2:
        old = prices[0]
        if old > 0:
            change = current - old
            pct = (change / old) * 100
            if change > 0:
                embed.add_field(name="변동", value=f"📈 +{change:,} (+{pct:.1f}%)", inline=True)
            elif change < 0:
                embed.add_field(name="변동", value=f"📉 {change:,} ({pct:.1f}%)", inline=True)
            else:
                embed.add_field(name="변동", value="➡️ 변동 없음", inline=True)

    embed.add_field(name="최고", value=f"{high:,}", inline=True)
    embed.add_field(name="최저", value=f"{low:,}", inline=True)

    # 추이 (최근 12개 포인트)
    recent = prices[-12:]
    recent_ts = timestamps[-12:]
    if len(recent) >= 3:
        r_min = min(recent)
        r_max = max(recent)
        r_range = r_max - r_min if r_max != r_min else 1

        lines = []
        step = max(1, len(recent) // 8)
        for i in range(0, len(recent), step):
            p = recent[i]
            bar = make_bar(p - r_min, r_range, 15)
            ts = recent_ts[i][11:16] if len(recent_ts[i]) > 15 else "?"
            lines.append(f"`{ts}` `{bar}` {p:,}")

        # 항상 마지막 값 포함
        if (len(recent) - 1) % step != 0:
            p = recent[-1]
            bar = make_bar(p - r_min, r_range, 15)
            ts = recent_ts[-1][11:16] if len(recent_ts[-1]) > 15 else "?"
            lines.append(f"`{ts}` `{bar}` {p:,}")

        embed.add_field(name="최근 추이", value="\n".join(lines), inline=False)

    embed.set_footer(text="Albion Online Data Project")
    await interaction.followup.send(embed=embed)


# ──────────────────────────────────────────────
# /히스토리 [아이템명] [도시]
# ──────────────────────────────────────────────
@bot.tree.command(name="히스토리", description="아이템의 최근 7일 가격 히스토리를 조회합니다")
@app_commands.describe(아이템="아이템 이름 또는 ID", 도시="도시 이름 (기본: Caerleon)")
@app_commands.choices(
    도시=[app_commands.Choice(name=f"{CITY_NAMES_KR[c]} ({c})", value=c) for c in CITIES]
)
async def cmd_history(interaction: discord.Interaction, 아이템: str, 도시: str = "Caerleon"):
    item_id = resolve_item(아이템)
    if not item_id:
        await interaction.response.send_message(
            f"**`{아이템}`** 에 해당하는 아이템을 찾을 수 없습니다.",
            ephemeral=True,
        )
        return

    await interaction.response.defer()

    data = await fetch_history(bot.session, item_id, 도시)
    if not data:
        await interaction.followup.send("히스토리 데이터를 가져올 수 없습니다.")
        return

    display_name = ID_TO_NAME.get(item_id, item_id)
    city_kr = CITY_NAMES_KR.get(도시, 도시)
    city_emoji = CITY_EMOJI.get(city_kr, "⚪")

    # 히스토리 파싱
    entries = []
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict) and "data" in first:
            entries = first["data"]
        elif isinstance(first, dict) and "avg_price" in first:
            entries = data

    if not entries:
        await interaction.followup.send("해당 기간의 히스토리 데이터가 없습니다.")
        return

    recent = entries[-7:] if len(entries) > 7 else entries

    dates = []
    avg_prices = []
    counts = []
    for e in recent:
        avg = e.get("avg_price", 0)
        ts = e.get("timestamp", "")
        cnt = e.get("item_count", 0)
        if avg > 0:
            dates.append(ts[:10] if ts else "?")
            avg_prices.append(avg)
            counts.append(cnt)

    if not avg_prices:
        await interaction.followup.send("해당 기간에 거래 기록이 없습니다.")
        return

    p_min = min(avg_prices)
    p_max = max(avg_prices)
    p_range = p_max - p_min if p_max != p_min else 1
    p_avg = sum(avg_prices) / len(avg_prices)

    embed = discord.Embed(color=EMBED_COLOR, timestamp=datetime.now(timezone.utc))
    embed.set_author(
        name=f"{display_name} - {city_emoji} {city_kr}",
        icon_url=ITEM_ICON_URL.format(item_id=item_id),
    )
    embed.set_thumbnail(url=ITEM_ICON_URL.format(item_id=item_id))

    # 가격 변동
    if len(avg_prices) >= 2:
        change = avg_prices[-1] - avg_prices[0]
        pct = (change / avg_prices[0]) * 100 if avg_prices[0] > 0 else 0
        arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        embed.description = f"{arrow} 7일간 **{change:+,.0f}** ({pct:+.1f}%)"

    # 일별 데이터
    lines = []
    for i, (date, price, count) in enumerate(zip(dates, avg_prices, counts)):
        bar = make_bar(price - p_min, p_range, 10)
        # 날짜에서 월-일만 표시
        short_date = date[5:] if len(date) >= 10 else date
        lines.append(f"`{short_date}` `{bar}` **{price:>10,.0f}** ({count:,}개)")

    embed.add_field(name="일별 평균가", value="\n".join(lines), inline=False)

    # 통계
    embed.add_field(name="평균", value=f"**{p_avg:,.0f}**", inline=True)
    embed.add_field(name="최고", value=f"**{p_max:,.0f}**", inline=True)
    embed.add_field(name="최저", value=f"**{p_min:,.0f}**", inline=True)

    embed.set_footer(text=f"{item_id}  •  Albion Online Data Project")
    await interaction.followup.send(embed=embed)


# ──────────────────────────────────────────────
# /검색 [키워드]
# ──────────────────────────────────────────────
@bot.tree.command(name="검색", description="아이템을 키워드로 검색합니다")
@app_commands.describe(키워드="검색할 아이템 키워드 (한글 또는 영문)")
async def cmd_search(interaction: discord.Interaction, 키워드: str):
    results = search_items(키워드)

    if not results:
        await interaction.response.send_message(
            f"**`{키워드}`** 에 해당하는 아이템을 찾을 수 없습니다.\n"
            "영문 아이템 ID를 직접 입력할 수도 있습니다. (예: `T4_BAG`)",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title=f"\"{키워드}\" 검색 결과",
        color=EMBED_COLOR,
    )

    lines = []
    for name, item_id in results[:15]:
        lines.append(f"`{item_id}` — {name}")

    embed.description = "\n".join(lines)
    embed.add_field(
        name="",
        value="위 ID를 `/시세` 또는 `/히스토리` 에서 사용하세요.",
        inline=False,
    )

    count_text = f"총 {len(results)}개 결과"
    if len(results) > 15:
        count_text += " (15개만 표시)"
    embed.set_footer(text=count_text)

    await interaction.response.send_message(embed=embed)


# ──────────────────────────────────────────────
# /찾기 - 카테고리 드롭다운 브라우저
# ──────────────────────────────────────────────
class CategorySelect(discord.ui.Select):
    """대분류 카테고리 선택 드롭다운."""

    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=key, emoji=emoji)
            for key, name, emoji in [
                ("weapon_melee", "근접 무기", "⚔️"),
                ("weapon_ranged", "원거리 무기", "🏹"),
                ("weapon_magic", "마법 무기", "🪄"),
                ("armor", "방어구", "🛡️"),
                ("accessory", "악세서리", "👜"),
                ("mount", "탈것", "🐴"),
                ("resource", "자원", "🪨"),
                ("consumable", "소모품", "🧪"),
            ]
        ]
        super().__init__(placeholder="카테고리를 선택하세요", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_key = self.values[0]
        category_name = CATEGORIES[category_key]
        subcats = SUBCATEGORIES.get(category_key, [])

        if not subcats:
            await interaction.response.send_message("해당 카테고리에 아이템이 없습니다.", ephemeral=True)
            return

        view = SubcategoryView(category_key, category_name, subcats)
        embed = discord.Embed(
            title=f"📂 {category_name}",
            description="세부 종류를 선택하세요.",
            color=EMBED_COLOR,
        )
        await interaction.response.edit_message(embed=embed, view=view)


class CategoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(CategorySelect())


class SubcategorySelect(discord.ui.Select):
    """소분류 선택 드롭다운."""

    def __init__(self, category_key: str, category_name: str, subcats: list[tuple[str, str]]):
        self.category_key = category_key
        self.category_name = category_name
        self.subcats = subcats
        options = [
            discord.SelectOption(label=name, value=pattern)
            for name, pattern in subcats[:25]
        ]
        super().__init__(placeholder="종류를 선택하세요", options=options)

    async def callback(self, interaction: discord.Interaction):
        pattern = self.values[0]
        # 선택된 소분류의 한글명 찾기
        subcat_name = pattern
        for name, pat in self.subcats:
            if pat == pattern:
                subcat_name = name
                break

        view = TierView(self.category_name, subcat_name, pattern)
        embed = discord.Embed(
            title=f"📂 {self.category_name} > {subcat_name}",
            description="티어를 선택하세요.",
            color=EMBED_COLOR,
        )
        await interaction.response.edit_message(embed=embed, view=view)


class SubcategoryView(discord.ui.View):
    def __init__(self, category_key: str, category_name: str, subcats: list[tuple[str, str]]):
        super().__init__(timeout=120)
        self.add_item(SubcategorySelect(category_key, category_name, subcats))


class TierSelect(discord.ui.Select):
    """티어 선택 드롭다운."""

    def __init__(self, category_name: str, subcat_name: str, pattern: str):
        self.category_name = category_name
        self.subcat_name = subcat_name
        self.pattern = pattern
        options = [
            discord.SelectOption(label=f"T{t} ({desc})", value=f"T{t}")
            for t, desc in [
                ("3", "장인"), ("4", "숙련자"), ("5", "전문가"),
                ("6", "마스터"), ("7", "그랜드마스터"), ("8", "장로"),
            ]
        ]
        super().__init__(placeholder="티어를 선택하세요", options=options)

    async def callback(self, interaction: discord.Interaction):
        tier = self.values[0]
        item_id = f"{tier}_{self.pattern}"

        display_name = ID_TO_NAME.get(item_id, item_id)

        # 시세 조회
        await interaction.response.defer()
        data = await fetch_prices(bot.session, item_id)

        if not data:
            await interaction.followup.send(
                f"`{display_name}` ({item_id})의 시세 데이터가 없습니다.",
                ephemeral=True,
            )
            return

        # 시세 임베드 (cmd_price와 동일한 포맷)
        sell_data = []
        buy_data = []
        for entry in data:
            city = entry.get("city", "Unknown")
            city_kr = CITY_NAMES_KR.get(city, city)
            sell_min = entry.get("sell_price_min", 0)
            buy_max = entry.get("buy_price_max", 0)
            if sell_min > 0:
                sell_data.append((city_kr, sell_min))
            if buy_max > 0:
                buy_data.append((city_kr, buy_max))

        sell_data.sort(key=lambda x: x[1])
        buy_data.sort(key=lambda x: x[1], reverse=True)

        embed = discord.Embed(color=EMBED_COLOR, timestamp=datetime.now(timezone.utc))
        embed.set_author(name=display_name, icon_url=ITEM_ICON_URL.format(item_id=item_id))
        embed.set_thumbnail(url=ITEM_ICON_URL.format(item_id=item_id))

        if sell_data:
            max_sell = sell_data[-1][1]
            lines = []
            for i, (city, price) in enumerate(sell_data):
                emoji = CITY_EMOJI.get(city, "⚪")
                bar = make_bar(price, max_sell)
                tag = " ← **최저**" if i == 0 else ""
                lines.append(f"{emoji} {city:<6} `{bar}` **{price:>10,}**{tag}")
            embed.add_field(name="💰 판매 최저가", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="💰 판매 최저가", value="```등록된 판매 주문 없음```", inline=False)

        if buy_data:
            max_buy = buy_data[0][1]
            lines = []
            for i, (city, price) in enumerate(buy_data):
                emoji = CITY_EMOJI.get(city, "⚪")
                bar = make_bar(price, max_buy)
                tag = " ← **최고**" if i == 0 else ""
                lines.append(f"{emoji} {city:<6} `{bar}` **{price:>10,}**{tag}")
            embed.add_field(name="🛒 구매 최고가", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="🛒 구매 최고가", value="```등록된 구매 주문 없음```", inline=False)

        summary_parts = []
        if sell_data:
            summary_parts.append(f"최저 판매 **{sell_data[0][0]}** {sell_data[0][1]:,}")
        if buy_data:
            summary_parts.append(f"최고 구매 **{buy_data[0][0]}** {buy_data[0][1]:,}")
        if sell_data and buy_data:
            diff = sell_data[0][1] - buy_data[0][1]
            if diff > 0:
                summary_parts.append(f"차익 **{diff:,}**")
            else:
                summary_parts.append(f"역마진 **{abs(diff):,}**")
        if summary_parts:
            embed.add_field(name="📋 요약", value=" ・ ".join(summary_parts), inline=False)

        embed.set_footer(text=f"아이템 ID: {item_id}  •  Albion Online Data Project")
        await interaction.followup.send(embed=embed)


class TierView(discord.ui.View):
    def __init__(self, category_name: str, subcat_name: str, pattern: str):
        super().__init__(timeout=120)
        self.add_item(TierSelect(category_name, subcat_name, pattern))


@bot.tree.command(name="찾기", description="카테고리에서 아이템을 찾아 시세를 조회합니다")
async def cmd_browse(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔎 아이템 찾기",
        description="카테고리를 선택하면 세부 종류 → 티어 순서로 아이템을 찾을 수 있습니다.",
        color=EMBED_COLOR,
    )
    view = CategoryView()
    await interaction.response.send_message(embed=embed, view=view)


# ──────────────────────────────────────────────
# 실행
# ──────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        print("DISCORD_TOKEN is not set in .env file.")
    else:
        bot.run(TOKEN)

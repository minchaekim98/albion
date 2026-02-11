"""시세 차트 이미지 생성 모듈"""

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정 (맑은 고딕)
FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
font_prop = fm.FontProperties(fname=FONT_PATH)

# 도시별 색상
CITY_COLORS = {
    "카를레온": "#D4A017",
    "브릿지워치": "#E87511",
    "포트스털링": "#A0A0A0",
    "림허스트": "#228B22",
    "마트락": "#4169E1",
    "뎃포드": "#800080",
    "브레실리엔": "#2E8B57",
}

DEFAULT_COLOR = "#888888"


def create_price_chart(item_name: str, sell_data: list, buy_data: list) -> io.BytesIO:
    """도시별 판매가/구매가 수평 바 차트를 생성한다.

    Args:
        item_name: 아이템 표시 이름
        sell_data: [(도시한글명, 가격), ...] 리스트 (최저가 순)
        buy_data: [(도시한글명, 가격), ...] 리스트 (최고가 순)

    Returns:
        PNG 이미지 BytesIO 버퍼
    """
    has_sell = len(sell_data) > 0
    has_buy = len(buy_data) > 0
    num_plots = has_sell + has_buy

    if num_plots == 0:
        return _create_no_data_chart(item_name)

    fig, axes = plt.subplots(1, num_plots, figsize=(8, max(3, len(sell_data or buy_data) * 0.7 + 1.5)))
    fig.patch.set_facecolor("#2C2F33")

    if num_plots == 1:
        axes = [axes]

    plot_idx = 0

    # 판매 최저가 차트
    if has_sell:
        ax = axes[plot_idx]
        plot_idx += 1
        cities = [d[0] for d in sell_data]
        prices = [d[1] for d in sell_data]
        colors = [CITY_COLORS.get(c, DEFAULT_COLOR) for c in cities]

        bars = ax.barh(cities, prices, color=colors, edgecolor="#40444B", linewidth=0.5)
        ax.set_title("Sell (lowest)", fontproperties=font_prop, color="white", fontsize=13, pad=10)

        # 최저가 강조
        if len(bars) > 0:
            bars[0].set_edgecolor("#00FF00")
            bars[0].set_linewidth(2)

        _style_axis(ax, prices)

    # 구매 최고가 차트
    if has_buy:
        ax = axes[plot_idx]
        cities = [d[0] for d in buy_data]
        prices = [d[1] for d in buy_data]
        colors = [CITY_COLORS.get(c, DEFAULT_COLOR) for c in cities]

        bars = ax.barh(cities, prices, color=colors, edgecolor="#40444B", linewidth=0.5)
        ax.set_title("Buy (highest)", fontproperties=font_prop, color="white", fontsize=13, pad=10)

        # 최고가 강조
        if len(bars) > 0:
            bars[0].set_edgecolor("#00FF00")
            bars[0].set_linewidth(2)

        _style_axis(ax, prices)

    fig.suptitle(item_name, fontproperties=font_prop, color="white", fontsize=16, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.93])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _style_axis(ax, prices):
    """차트 축 스타일 적용"""
    ax.set_facecolor("#36393F")
    ax.tick_params(colors="white", labelsize=10)
    ax.xaxis.label.set_color("white")

    for label in ax.get_yticklabels():
        label.set_fontproperties(font_prop)
        label.set_color("white")

    # 바 위에 가격 표시
    for i, (price, bar) in enumerate(zip(prices, ax.patches)):
        ax.text(
            bar.get_width() + max(prices) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{price:,}",
            va="center",
            color="white",
            fontsize=9,
            fontproperties=font_prop,
        )

    ax.set_xlim(0, max(prices) * 1.25 if prices else 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#40444B")
    ax.spines["left"].set_color("#40444B")
    ax.tick_params(axis="x", colors="#72767D")
    ax.invert_yaxis()


def _create_no_data_chart(item_name: str) -> io.BytesIO:
    """데이터 없음 차트"""
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("#2C2F33")
    ax.set_facecolor("#36393F")
    ax.text(0.5, 0.5, "No data", ha="center", va="center", color="white", fontsize=16, fontproperties=font_prop)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.suptitle(item_name, fontproperties=font_prop, color="white", fontsize=16)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


def create_gold_chart(prices: list[int], timestamps: list[str]) -> io.BytesIO:
    """골드 시세 라인 차트를 생성한다.

    Args:
        prices: 가격 리스트
        timestamps: 타임스탬프 리스트

    Returns:
        PNG 이미지 BytesIO 버퍼
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#2C2F33")
    ax.set_facecolor("#36393F")

    x = range(len(prices))
    ax.plot(x, prices, color="#FFD700", linewidth=2, marker="o", markersize=4)
    ax.fill_between(x, prices, alpha=0.15, color="#FFD700")

    # 최고/최저 표시
    max_idx = prices.index(max(prices))
    min_idx = prices.index(min(prices))
    ax.annotate(f"{max(prices):,}", xy=(max_idx, max(prices)), color="#00FF00",
                fontsize=9, fontproperties=font_prop, ha="center",
                xytext=(0, 10), textcoords="offset points")
    ax.annotate(f"{min(prices):,}", xy=(min_idx, min(prices)), color="#FF4444",
                fontsize=9, fontproperties=font_prop, ha="center",
                xytext=(0, -15), textcoords="offset points")

    ax.set_title("Gold Price", fontproperties=font_prop, color="white", fontsize=15, pad=10)
    ax.tick_params(colors="#72767D", labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#40444B")
    ax.spines["left"].set_color("#40444B")
    ax.grid(axis="y", color="#40444B", alpha=0.3)

    # x축 라벨 (시간)
    if timestamps:
        step = max(1, len(timestamps) // 6)
        tick_positions = list(range(0, len(timestamps), step))
        tick_labels = [timestamps[i][11:16] if len(timestamps[i]) > 15 else timestamps[i][:10] for i in tick_positions]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, color="#72767D", fontsize=8)

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def create_history_chart(item_name: str, city_name: str, dates: list[str], avg_prices: list[float]) -> io.BytesIO:
    """히스토리 라인 차트를 생성한다.

    Args:
        item_name: 아이템 표시 이름
        city_name: 도시 한글명
        dates: 날짜 리스트
        avg_prices: 평균 가격 리스트

    Returns:
        PNG 이미지 BytesIO 버퍼
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#2C2F33")
    ax.set_facecolor("#36393F")

    x = range(len(avg_prices))
    ax.plot(x, avg_prices, color="#00BFFF", linewidth=2, marker="s", markersize=5)
    ax.fill_between(x, avg_prices, alpha=0.1, color="#00BFFF")

    # 각 포인트에 가격 표시
    for i, price in enumerate(avg_prices):
        ax.annotate(f"{price:,.0f}", xy=(i, price), color="white",
                    fontsize=8, fontproperties=font_prop, ha="center",
                    xytext=(0, 10), textcoords="offset points")

    ax.set_title(f"{item_name} - {city_name}", fontproperties=font_prop, color="white", fontsize=14, pad=10)
    ax.tick_params(colors="#72767D", labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#40444B")
    ax.spines["left"].set_color("#40444B")
    ax.grid(axis="y", color="#40444B", alpha=0.3)

    # x축 날짜 라벨
    if dates:
        ax.set_xticks(list(x))
        short_dates = [d[5:10] if len(d) >= 10 else d for d in dates]
        ax.set_xticklabels(short_dates, color="#72767D", fontsize=8, rotation=30)

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

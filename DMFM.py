import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from datetime import datetime, date
from vnstock import Quote, Listing
from dotenv import load_dotenv
from supabase import create_client, Client

# ============================================================
# TẢI BIẾN MÔI TRƯỜNG & KHỞI TẠO SUPABASE
# ============================================================
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ============================================================
# CẤU HÌNH TRANG
# ============================================================
st.set_page_config(
    page_title="Danh Mục Đầu Tư - KAFI SAIGON",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# CSS GIAO DIỆN DARK THEME + GLASSMORPHISM
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* ===== TOÀN BỘ TRANG ===== */
    .stApp {
        background: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }

    /* ===== HEADER ===== */
    .main-header {
        text-align: center;
        padding: 5px 0 20px 0;
        animation: fadeInUp 0.5s ease-out;
        position: relative;
    }
    .main-header .logo-img {
        position: absolute;
        left: 0;
        top: -10px;
        height: 120px;
    }
    .main-header h1 {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00897B 0%, #26A69A 40%, #4DB6AC 70%, #00897B 100%);
        background-size: 200% auto;
        animation: shimmer 4s linear infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1.5px;
        margin: 0;
    }
    .main-header .sub {
        color: #78909C;
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-top: 6px;
    }
    .main-header .divider {
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, transparent, #00897B, transparent);
        margin: 12px auto 0;
        border-radius: 2px;
    }

    /* ===== TABLE CARD (chứa bảng) ===== */
    .glass-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        padding: 0;
        margin-bottom: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out;
    }

    /* ===== CSS TABS STREAMLIT ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px 8px 0 0;
        padding: 10px 24px;
        color: #78909C;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.02);
        transition: all 0.2s ease-in-out;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00897B;
        background-color: #f9fdf9 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e8f5e9 !important;
        color: #00897B !important;
        border-bottom-color: #00897B !important;
        border-bottom-width: 3px !important;
    }

    /* ===== KPI CARDS ===== */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 30px;
        margin-top: 15px;
        animation: fadeInUp 0.5s ease-out;
    }
    .kpi-card {
        background: linear-gradient(145deg, #00897B 0%, #00796B 100%);
        border: none;
        border-radius: 12px;
        padding: 20px 18px 16px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0,137,123,0.25);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,137,123,0.35);
    }
    .kpi-card .kpi-title-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-bottom: 10px;
    }
    .kpi-card .kpi-icon {
        font-size: 1.1rem;
        line-height: 1;
    }
    .kpi-card .label {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .kpi-card .value {
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1;
    }
    .kpi-card .value.positive { color: #B9F6CA; }
    .kpi-card .value.negative { color: #FF8A80; }
    .kpi-card .value.neutral  { color: #ffffff; }

    /* ===== BẢNG DỮ LIỆU ===== */
    .portfolio-table {
        width: 100%;
        border-collapse: collapse;
    }
    .portfolio-table thead th {
        background: #00796B;
        color: #ffffff;
        font-weight: 700;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding: 18px 16px;
        text-align: center;
        border-bottom: 2px solid #004D40;
    }
    .portfolio-table tbody td {
        padding: 16px 16px;
        color: #37474F;
        font-size: 0.93rem;
        text-align: center;
        border-bottom: 1px solid #f0f0f0;
        font-weight: 500;
    }
    .portfolio-table tbody tr {
        transition: background 0.2s;
    }
    .portfolio-table tbody tr:nth-child(even) {
        background: #f9fdf9;
    }
    .portfolio-table tbody tr:hover {
        background: #e8f5e9;
    }
    .portfolio-table .symbol {
        font-weight: 800;
        color: #00897B;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
    }
    .portfolio-table .profit-positive {
        color: #2E7D32;
        font-weight: 800;
    }
    .portfolio-table .profit-negative {
        color: #D32F2F;
        font-weight: 800;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #00897B 0%, #00796B 100%) !important;
        border-right: none;
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: white;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
    }
    section[data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: rgba(255,255,255,0.9) !important;
    }

    /* ===== FORM INPUTS ===== */
    .stNumberInput input, .stTextInput input, .stDateInput input {
        background: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        color: #37474F !important;
        font-weight: 500 !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus, .stDateInput input:focus {
        border-color: #00897B !important;
        box-shadow: 0 0 8px rgba(0,137,123,0.15) !important;
    }

    /* ===== NÚT BẤM ===== */
    .stButton > button {
        background: linear-gradient(135deg, #00897B 0%, #26A69A 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0,137,123,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,137,123,0.35);
        background: linear-gradient(135deg, #00796B 0%, #00897B 100%);
        color: white;
    }

    /* ===== TIMESTAMP ===== */
    .timestamp {
        text-align: center;
        color: #90A4AE;
        font-size: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.5px;
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid #e0e0e0;
    }

    /* ===== FORM STYLING ===== */
    [data-testid="stForm"] {
        background: #fafafa !important;
        border: 1px solid #eeeeee !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin-top: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02) !important;
        transition: box-shadow 0.3s ease;
    }
    [data-testid="stForm"]:hover {
        box-shadow: 0 8px 24px rgba(0,137,123,0.06) !important;
    }

    /* Ẩn hamburger menu & footer mặc định */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Loại bỏ khoảng trắng thừa của thanh tab */
    .stTabs {
        margin-top: -10px;
    }

    /* ===== RESPONSIVE DESIGN (Điện thoại & Tablet) ===== */
    @media (max-width: 992px) {
        .kpi-row {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem;
        }
        .main-header .sub {
            font-size: 0.75rem;
        }
        .main-header .logo-img {
            position: relative;
            height: 120px;
            display: block;
            margin: 0 auto 12px;
        }
        .kpi-row {
            grid-template-columns: 1fr;
        }
        .portfolio-table {
            display: block;
            overflow-x: auto;
            white-space: nowrap;
        }
        .portfolio-table thead th, .portfolio-table tbody td {
            padding: 10px;
            font-size: 0.85rem;
        }
        .stButton > button {
            padding: 8px 16px;
            font-size: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DỮ LIỆU - LƯU/ĐỌC SUPABASE
# ============================================================

def load_portfolio(tab_id="tab1"):
    """Đọc danh mục từ bảng portfolio trên Supabase."""
    try:
        response = supabase.table("portfolio").select("*").eq("tab_id", tab_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Lỗi đọc Supabase: {e}")
        return []

def save_portfolio_item(data, tab_id="tab1"):
    """Thêm 1 record vào bảng portfolio trên Supabase."""
    data["tab_id"] = tab_id
    supabase.table("portfolio").insert(data).execute()

def update_portfolio_item(item_id, data):
    """Cập nhật 1 record trong bảng portfolio."""
    supabase.table("portfolio").update(data).eq("id", item_id).execute()

def delete_portfolio_item(item_id):
    """Xóa 1 record trong bảng portfolio."""
    supabase.table("portfolio").delete().eq("id", item_id).execute()

# ============================================================
# DỮ LIỆU - VỊ THẾ ĐÃ ĐÓNG (Chốt lời / Cắt lỗ)
# ============================================================

def load_closed(tab_id="tab1"):
    """Đọc danh sách vị thế đã đóng từ Supabase."""
    try:
        response = supabase.table("closed_positions").select("*").eq("tab_id", tab_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Lỗi đọc Supabase: {e}")
        return []

def save_closed_item(data, tab_id="tab1"):
    """Thêm 1 record vào bảng closed_positions trên Supabase."""
    data["tab_id"] = tab_id
    supabase.table("closed_positions").insert(data).execute()

def delete_closed_item(item_id):
    """Xóa 1 record trong bảng closed_positions."""
    supabase.table("closed_positions").delete().eq("id", item_id).execute()


# ============================================================
# LẤY GIÁ THỊ TRƯỜNG TỪ VNSTOCK
# ============================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_market_price(symbol: str) -> float | None:
    """Lấy giá đóng cửa mới nhất của 1 mã cổ phiếu (đơn vị: VND)."""
    try:
        quote = Quote(symbol=symbol)
        df = quote.history(length="1M", interval="1D")
        if df is not None and not df.empty:
            # vnstock trả giá theo đơn vị nghìn VND (VD: 92.6 = 92,600 VND)
            raw_price = float(df["close"].iloc[-1])
            return raw_price * 1000
    except Exception:
        pass
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_industry_map() -> dict:
    """Lấy bảng phân ngành ICB cấp 2 cho tất cả mã CP (cache 1 ngày)."""
    try:
        ls = Listing()
        df = ls.symbols_by_industries()
        if df is not None and not df.empty:
            return dict(zip(df["symbol"], df["industry_name"]))
    except Exception:
        pass
    return {}


# ============================================================
# SESSION STATE KHỞI TẠO MẶC ĐỊNH
# ============================================================
if "portfolio_tab1" not in st.session_state:
    st.session_state.portfolio_tab1 = load_portfolio("tab1")
if "closed_positions_tab1" not in st.session_state:
    st.session_state.closed_positions_tab1 = load_closed("tab1")
if "editing_idx_tab1" not in st.session_state:
    st.session_state.editing_idx_tab1 = None
if "selling_idx_tab1" not in st.session_state:
    st.session_state.selling_idx_tab1 = None

if "portfolio_tab2" not in st.session_state:
    st.session_state.portfolio_tab2 = load_portfolio("tab2")
if "closed_positions_tab2" not in st.session_state:
    st.session_state.closed_positions_tab2 = load_closed("tab2")
if "editing_idx_tab2" not in st.session_state:
    st.session_state.editing_idx_tab2 = None
if "selling_idx_tab2" not in st.session_state:
    st.session_state.selling_idx_tab2 = None


# ============================================================
# HÀM HIỆN NỘI DUNG 1 TAB
# ============================================================
def render_tab_content(tab_id: str, tab_title: str):
    
    # Prefix cho key widget để không bị trùng (ví dụ dropdown)
    k_pfx = tab_id
    
    # Tham chiếu data của tab hiện tại
    portfolio_key = f"portfolio_{tab_id}"
    closed_key = f"closed_positions_{tab_id}"
    edit_key = f"editing_idx_{tab_id}"
    sell_key = f"selling_idx_{tab_id}"

    curr_portfolio = st.session_state[portfolio_key]
    curr_closed = st.session_state[closed_key]

    # Nút trên cùng: Thêm CP + Cập nhật giá
    _, col_add, col_refresh = st.columns([2.5, 1, 1.2])
    with col_add:
        add_clicked = st.button("➕ Thêm cổ phiếu", key=f"add_btn_{k_pfx}", use_container_width=True)
    with col_refresh:
        refresh = st.button("🔄 Cập nhật giá thị trường", key=f"refresh_btn_{k_pfx}", use_container_width=True)

    if refresh:
        st.cache_data.clear()

    # Thêm Header "Báo Cáo Danh Mục Đầu Tư" vào giữa nút và bảng
    LOGO_PATH = Path("D:/Python file/Twise/Logo/logo.png")
    logo_b64 = ""
    if LOGO_PATH.exists():
        logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

    if logo_b64:
        header_html = f"""
        <div class="main-header">
            <img src="data:image/png;base64,{logo_b64}" class="logo-img" alt="KAFI SAIGON">
            <h1>BÁO CÁO DANH MỤC ĐẦU TƯ</h1>
            <div class="sub">{datetime.now().strftime("%d:%m:%Y")}</div>
            <div class="divider"></div>
        </div>
        """
    else:
        header_html = f"""
        <div class="main-header">
            <h1>BÁO CÁO DANH MỤC ĐẦU TƯ</h1>
            <div class="sub">{datetime.now().strftime("%d:%m:%Y")}</div>
            <div class="divider"></div>
        </div>
        """
    st.markdown(header_html, unsafe_allow_html=True)

    @st.dialog(f"➕ Thêm cổ phiếu - {tab_title}")
    def add_stock_dialog():
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            new_symbol = st.text_input("Mã CP", placeholder="VD: FPT", key=f"new_sym_{k_pfx}").upper().strip()
        with col_s2:
            new_date = st.date_input("Ngày mua lần 1", value=date.today(), format="DD/MM/YYYY", key=f"new_date1_{k_pfx}")
        col_s3, col_s4 = st.columns(2)
        with col_s3:
            new_price = st.number_input("Giá vốn lần 1 (₫)", min_value=0, step=1000, value=0, key=f"new_prc1_{k_pfx}")
        with col_s4:
            new_weight = st.number_input("Tỷ trọng (%)", min_value=0, max_value=100, step=5, value=25, key=f"new_w_{k_pfx}")

        buy_twice = st.checkbox("🔄 Mua 2 lần", key=f"buy2_{k_pfx}")
        new_date_2 = None
        new_price_2 = 0
        if buy_twice:
            col_d2, col_p2 = st.columns(2)
            with col_d2:
                new_date_2 = st.date_input("Ngày mua lần 2", value=date.today(), format="DD/MM/YYYY", key=f"new_date2_{k_pfx}")
            with col_p2:
                new_price_2 = st.number_input("Giá vốn lần 2 (₫)", min_value=0, step=1000, value=0, key=f"new_prc2_{k_pfx}")

        if st.button("✅ Thêm vào danh mục", key=f"add_submit_{k_pfx}", use_container_width=True):
            if new_symbol and new_price > 0:
                entry = {
                    "ngay_mua": new_date.strftime("%Y-%m-%d"),
                    "ma_cp": new_symbol,
                    "gia_von": new_price,
                    "ty_trong": new_weight,
                }
                if buy_twice and new_price_2 > 0 and new_date_2:
                    entry["ngay_mua_2"] = new_date_2.strftime("%Y-%m-%d")
                    entry["gia_von_2"] = new_price_2
                save_portfolio_item(entry, tab_id)
                st.session_state[portfolio_key] = load_portfolio(tab_id)
                st.rerun()

    if add_clicked:
        add_stock_dialog()

    # ============================================================
    # DANH MỤC
    # ============================================================
    if not curr_portfolio and not curr_closed:
        st.info("Danh mục trống. Hãy thêm cổ phiếu mới để bắt đầu!")
        return

    with st.spinner("Đang lấy giá thị trường..."):
        industry_map = get_industry_map()
        rows = []
        for i, item in enumerate(curr_portfolio):
            market_price = get_market_price(item["ma_cp"])
            # Giá vốn trung bình nếu mua 2 lần
            gia_von_avg = item["gia_von"]
            if item.get("gia_von_2"):
                gia_von_avg = (item["gia_von"] + item["gia_von_2"]) / 2

            if market_price:
                profit_pct = (market_price - gia_von_avg) / gia_von_avg * 100
                display_price = market_price
            else:
                profit_pct = 0.0
                display_price = gia_von_avg

            rows.append({
                "ma_cp": item["ma_cp"],
                "ngay_mua": item["ngay_mua"],
                "gia_von": item["gia_von"],
                "ngay_mua_2": item.get("ngay_mua_2"),
                "gia_von_2": item.get("gia_von_2"),
                "gia_von_avg": gia_von_avg,
                "current_price": display_price,
                "profit_pct": profit_pct,
                "ty_trong": item["ty_trong"],
                "nganh": industry_map.get(item["ma_cp"], "—"),
            })

    # BẢNG DANH MỤC (HTML) + NÚT CHỈNH SỬA / XÓA
    table_rows_html = ""
    for r in rows:
        ngay_display = datetime.strptime(r["ngay_mua"], "%Y-%m-%d").strftime("%d/%m/%Y")
        if r.get("ngay_mua_2"):
            ngay_display += "<br>" + datetime.strptime(r["ngay_mua_2"], "%Y-%m-%d").strftime("%d/%m/%Y")

        gia_von_fmt = f"{r['gia_von_avg']:,.0f}".replace(",", ".")
        gia_tt_fmt = f"{r['current_price']:,.0f}".replace(",", ".")
        p = r["profit_pct"]
        if p >= 0:
            p_cls = "profit-positive"
            p_icon = "▲"
            p_sign = "+"
        else:
            p_cls = "profit-negative"
            p_icon = "▼"
            p_sign = ""
        profit_display = f'<span class="{p_cls}">{p_icon} {p_sign}{p:.2f}%</span>'

        table_rows_html += (f'<tr><td>{rows.index(r)+1}</td>'
                            f'<td>{ngay_display}</td>'
                            f'<td class="symbol">{r["ma_cp"]}</td><td>{gia_von_fmt}</td>'
                            f'<td>{gia_tt_fmt}</td><td>{profit_display}</td>'
                            f'<td>{r["ty_trong"]}%</td><td>{r["nganh"]}</td></tr>')

    table_html = ('<div class="glass-card"><table class="portfolio-table">'
                  '<thead><tr><th>STT</th><th>Ngày mua</th><th>Mã cổ phiếu</th>'
                  '<th>Giá vốn</th><th>Giá thị trường</th><th>% Lợi nhuận</th>'
                  '<th>Tỷ trọng</th><th>Ngành</th></tr></thead>'
                  f'<tbody>{table_rows_html}</tbody></table></div>')
    st.markdown(table_html, unsafe_allow_html=True)

    # CHỈNH SỬA / XÓA TỪNG CỔ PHIẾU
    st.markdown("")  # spacer

    for i, item in enumerate(curr_portfolio):
        idx = i
        col_name, col_edit, col_sell, col_del = st.columns([3, 1, 1, 1])
        with col_name:
            ngay = datetime.strptime(item["ngay_mua"], "%Y-%m-%d").strftime("%d/%m/%Y")
            st.markdown(
                f'<span style="color:#78909C;font-size:0.85rem;">'
                f'{idx+1}. {item["ma_cp"]} — tỷ trọng {item["ty_trong"]}%</span>',
                unsafe_allow_html=True,
            )
        with col_edit:
            if st.button("✏️ Sửa", key=f"edit_{k_pfx}_{idx}", use_container_width=True):
                st.session_state[edit_key] = idx
                st.session_state[sell_key] = None
        with col_sell:
            if st.button("💰 Bán", key=f"sell_{k_pfx}_{idx}", use_container_width=True):
                st.session_state[sell_key] = idx
                st.session_state[edit_key] = None
        with col_del:
            if st.button("🗑️ Xóa", key=f"del_{k_pfx}_{idx}", use_container_width=True):
                removed = item
                delete_portfolio_item(item["id"])
                st.session_state[portfolio_key] = load_portfolio(tab_id)
                st.session_state[edit_key] = None
                st.toast(f"Đã xóa **{removed['ma_cp']}**", icon="🗑️")
                st.rerun()

        # Form bán cổ phiếu (chốt lời / cắt lỗ)
        if st.session_state.get(sell_key) == idx:
            with st.form(f"sell_form_{k_pfx}_{idx}"):
                st.markdown(
                    f'<span style="color:#FF6F00;font-weight:600;">💰 Bán {item["ma_cp"]}</span>',
                    unsafe_allow_html=True,
                )
                sc1, sc2 = st.columns(2)
                with sc1:
                    sell_date = st.date_input("Ngày bán", value=date.today(), format="DD/MM/YYYY", key=f"sdate_{k_pfx}_{idx}")
                with sc2:
                    sell_price = st.number_input("Giá bán (₫)", min_value=0, step=1000, value=0, key=f"sprice_{k_pfx}_{idx}")
                sb1, sb2 = st.columns(2)
                with sb1:
                    confirm_sell = st.form_submit_button("✅ Xác nhận bán", use_container_width=True)
                with sb2:
                    cancel_sell = st.form_submit_button("↩️ Hủy", use_container_width=True)

                if confirm_sell and sell_price > 0:
                    gia_von_avg = item["gia_von"]
                    if item.get("gia_von_2"):
                        gia_von_avg = (item["gia_von"] + item["gia_von_2"]) / 2
                    profit_pct = (sell_price - gia_von_avg) / gia_von_avg * 100

                    closed_entry = {
                        "ma_cp": item["ma_cp"],
                        "ngay_mua": item["ngay_mua"],
                        "gia_von": item["gia_von"],
                        "ty_trong": item["ty_trong"],
                        "ngay_ban": sell_date.strftime("%Y-%m-%d"),
                        "gia_ban": sell_price,
                        "profit_pct": profit_pct,
                        "loai": "chot_loi" if profit_pct >= 0 else "cat_lo",
                    }
                    if item.get("ngay_mua_2"):
                        closed_entry["ngay_mua_2"] = item["ngay_mua_2"]
                        closed_entry["gia_von_2"] = item["gia_von_2"]

                    save_closed_item(closed_entry, tab_id)
                    delete_portfolio_item(item["id"])
                    st.session_state[closed_key] = load_closed(tab_id)
                    st.session_state[portfolio_key] = load_portfolio(tab_id)
                    st.session_state[sell_key] = None
                    label = "Chốt lời" if profit_pct >= 0 else "Cắt lỗ"
                    st.toast(f"{label} **{item['ma_cp']}** ({profit_pct:+.2f}%)", icon="💰")
                    st.rerun()

                if cancel_sell:
                    st.session_state[sell_key] = None
                    st.rerun()

        # Form chỉnh sửa inline
        if st.session_state.get(edit_key) == idx:
            with st.form(f"edit_form_{k_pfx}_{idx}"):
                st.markdown(
                    f'<span style="color:#00897B;font-weight:600;">Chỉnh sửa {item["ma_cp"]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown("**Lần mua 1**")
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    edit_date = st.date_input(
                        "Ngày mua 1",
                        value=datetime.strptime(item["ngay_mua"], "%Y-%m-%d").date(),
                        format="DD/MM/YYYY",
                        key=f"edate_{k_pfx}_{idx}",
                    )
                with ec2:
                    edit_price = st.number_input(
                        "Giá vốn 1 (₫)", min_value=0, step=1000, value=int(item["gia_von"]),
                        key=f"eprice_{k_pfx}_{idx}",
                    )
                with ec3:
                    edit_weight = st.number_input(
                        "Tỷ trọng (%)", min_value=0, max_value=100, step=5, value=int(item["ty_trong"]),
                        key=f"eweight_{k_pfx}_{idx}",
                    )

                has_buy2 = bool(item.get("ngay_mua_2"))
                st.markdown("**Lần mua 2** *(tuỳ chọn)*")
                ed2_1, ed2_2 = st.columns(2)
                with ed2_1:
                    edit_date_2 = st.date_input(
                        "Ngày mua 2",
                        value=datetime.strptime(item["ngay_mua_2"], "%Y-%m-%d").date() if has_buy2 else date.today(),
                        format="DD/MM/YYYY",
                        key=f"edate2_{k_pfx}_{idx}",
                    )
                with ed2_2:
                    edit_price_2 = st.number_input(
                        "Giá vốn 2 (₫)", min_value=0, step=1000,
                        value=int(item["gia_von_2"]) if has_buy2 else 0,
                        key=f"eprice2_{k_pfx}_{idx}",
                    )

                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    save_btn = st.form_submit_button("✅ Lưu lại", use_container_width=True)
                with fc2:
                    cancel_btn = st.form_submit_button("↩️ Hủy", use_container_width=True)
                
                if has_buy2:
                    with fc3:
                        del_buy2_btn = st.form_submit_button("🗑️ Xóa lần mua 2", use_container_width=True)
                else:
                    del_buy2_btn = False

                if save_btn:
                    upd_data = {
                        "ngay_mua": edit_date.strftime("%Y-%m-%d"),
                        "gia_von": edit_price,
                        "ty_trong": edit_weight,
                    }
                    if edit_price_2 > 0:
                        upd_data["ngay_mua_2"] = edit_date_2.strftime("%Y-%m-%d")
                        upd_data["gia_von_2"] = edit_price_2
                    else:
                        upd_data["ngay_mua_2"] = None
                        upd_data["gia_von_2"] = None

                    update_portfolio_item(item["id"], upd_data)
                    st.session_state[portfolio_key] = load_portfolio(tab_id)
                    st.session_state[edit_key] = None
                    st.cache_data.clear()
                    st.toast(f"Đã cập nhật **{item['ma_cp']}**", icon="✅")
                    st.rerun()
                if cancel_btn:
                    st.session_state[edit_key] = None
                    st.rerun()
                if del_buy2_btn:
                    update_portfolio_item(item["id"], {"ngay_mua_2": None, "gia_von_2": None})
                    st.session_state[portfolio_key] = load_portfolio(tab_id)
                    st.session_state[edit_key] = None
                    st.cache_data.clear()
                    st.toast(f"Đã xóa lần mua 2 của **{item['ma_cp']}**", icon="🗑️")
                    st.rerun()

    # ============================================================
    # THỐNG KÊ VỊ THẾ ĐÃ ĐÓNG (Chốt lời / Cắt lỗ)
    # ============================================================
    if curr_closed:
        st.markdown("---")
        st.markdown("### <span style='color:#00897B;'>📊 Lịch sử giao dịch đã đóng</span>", unsafe_allow_html=True)

        # Phân loại
        chot_loi = [c for c in curr_closed if c["loai"] == "chot_loi"]
        cat_lo = [c for c in curr_closed if c["loai"] == "cat_lo"]

        # Thống kê tổng quan
        total_closed = len(curr_closed)
        win_rate = len(chot_loi) / total_closed * 100 if total_closed > 0 else 0
        avg_profit = sum(c["profit_pct"] for c in chot_loi) / len(chot_loi) if chot_loi else 0
        avg_loss = sum(c["profit_pct"] for c in cat_lo) / len(cat_lo) if cat_lo else 0

        stats_html = f"""
        <div class="kpi-row">
            <div class="kpi-card" style="background: linear-gradient(145deg, #2E7D32 0%, #1B5E20 100%); box-shadow: 0 4px 16px rgba(46,125,50,0.25);">
                <div class="kpi-title-row"><span class="kpi-icon">✅</span><div class="label">Chốt lời</div></div>
                <div class="value neutral">{len(chot_loi)}</div>
            </div>
            <div class="kpi-card" style="background: linear-gradient(145deg, #C62828 0%, #B71C1C 100%); box-shadow: 0 4px 16px rgba(198,40,40,0.25);">
                <div class="kpi-title-row"><span class="kpi-icon">❌</span><div class="label">Cắt lỗ</div></div>
                <div class="value neutral">{len(cat_lo)}</div>
            </div>
            <div class="kpi-card" style="background: linear-gradient(145deg, #1565C0 0%, #0D47A1 100%); box-shadow: 0 4px 16px rgba(21,101,192,0.25);">
                <div class="kpi-title-row"><span class="kpi-icon">🎯</span><div class="label">Win Rate</div></div>
                <div class="value neutral">{win_rate:.1f}%</div>
            </div>
            <div class="kpi-card" style="background: linear-gradient(145deg, #FF8F00 0%, #EF6C00 100%); box-shadow: 0 4px 16px rgba(255,143,0,0.25);">
                <div class="kpi-title-row"><span class="kpi-icon">📈</span><div class="label">TB Lãi / Lỗ</div></div>
                <div class="value neutral" style="font-size:1rem;">{avg_profit:+.2f}% / {avg_loss:+.2f}%</div>
            </div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)

        # Bảng chi tiết
        closed_rows_html = ""
        for ci, c in enumerate(curr_closed):
            ngay_mua = datetime.strptime(c["ngay_mua"], "%Y-%m-%d").strftime("%d/%m/%Y")
            ngay_ban = datetime.strptime(c["ngay_ban"], "%Y-%m-%d").strftime("%d/%m/%Y")
            gia_von = c["gia_von"]
            if c.get("gia_von_2"):
                gia_von = (c["gia_von"] + c["gia_von_2"]) / 2
            gia_von_fmt = f"{gia_von:,.0f}".replace(",", ".")
            gia_ban_fmt = f"{c['gia_ban']:,.0f}".replace(",", ".")
            p = c["profit_pct"]
            if p >= 0:
                p_cls = "profit-positive"
                p_icon = "▲"
                p_sign = "+"
            else:
                p_cls = "profit-negative"
                p_icon = "▼"
                p_sign = ""
            profit_display = f'<span class="{p_cls}">{p_icon} {p_sign}{p:.2f}%</span>'
            loai_badge = '<span style="background:#2E7D32;color:#fff;padding:2px 8px;border-radius:8px;font-size:0.75rem;">Chốt lời</span>' if c["loai"] == "chot_loi" else '<span style="background:#C62828;color:#fff;padding:2px 8px;border-radius:8px;font-size:0.75rem;">Cắt lỗ</span>'

            closed_rows_html += (f'<tr><td>{ci+1}</td><td class="symbol">{c["ma_cp"]}</td>'
                                 f'<td>{ngay_mua}</td><td>{gia_von_fmt}</td>'
                                 f'<td>{ngay_ban}</td><td>{gia_ban_fmt}</td>'
                                 f'<td>{profit_display}</td><td>{loai_badge}</td></tr>')

        closed_table = ('<div class="glass-card"><table class="portfolio-table">'
                        '<thead><tr><th>STT</th><th>Mã CP</th><th>Ngày mua</th>'
                        '<th>Giá vốn</th><th>Ngày bán</th><th>Giá bán</th>'
                        '<th>% Lợi nhuận</th><th>Loại</th></tr></thead>'
                        f'<tbody>{closed_rows_html}</tbody></table></div>')
        st.markdown(closed_table, unsafe_allow_html=True)

        # Nút xóa từng giao dịch đã đóng
        for ci, c in enumerate(curr_closed):
            cc_label, cc_btn = st.columns([4, 1])
            with cc_label:
                st.markdown(
                    f'<span style="color:#78909C;font-size:0.85rem;">'
                    f'{ci+1}. {c["ma_cp"]} — bán {datetime.strptime(c["ngay_ban"], "%Y-%m-%d").strftime("%d/%m/%Y")}</span>',
                    unsafe_allow_html=True,
                )
            with cc_btn:
                if st.button("🗑️ Xóa", key=f"del_closed_{k_pfx}_{ci}", use_container_width=True):
                    delete_closed_item(c["id"])
                    st.session_state[closed_key] = load_closed(tab_id)
                    st.toast(f"Đã xóa giao dịch **{c['ma_cp']}**", icon="🗑️")
                    st.rerun()

    # Timestamp
    st.markdown("")
    st.markdown(
        f'<div class="timestamp">Cập nhật lúc {datetime.now().strftime("%H:%M:%S %d/%m/%Y")} '
        f'&nbsp;|&nbsp; Giá được cache 5 phút</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN ENTRY POINT - TABS
# ============================================================

# Khởi tạo Tabs
tab1, tab2 = st.tabs(["📑 Danh mục Tổng", "📑 Danh mục Margin"])

with tab1:
    render_tab_content("tab1", "Tài khoản 1 (Đuôi 1)")
    
with tab2:
    render_tab_content("tab2", "Tài khoản 6 (Margin)")
import streamlit as st
import base64
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any

# Utils
from utils.data_processing import calculate_portfolio_metrics, prepare_closed_positions_stats, get_market_price

def render_header(tab_id: str):
    """Render the application header with optional logo."""
    LOGO_PATH = Path("logo.png")
    logo_b64 = ""
    if LOGO_PATH.exists() and tab_id == "tab1":
        logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

    if logo_b64:
        header_html = f"""
        <div class="main-header">
            <img src="data:image/png;base64,{logo_b64}" class="logo-img" alt="KAFI SAIGON">
            <h1>BÁO CÁO DANH MỤC ĐẦU TƯ</h1>
            <div class="sub">Cập nhật ngày {datetime.now().strftime("%d/%m/%Y")}</div>
            <div class="divider"></div>
        </div>
        """
    else:
        header_html = f"""
        <div class="main-header">
            <h1>BÁO CÁO DANH MỤC ĐẦU TƯ</h1>
            <div class="sub">Cập nhật ngày {datetime.now().strftime("%d/%m/%Y")}</div>
            <div class="divider"></div>
        </div>
        """
    st.markdown(header_html, unsafe_allow_html=True)

def render_portfolio_table(rows: List[Dict[str, Any]], tab_id: str):
    """Render the HTML table for the portfolio."""
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

        ty_trong_td = f'<td>{r["ty_trong"]}%</td>' if tab_id == "tab1" else ""
        table_rows_html += (f'<tr><td>{rows.index(r)+1}</td>'
                            f'<td>{ngay_display}</td>'
                            f'<td class="symbol">{r["ma_cp"]}</td><td>{gia_von_fmt}</td>'
                            f'<td>{gia_tt_fmt}</td><td>{profit_display}</td>'
                            f'{ty_trong_td}<td>{r["nganh"]}</td></tr>')

    ty_trong_th = '<th>Tỷ trọng</th>' if tab_id == "tab1" else ""
    table_html = ('<div class="glass-card"><table class="portfolio-table">'
                  '<thead><tr><th>STT</th><th>Ngày mua</th><th>Mã cổ phiếu</th>'
                  '<th>Giá vốn</th><th>Giá thị trường</th><th>% Lợi nhuận</th>'
                  f'{ty_trong_th}<th>Ngành</th></tr></thead>'
                  f'<tbody>{table_rows_html}</tbody></table></div>')
    st.markdown(table_html, unsafe_allow_html=True)


def render_closed_stats(stats: Dict[str, Any]):
    """Render top statistics for closed positions."""
    if not stats:
        return
        
    stats_html = f"""
    <div class="kpi-row">
        <div class="kpi-card" style="background: linear-gradient(145deg, #2E7D32 0%, #1B5E20 100%); box-shadow: 0 4px 16px rgba(46,125,50,0.25);">
            <div class="kpi-title-row"><span class="kpi-icon">✅</span><div class="label">Chốt lời</div></div>
            <div class="value neutral">{stats['chot_loi_count']}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(145deg, #C62828 0%, #B71C1C 100%); box-shadow: 0 4px 16px rgba(198,40,40,0.25);">
            <div class="kpi-title-row"><span class="kpi-icon">❌</span><div class="label">Cắt lỗ</div></div>
            <div class="value neutral">{stats['cat_lo_count']}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(145deg, #1565C0 0%, #0D47A1 100%); box-shadow: 0 4px 16px rgba(21,101,192,0.25);">
            <div class="kpi-title-row"><span class="kpi-icon">🎯</span><div class="label">Win Rate</div></div>
            <div class="value neutral">{stats['win_rate']:.1f}%</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(145deg, #FF8F00 0%, #EF6C00 100%); box-shadow: 0 4px 16px rgba(255,143,0,0.25);">
            <div class="kpi-title-row"><span class="kpi-icon">📈</span><div class="label">TB Lãi / Lỗ</div></div>
            <div class="value neutral" style="font-size:1rem;">{stats['avg_profit']:+.2f}% / {stats['avg_loss']:+.2f}%</div>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)


def render_closed_table(curr_closed: List[Dict[str, Any]]):
    """Render HTML table for the closed positions history."""
    if not curr_closed:
        return

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

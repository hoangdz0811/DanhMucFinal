import streamlit as st
import pandas as pd
from datetime import datetime, date
from vnstock import Quote, Listing

import time

@st.cache_data(ttl=300, show_spinner=False)
def get_market_price(symbol: str) -> float | None:
    """Lấy giá đóng cửa mới nhất của 1 mã cổ phiếu (đơn vị: VND) với cơ chế retry và xử lý lỗi."""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            quote = Quote(symbol=symbol)
            df = quote.history(length="1M", interval="1D")
            
            if df is not None and not df.empty:
                # vnstock trả giá theo đơn vị nghìn VND (VD: 92.6 = 92,600 VND)
                raw_price = float(df["close"].iloc[-1])
                return raw_price * 1000
            else:
                st.warning(f"⚠️ vnstock không trả về dữ liệu cho {symbol}. (Thử lại {attempt + 1}/{max_retries})")
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                st.error(f"❌ Lỗi lấy giá {symbol} sau {max_retries} lần thử: {str(e)}")
                return None
                
    # If all retries failed and no exception was raised but data was empty
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_industry_map() -> dict:
    """Lấy bảng phân ngành ICB cấp 2 cho tất cả mã CP (cache 1 ngày)."""
    try:
        ls = Listing()
        df = ls.symbols_by_industries()
        if df is not None and not df.empty:
            return dict(zip(df["symbol"], df["industry_name"]))
    except Exception as e:
        print(f"Error fetching industry map: {e}")
        pass
    return {}

def calculate_portfolio_metrics(curr_portfolio, industry_map):
    """Tính toán các chỉ số cho danh mục: lãi/lỗ, giá trung bình, giá hiện tại..."""
    rows = []
    
    for item in curr_portfolio:
        ma_cp = item["ma_cp"]
        market_price = get_market_price(ma_cp)
        
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
            "id": item["id"],
            "ma_cp": ma_cp,
            "ngay_mua": item["ngay_mua"],
            "gia_von": item["gia_von"],
            "ngay_mua_2": item.get("ngay_mua_2"),
            "gia_von_2": item.get("gia_von_2"),
            "gia_von_avg": gia_von_avg,
            "current_price": display_price,
            "profit_pct": profit_pct,
            "ty_trong": item.get("ty_trong", 0),
            "nganh": industry_map.get(ma_cp, "—"),
            "raw_item": item # Keep original item for editing/deleting references
        })
        
    return rows

def prepare_closed_positions_stats(curr_closed):
    """Tính toán thống kê cho các vị thế đã đóng."""
    if not curr_closed:
        return None
        
    chot_loi = [c for c in curr_closed if c["loai"] == "chot_loi"]
    cat_lo = [c for c in curr_closed if c["loai"] == "cat_lo"]

    total_closed = len(curr_closed)
    win_rate = len(chot_loi) / total_closed * 100 if total_closed > 0 else 0
    avg_profit = sum(c["profit_pct"] for c in chot_loi) / len(chot_loi) if chot_loi else 0
    avg_loss = sum(c["profit_pct"] for c in cat_lo) / len(cat_lo) if cat_lo else 0
    
    return {
        "total_closed": total_closed,
        "chot_loi_count": len(chot_loi),
        "cat_lo_count": len(cat_lo),
        "win_rate": win_rate,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "chot_loi": chot_loi,
        "cat_lo": cat_lo
    }

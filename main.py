import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- ตั้งค่า Theme ---
st.set_page_config(
    page_title="💰 Dashboard ราคาทอง",
    page_icon="💎",
    layout="wide"
)

# --- ดึงราคาทองจากสมาคมค้าทองคำ ---
@st.cache_data(ttl=600)  # Cache 10 นาที เพื่อลดโหลดซ้ำ
def get_thai_gold_price():
    url = "https://www.goldtraders.or.th/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        gold_bar_sell = soup.find("span", id="DetailPlace_uc_goldprices1_lblBLSell")
        gold_bar_buy = soup.find("span", id="DetailPlace_uc_goldprices1_lblBLBuy")
        gold_jewelry_sell = soup.find("span", id="DetailPlace_uc_goldprices1_lblOMSell")
        gold_jewelry_buy = soup.find("span", id="DetailPlace_uc_goldprices1_lblOMBuy")

        if None in (gold_bar_sell, gold_bar_buy, gold_jewelry_sell, gold_jewelry_buy):
            raise ValueError("ไม่พบข้อมูลราคาทอง")

        return (
            float(gold_bar_sell.text.replace(",", "")),
            float(gold_bar_buy.text.replace(",", "")),
            float(gold_jewelry_sell.text.replace(",", "")),
            float(gold_jewelry_buy.text.replace(",", ""))
        )
    except Exception as e:
        st.error(f"❌ ไม่สามารถดึงราคาทองได้: {e}")
        return None, None, None, None

# --- โหลดราคาทอง ---
gold_bar_sell, gold_bar_buy, gold_jewelry_sell, gold_jewelry_buy = get_thai_gold_price()

st.title("💰 Dashboard ราคาทองคำ")

if gold_bar_sell is None or gold_bar_buy is None:
    st.error("⚠️ ไม่สามารถดึงราคาทองได้ กรุณาลองใหม่อีกครั้ง")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 ทองคำแท่ง ราคาซื้อ/ขาย")
        st.markdown(f"🔴 **ขายออก:** {gold_bar_sell:,.2f} บาท")
        st.markdown(f"🟢 **รับซื้อ:** {gold_bar_buy:,.2f} บาท")
    with col2:
        st.subheader("💎 ทองรูปพรรณ ราคาซื้อ/ขาย")
        st.markdown(f"🔴 **ขายออก:** {gold_jewelry_sell:,.2f} บาท")
        st.markdown(f"🟢 **รับซื้อ:** {gold_jewelry_buy:,.2f} บาท")

# --- คำนวณกำไร-ขาดทุนจากการซื้อทอง ---
st.subheader("📈 คำนวณกำไร-ขาดทุนจากการซื้อทอง")

gold_type = st.radio("เลือกประเภททอง", ["ทองคำแท่ง", "ทองรูปพรรณ"])
buy_price = st.number_input("💰 ราคาทองที่คุณซื้อ (บาท)", min_value=0.0, value=30000.0)
gold_weight = st.number_input("🏆 จำนวนทองที่ซื้อ (บาททอง)", min_value=0.0, value=1.0)

if st.button("🚀 คำนวณกำไร/ขาดทุน") and gold_bar_sell is not None:
    current_price = gold_bar_sell if gold_type == "ทองคำแท่ง" else gold_jewelry_sell
    total_buy = buy_price * gold_weight
    total_sell = current_price * gold_weight
    profit_loss = total_sell - total_buy
    percent_change = (profit_loss / total_buy * 100) if total_buy > 0 else 0
    
    st.success(f"📊 กำไร/ขาดทุนของคุณ: {'กำไร' if profit_loss > 0 else 'ขาดทุน'} {profit_loss:,.2f} บาท ({percent_change:.2f}%)")

# --- เครื่องมือคำนวณราคาซื้อทองของร้านทอง ---
st.subheader("🛒 เครื่องมือคำนวณราคาซื้อทองของร้านทอง")

default_sell = gold_bar_sell if gold_bar_sell is not None else 46650.0
default_buy = gold_bar_buy if gold_bar_buy is not None else 46550.0

custom_gold_sell_price = st.number_input("🔴 ราคาทองขายออก (บาท)", min_value=0.0, value=default_sell)
custom_gold_buy_price = st.number_input("🟢 ราคาทองรับซื้อ (บาท)", min_value=0.0, value=default_buy)

gold_weight = st.number_input("🏆 น้ำหนักทองที่ลูกค้าขายให้ร้าน (บาททอง)", min_value=0.0, value=1.0)
shop_fee = st.number_input("⚙️ ค่ากำเหน็จต่อบาททอง (บาท)", min_value=0.0, value=500.0)
devaluation_percent = st.number_input("📉 ค่าเสื่อมสภาพของทอง (%)", min_value=0.0, max_value=100.0, value=2.0)
other_costs = st.number_input("💸 ค่าใช้จ่ายเพิ่มเติมของร้าน (บาท)", min_value=0.0, value=100.0)

if st.button("📊 คำนวณราคาซื้อทอง"):
    base_purchase_price = custom_gold_buy_price * gold_weight
    depreciation_cost = (devaluation_percent / 100) * base_purchase_price
    total_cost = base_purchase_price - depreciation_cost - shop_fee - other_costs
    avg_price_per_baht = total_cost / gold_weight if gold_weight > 0 else 0
    total_sell_price = custom_gold_sell_price * gold_weight
    shop_profit = total_sell_price - total_cost
    shop_profit_percent = (shop_profit / total_sell_price * 100) if total_sell_price > 0 else 0

    st.info(f"🟢 ราคาทองรับซื้อทั้งหมด: {base_purchase_price:,.2f} บาท")
    st.warning(f"📉 หักค่าเสื่อมสภาพ: {depreciation_cost:,.2f} บาท")
    st.warning(f"⚙️ หักค่ากำเหน็จ: {shop_fee:,.2f} บาท")
    st.warning(f"💸 หักค่าใช้จ่ายเพิ่มเติม: {other_costs:,.2f} บาท")
    st.success(f"🏦 ราคาสุทธิที่ร้านต้องจ่ายให้ลูกค้า: {total_cost:,.2f} บาท")
    st.success(f"📌 ราคาซื้อเฉลี่ยต่อบาททอง: {avg_price_per_baht:,.2f} บาท")
    st.success(f"💰 กำไรของร้านทอง: {shop_profit:,.2f} บาท ({shop_profit_percent:.2f}%)")
# --- Footer ---
st.markdown("""
    <hr>
    <p style='text-align:center;'>📌 ข้อมูลจาก: <a href='https://www.goldtraders.or.th/' target='_blank'>สมาคมค้าทองคำ</a></p>
""", unsafe_allow_html=True)

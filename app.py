import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# --- 2. CSS (Tasarım Ayarları) ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { 
        min-width: 380px; 
        max-width: 380px; 
    }
    .sidebar-header { 
        font-size: 30px !important; 
        font-weight: 800; 
        color: #00D1B2; 
        margin-top: 10px; 
        margin-bottom: 10px;
    }
    .sidebar-subheader { 
        font-size: 24px !important; 
        font-weight: 700; 
        color: #F0F2F6; 
        margin-top: 15px; 
        margin-bottom: 10px;
    }
    /* Sol Paneldeki Butonu Şıklaştırma */
    div.stButton > button {
        background-color: #00D1B2 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 55px !important;
        border-radius: 8px !important;
        border: none !important;
        margin-top: 15px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. ANA EKRAN ÜST KISIM ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("---")

# --- 4. YAN PANEL (VERİ GİRİŞLERİ) ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)
sermaye = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=1500000, step=50000)
maliyet = st.sidebar.number_input("Dosya Başına Ort. Hasar Maliyeti", value=7500)
satis_hedefi = st.sidebar.slider("Aylık Poliçe Satış Hedefi", 50, 500, 100)

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)
hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25)
if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod: Risk yüksek!")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod: İdeal seviye.")
else:
    st.sidebar.success("🛡️ Güvenli Mod: Minimum risk.")

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">🏢 Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0)
st.sidebar.info(f"🛡️ Şirket Üzerindeki Risk

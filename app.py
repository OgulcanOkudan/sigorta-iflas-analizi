import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# Sidebar Tasarımı (380px genişlik, dev başlıklar ve ferahlık)
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
        margin-bottom: 10px;
        line-height: 1.2;
    }
    .sidebar-subheader {
        font-size: 24px !important;
        font-weight: 700;
        color: #F0F2F6;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    div.stButton > button {
        background-color: #00D1B2 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 55px !important;
        border-radius: 8px !important;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. ANA EKRAN GİRİŞ ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("Bu panel, finansal sağlığınızı **Stokastik Simülasyon** yöntemleriyle analiz eder.")
st.markdown("---")

# --- 3. YAN PANEL: VERİ GİRİŞİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin hasarları ödemek için hazırda tuttuğu toplam nakittir."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Gerçekleşen her bir hasar dosyasının ortalama maliyetidir (Severity)."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100,
    help="Her ay satmayı planladığınız yeni poliçe sayısı."
)

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# --- 4. YAN PANEL: HASAR FREKANSI ---
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
st.sidebar.caption("Son 6 aylık hasar adetlerini giriniz:")

h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# --- 5. YAN PANEL: FİYATLANDIRMA ---
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider(
    "Hedeflenen Kâr Marjı (%)", 
    0, 100, 25,
    help="Beklenen hasar maliyetinin üzerine eklenen güvenlik payıdır (Security Loading)."
)

if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod")
else:
    st.sidebar.success("🛡️ Güvenli Mod")

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# --- 6. YAN PANEL: RİSK & SÜRE ---
st.sidebar.markdown('<p

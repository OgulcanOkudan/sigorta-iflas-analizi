import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 380px;
        max-width: 380px;
    }
    .sidebar-header {
        font-size: 32px !important;
        font-weight: 800;
        color: #00D1B2;
        margin-bottom: 15px;
        margin-top: 10px;
        line-height: 1.2;
    }
    .sidebar-subheader {
        font-size: 26px !important;
        font-weight: 700;
        color: #F0F2F6;
        margin-bottom: 12px;
        margin-top: 15px;
        line-height: 1.2;
    }
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

# --- ANA BAŞLIK VE DETAYLI AÇIKLAMA ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("""
Bu panel, bir sigorta şirketinin finansal sağlığını **Stokastik Simülasyon (Monte Carlo & Poisson-Üstel Dağılım)** yöntemleriyle analiz eder. 
Sol menüden verilerinizi girin, hedef kâr marjınızı belirleyin ve gelecekteki olası iflas riskinizi şimdiden yönetin.
""")
st.markdown("---")

# --- YAN PANEL: VERİ GİRİŞ MERKEZİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)",
    value=1500000,
    step=50000,
    help="Şirketin tüm hasarları ödemek için hazırda bulundurduğu toplam nakit rezervidir."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti",
    value=7500,
    help="Gerçekleşen her bir hasar dosyasının şirkete ortalama maliyetidir (Severity)."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi",
    50, 500, 100,
    help="Her ay satmayı planladığınız yeni poliçe sayısıdır. Satış arttıkça prim geliri artar ancak risk dağılımı da değişir."
)

st.sidebar.markdown("---")

# --- YAN PANEL: HASAR FREKANSI ---
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
st.sidebar.caption("Gelecekteki hasar sıklığını (Frequency) tahmin etmek için son 6 aylık adetleri giriniz.")

h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---")

# --- YAN PANEL: FİYATLANDIRMA VE DETAYLI UYARILAR ---
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider(
    "Hedeflenen Kâr Marjı (%)",
    0, 100, 25,
    help="Aktüeryal

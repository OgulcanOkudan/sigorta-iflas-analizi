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

# --- 4. YAN PANEL (VERİ GİRİŞLERİ VE YARDIM NOTLARI) ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin hasarları ödemek için kasasında hazır tuttuğu toplam nakit rezervidir."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Gerçekleşen her bir hasar dosyasının şirkete ortalama maliyetidir (Severity)."
)

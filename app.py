import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

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
    }
    .sidebar-subheader {
        font-size: 26px !important;
        font-weight: 700;
        color: #F0F2F6;
        margin-bottom: 12px;
        margin-top: 15px;
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

# --- ANA BAŞLIK VE AÇIKLAMA ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("Bu panel, Stokastik Simülasyon yöntemleriyle finansal sağlığınızı analiz eder.")
st.markdown("---")

# --- YAN PANEL: VERİ GİRİŞ MERKEZİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=1500000, step=50000, help="Nakit rezerviniz.")
maliyet = st.sidebar.number_input("Dosya Başına Ort. Hasar Maliyeti", value=7500, help="Ortalama maliyet (Severity).")
satis_hedefi = st.sidebar.slider("Aylık Poliçe Satış Hedefi", 50, 500, 100, help="Aylık hedef.")

st.sidebar.markdown("---")

# --- YAN PANEL: HASAR FREKANSI ---
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)

h_verileri = []
cols = st.

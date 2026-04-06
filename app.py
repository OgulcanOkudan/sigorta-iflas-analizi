import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Sidebar Tasarımı (Fontları ekrana sığacak şekilde optimize ettik)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 360px;
        max-width: 360px;
    }
    .buyuk-baslik {
        font-size: 28px !important;
        font-weight: 800;
        color: #00D1B2;
        margin-bottom: 5px;
    }
    .alt-baslik {
        font-size: 22px !important;
        font-weight: 700;
        color: #F0F2F6;
        margin-bottom: 5px;
        margin-top: 15px;
    }
    /* Butonu daha belirgin yapıyoruz */
    .stButton>button {
        height: 60px;
        font-size: 20px !important;
        font-weight: bold;
        color: white;
        background-color: #00D1B2;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. ANA EKRAN ÜST KISIM ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("---")

# --- 3. YAN PANEL: VERİ GİRİŞİ ---
st.sidebar.markdown('<p class="buyuk-baslik">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin hasarları ödemek için kasasında hazır tuttuğu nakit rezervidir."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Gerçekleşen her bir hasar dosyasının ortalama maliyetidir (Severity)."
)
satis_hedefi = st.sidebar.slider("Aylık Poliçe Satış Hedefi", 50, 500, 100, help="Satmayı hedeflediğiniz poliçe sayısı.")

# --- 4. YAN PANEL: HASAR FREKANSI ---
st.sidebar.markdown('<p class="alt-baslik">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
st.sidebar.caption("Son 6 aylık hasar adetleri:")

h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

# --- 5. YAN PANEL: FİYATLANDIRMA ---
st.sidebar.markdown('<p class="alt-baslik">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25, help="Hasar maliyetinin üzerine eklenen güvenlik payıdır (Loading).")

if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod: Risk yüksek!")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod: İdeal seviye.")
else:
    st.sidebar.success("🛡️ Güvenli Mod: Minimum risk.")

# --- 6. YAN PANEL: RİSK VE SİMÜLASYON ---
st.sidebar.markdown('<p class="alt-baslik">🏢 Risk & Simülasyon</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0, help="Hasarların ne kadarını reasüröre devretmek istiyorsunuz?")
st.sidebar.info(f"🛡️ Şirket Üzerindeki Risk: %{100 - reasurans_orani}")
analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

# --- 7. MATEMATİKSEL HESAPLAMALAR ---
s_h = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / s_h
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
net_gelir = tavsiye_prim * s_h * (1 - (reasurans_orani/100))
net_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# ==========================================
# ANA EKRAN DÜZENİ (BUTON ARTIK BURADA!)
# ==========================================
st.info("👈 Lütfen sol panelden verilerinizi girin ve analizi başlatmak için aşağıdaki dev butona tıklayın. Yan paneldeki (?) simgeleri size rehberlik edecektir.")

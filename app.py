import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Sidebar Tasarımı (CSS Dokunuşuyla Şov Başlıyor)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 380px;
        max-width: 380px;
    }
    /* Ana Başlık Stili */
    .sidebar-header {
        font-size: 32px !important;
        font-weight: 800;
        color: #00D1B2; /* Turkuaz tonuyla daha profesyonel */
        margin-bottom: 20px;
        margin-top: 10px;
    }
    /* Alt Başlık Stilleri */
    .sidebar-subheader {
        font-size: 26px !important;
        font-weight: 700;
        color: #F0F2F6;
        margin-bottom: 15px;
        margin-top: 10px;
    }
    /* Boşluk Ayarı */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- ANA EKRAN BAŞLIK ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("---")

# --- YAN PANEL: VERİ GİRİŞ MERKEZİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

# 1. Sermaye ve Maliyet
sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin hasarları ödemek için kasasında tuttuğu toplam nakittir."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Her bir hasar dosyasının şirkete ortalama maliyetidir."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100,
    help="Her ay satmayı planladığınız yeni poliçe sayısıdır."
)

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# 2. Geçmiş Hasar Verileri (Frekans)
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
st.sidebar.caption("Son 6 aylık hasar adetlerini giriniz:")
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# 3. Fiyatlandırma Stratejisi
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider(
    "Hedeflenen Kâr Marjı (%)", 
    0, 100, 25,
    help="Güvenlik payı (Security Loading)."
)

if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod")
else:
    st.sidebar.success("🛡️ Güvenli Mod")

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# 4. Gelişmiş Risk Yönetimi
st.sidebar.markdown('<p class="sidebar-subheader">🏢 Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider(
    "Risk Devir Oranı (%)", 
    0, 90, 0,
    help="Hasarların ne kadarını reasüröre devretmek istiyorsunuz?"
)
st.sidebar.info(f"🛡️ Şirket Üzerindeki Risk: %{100 - reasurans_orani}")

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# 5. Simülasyon Ayarları (YENİ AYRILMIŞ BÖLÜM)
st.sidebar.markdown('<p class="sidebar-subheader">⏱️ Simülasyon Ayarı</p>', unsafe_allow_html=True)
analiz_suresi = st.sidebar.slider(
    "Analiz Süresi (Yıl)", 
    1, 5, 3,
    help="Gelecekte kaç yıllık bir projeksiyon görmek istiyorsunuz?"
)

# --- HESAPLAMA MOTORU ---
saf_prim = (hasar_ort * maliyet) / satis_hedefi
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
satis_geliri = tavsiye_prim * satis_hedefi * (1 - (reasurans_orani/100))
beklenen_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# --- SİMÜLASYON ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT"):
    aylar = analiz_suresi * 12
    sim_n = 5000 
    tablo = np.zeros((aylar + 1, sim_n))
    tablo[0, :] = sermaye
    
    for ay in range(aylar):
        gelir = np.random.poisson(satis_hedefi, sim_n) * tavsiye_prim * (1 - (reasurans_orani/100))
        hasar_sayisi = np.random.poisson(hasar_

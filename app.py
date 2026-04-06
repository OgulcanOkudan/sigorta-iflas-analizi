import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# Sidebar Tasarımı (380px genişlik ve turkuaz dev başlıklar)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { min-width: 380px; max-width: 380px; }
    .sidebar-header { font-size: 32px !important; font-weight: 800; color: #00D1B2; margin-bottom: 10px; }
    .sidebar-subheader { font-size: 26px !important; font-weight: 700; color: #F0F2F6; margin-top: 15px; margin-bottom: 10px; }
    div.stButton > button {
        background-color: #00D1B2 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 55px !important;
        border-radius: 10px !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. ANA EKRAN GİRİŞ ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("Bu sistem, sigorta portföyünüzün finansal geleceğini **Stokastik Simülasyon** ile analiz eder.")
st.markdown("---")

# --- 3. YAN PANEL: VERİ GİRİŞ MERKEZİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Giriş Merkezi</p>', unsafe_allow_html=True)

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
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100,
    help="Her ay satmayı hedeflediğiniz yeni poliçe sayısıdır. Geliri doğrudan etkiler."
)

st.sidebar.markdown("---")

# --- 4. YAN PANEL: HASAR SAYILARI ---
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Sayıları</p>', unsafe_allow_html=True)
st.sidebar.caption("Gelecekteki hasar sıklığını tahmin etmek için son 6 aylık verileri giriniz.")

h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay Adedi", value=35+(i*2), min_value=0)
    h_verileri.append(val)
hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---")

# --- 5. YAN PANEL: FİYATLANDIRMA & KÂR ---
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma & Kâr</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider(
    "Hedeflenen Kâr Marjı (%)", 
    0, 100, 25,
    help="Hasar maliyetinin üzerine belirsizlikler için eklenen emniyet payıdır (Security Loading)."
)

if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod: Risk yüksek!")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod: İdeal seviye.")
else:
    st.sidebar.success("🛡️ Güvenli Mod: Minimum risk.")

st.sidebar.markdown("---")

# --- 6. YAN PANEL: GELİŞMİŞ RİSK YÖNETİMİ ---
st.sidebar.markdown('<p class="sidebar-subheader">🏢 Gelişmiş Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider(
    "Risk Devir Oranı (%)", 
    0, 90, 0,
    help="Hasarların ne kadarını başka bir reasürör şirkete devretmek istiyorsunuz?"
)
st.sidebar.info(f"🛡️ Şirket Üzerindeki Risk: %{100 - reasurans_orani}")

# --- 7. YAN PANEL: SİMÜLASYON AYARLARI ---
st.sidebar.markdown('<p class="sidebar-subheader">⏱️ Simülasyon Ayarları</p>', unsafe_allow_html=True)
analiz_suresi = st.sidebar.slider(
    "Analiz Süresi (Yıl)", 
    1, 5, 3,
    help="Simülasyonun ne kadar ileriye dönük bir gelecek tahmini yapacağını belirler."
)

st.sidebar.markdown("---")

# --- 8. HESAPLAMA MOTORU ---
s_h = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / s_h
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
net_gelir = tavsiye_prim * s_h * (1 - (reasurans_orani / 100))
net_gider = (hasar_ort * mali

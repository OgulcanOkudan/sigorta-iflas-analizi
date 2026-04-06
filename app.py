import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Sidebar Genişliğini (380px) ve Başlık Boyutlarını Ayarlayan CSS
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 380px;
        max-width: 380px;
    }
    .sidebar-header {
        font-size: 26px !important;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 5px;
    }
    .sidebar-subheader {
        font-size: 20px !important;
        font-weight: 600;
        color: #F0F2F6;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- ANA BAŞLIK ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("""
Bu panel, bir sigorta şirketinin finansal sağlığını **Stokastik Simülasyon** yöntemleriyle analiz eder. 
Verileri girin, ideal priminizi bulun ve iflas riskinizi yönetin.
""")

# --- YAN PANEL: VERİ GİRİŞ MERKEZİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Giriş Merkezi</p>', unsafe_allow_html=True)

# 1. Sermaye ve Maliyet
sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin tüm hasarları ödemek için hazırda bulundurduğu toplam nakit rezervidir."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Dosya başına düşen ortalama hasar tutarıdır (Severity)."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100,
    help="Her ay kaç adet yeni sigorta poliçesi satmayı hedefliyorsunuz?"
)

# 2. Geçmiş Hasar Verileri
st.sidebar.markdown('<p class="sidebar-subheader">📉 Son 6 Aylık Hasar Sayıları</p>', unsafe_allow_html=True)
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

# 3. Fiyatlandırma Stratejisi
st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma & Kâr</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider(
    "Hedeflenen Kâr Marjı (%)", 
    0, 100, 25,
    help="Beklenen hasarların üzerine eklenen emniyet payıdır (Security Loading)."
)

# Dinamik Rehberlik Metni
if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi: Risk yüksektir.")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli: İdeal denge.")
else:
    st.sidebar.success("🛡️ Güvenli: İflas riski minimum.")

# 4. Reasürans & Süre
with st.sidebar.expander("🏢 Gelişmiş Risk Yönetimi"):
    reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0)
    analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

# --- HESAPLAMA MOTORU ---
saf_prim = (hasar_ort * maliyet) / satis_hedefi
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
satis_geliri = tavsiye_prim * satis_hedefi * (1 - (reasurans_orani/100))
beklenen_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# --- SİMÜLASYON ---
if st.sidebar.button("🚀 Analizi Başlat"):
    aylar = analiz_suresi * 12
    sim_n = 5000 
    tablo = np.zeros((aylar + 1, sim_n))
    tablo[0, :] = sermaye
    
    for ay in range(aylar):
        gelir = np.random.poisson(satis_hedefi, sim_n) * tavsiye_prim * (1 - (reasurans_orani/100))
        hasar_sayisi = np.random.poisson(hasar_ort, sim_n)
        gider = np.zeros(sim_n)
        for s in range(sim_n):
            if hasar_sayisi[s] > 0:
                gider[s] = np.sum(np.random.exponential(maliyet, hasar_sayisi[s]))
        gider = gider * (1 - (reasurans_orani/100))
        tablo[ay + 1, :] = tablo[ay, :] + gelir - gider

    iflas_sayisi = np.sum(np.min(tablo, axis=0) < 0)
    iflas_riski = (iflas_sayisi / sim_n) * 100
    loss_ratio = (beklenen_gider / (satis_geliri if satis_geliri > 0 else 1)) * 100
    ortalama_kasa = np.mean(tablo[-1, :])

    # --- EKRAN ÇIKTILARI ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tavsiye Edilen Prim", f"{tavsiye_prim:,.0f} TL")
    if iflas_riski < 5:
        c2.metric

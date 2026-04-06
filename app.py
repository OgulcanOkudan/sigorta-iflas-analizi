import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Sidebar Tasarımı: Dev Başlıklar ve Ferah Bölmeler
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
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- ANA EKRAN ÜST KISIM ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("---")

# --- YAN PANEL ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin kasasındaki toplam nakit rezervi."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Ortalama hasar şiddeti (Severity)."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100
)

st.sidebar.markdown("---") # ÇİZGİ
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)

h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---") # ÇİZGİ
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25)

if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod")
else:
    st.sidebar.success("🛡️ Güvenli Mod")

st.sidebar.markdown("---") # ÇİZGİ
st.sidebar.markdown('<p class="sidebar-subheader">🏢 Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0)
st.sidebar.info(f"🛡️ Şirket Üzerindeki Risk: %{100 - reasurans_orani}")

st.sidebar.markdown("---") # ÇİZGİ
st.sidebar.markdown('<p class="sidebar-subheader">⏱️ Simülasyon Ayarı</p>', unsafe_allow_html=True)
analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

# --- MATEMATİKSEL ARKA PLAN ---
s_hedef = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / s_hedef
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
net_gelir = tavsiye_prim * s_hedef * (1 - (reasurans_orani/100))
net_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# --- ANALİZİ BAŞLAT BUTONU VE TÜM İÇERİK ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT"):
    with st.spinner("5.000 farklı senaryo hesaplanıyor, lütfen bekleyin..."):
        aylar = analiz_suresi * 12
        sim_n = 5000 
        tablo = np.zeros((aylar + 1, sim_n))
        tablo[0, :] = sermaye
        
        # Simülasyon Döngüsü
        for ay in range(aylar):
            # Poisson ile gelir ve hasar adedi simülasyonu
            gelir_sim = np.random.poisson(s_hedef, sim_n) * tavsiye_prim * (1 - (reasurans_orani/100))
            hasar_sayisi = np.random.poisson(hasar_ort, sim_n)
            
            # Üstel dağılım ile hasar tutarı simülasyonu
            gider_sim = np.zeros(sim_n)
            for s in range(sim_n):
                if hasar_sayisi[s] > 0:
                    gider_sim[s] = np.sum(np.random.exponential(maliyet, hasar_sayisi[s]))
            
            gider_sim = gider_sim * (1 - (reasurans_orani/100))
            tablo[ay + 1, :] = tablo[ay, :] + gelir_sim - gider_sim

        # Analitik Çıktılar
        iflas_sayisi = np.sum(np.min(tablo, axis=0) < 0)
        iflas_riski = (iflas_sayisi / sim_n) * 100
        loss_ratio = (net_gider / (net_gelir if net_gelir > 0 else 1)) * 100
        ortalama_kasa = np.mean(tablo[-1,

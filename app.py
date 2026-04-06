import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. TASARIM VE STİL ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { min-width: 380px; max-width: 380px; }
    .main-title { font-size: 32px; font-weight: 800; color: #00D1B2; margin-bottom: 20px; }
    .sub-title { font-size: 24px; font-weight: 700; color: #F0F2F6; margin-top: 20px; }
    div.stButton > button {
        background-color: #00D1B2 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 50px !important;
        width: 100% !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ANA EKRAN GİRİŞ ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("Bu sistem, sigorta portföyünüzün iflas riskini **Stokastik Simülasyon** ile ölçer.")
st.markdown("---")

# --- 3. SIDEBAR (VERİ GİRİŞİ) ---
st.sidebar.markdown('<p class="main-title">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=1500000, step=50000, help="Şirketin nakit rezervi.")
maliyet = st.sidebar.number_input("Ortalama Hasar Maliyeti", value=7500, help="Dosya başına ortalama tazminat.")
satis = st.sidebar.slider("Aylık Poliçe Satış Hedefi", 50, 500, 100)

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sub-title">📉 Hasar Frekansı</p>', unsafe_allow_html=True)

h_verileri = []
c1, c2 = st.sidebar.columns(2)
for i in range(6):
    val = (c1 if i % 2 == 0 else c2).number_input(f"{i+1}. Ay Adedi", value=35+(i*2), min_value=0)
    h_verileri.append(val)
h_ort = sum(h_verileri) / 6

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sub-title">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar = st.sidebar.slider("Kâr Marjı (%)", 0, 100, 25, help="Security Loading payı.")

if kar < 15: st.sidebar.warning("⚠️ Rekabetçi: Risk Yüksek")
elif 15 <= kar <= 35: st.sidebar.info("✅ Dengeli: İdeal Seviye")
else: st.sidebar.success("🛡️ Güvenli: Minimum Risk")

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sub-title">🏢 Risk Yönetimi</p>', unsafe_allow_html=True)
reas = st.sidebar.slider("Reasürans Devir (%)", 0, 90, 0)
sure = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

st.sidebar.markdown("---")

# --- 4. HESAPLAMA MOTORU ---
s_h = satis if satis > 0 else 1
saf_prim = (h_ort * maliyet) / s_h
tavsiye_prim = saf_prim * (1 + (kar / 100))
n_gelir = tavsiye_prim * s_h * (1 - (reas / 100))
n_gider = (h_ort * maliyet) * (1 - (reas / 100))

# --- 5. ANALİZ VE ÇIKTILAR ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT"):
    with st.spinner("5.000 senaryo simüle ediliyor..."):
        aylar = sure * 12
        sim_n = 5000
        tablo = np.zeros((aylar + 1, sim_n))
        tablo[0, :] = sermaye
        
        for ay in range(aylar):
            g_sim = np.random.poisson(s_h, sim_n) * tavsiye_prim * (1 - (reas/100))
            h_sim = np.random.poisson(h_ort, sim_n)
            gi_sim = np.zeros(sim_n)
            for s in range(sim_n):
                if h_sim[s] > 0:
                    gi_sim[s] = np.sum(np.random.exponential(maliyet, h_sim[s]))
            tablo[ay+1, :] = tablo[ay, :] + g_sim - (gi_sim * (1 - (reas/100)))

        iflas_riski = (np.sum(np.min(tablo, axis=0) < 0) / sim_n) * 100
        loss_ratio = (n_gider / (n_gelir if n_gelir > 0 else 1)) * 100
        kasa = np.mean(tablo[-1, :])

        # Kartlar
        m

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# --- 2. CSS (Butonu ve Başlıkları Zorla Şekillendirme) ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { min-width: 350px; max-width: 350px; }
    .buyuk-baslik { font-size: 28px !important; font-weight: 800; color: #00D1B2; }
    .alt-baslik { font-size: 20px !important; font-weight: 700; color: #F0F2F6; margin-top: 15px; margin-bottom: 5px;}
    
    /* BUTON İÇİN ZORUNLU CSS (Asla Kaybolmaz) */
    div.stButton > button:first-child {
        background-color: #00D1B2 !important;
        color: white !important;
        height: 60px !important;
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        margin-top: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. ANA EKRAN ÜST KISIM ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("---")

# --- 4. YAN PANEL (VERİ GİRİŞLERİ) ---
st.sidebar.markdown('<p class="buyuk-baslik">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=1500000, step=50000)
maliyet = st.sidebar.number_input("Dosya Başına Ort. Hasar Maliyeti", value=7500)
satis_hedefi = st.sidebar.slider("Aylık Poliçe Satış Hedefi", 50, 500, 100)

st.sidebar.markdown('<p class="alt-baslik">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)
hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown('<p class="alt-baslik">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25)
if kar_marji < 15: 
    st.sidebar.warning("⚠️ Rekabetçi Mod: Risk yüksek!")
elif 15 <= kar_marji <= 35: 
    st.sidebar.info("✅ Dengeli Mod: İdeal seviye.")
else: 
    st.sidebar.success("🛡️ Güvenli Mod: Minimum risk.")

st.sidebar.markdown('<p class="alt-baslik">🏢 Risk & Simülasyon</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0)
st.sidebar.info(f"🛡️ Şirket Riski: %{100 - reasurans_orani}")
analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

# --- MATEMATİKSEL ÖN HESAPLAR ---
s_h = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / s_h
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
net_gelir = tavsiye_prim * s_h * (1 - (reasurans_orani/100))
net_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# --- 5. ANA EKRAN BUTONU VE ANALİZ ---
st.info("👈 Lütfen sol panelden verilerinizi girin ve analizi başlatmak için aşağıdaki dev butona tıklayın.")

if st.button("🚀 AKTÜERYAL SİMÜLASYONU BAŞLAT (5.000 Senaryo)"):
    with st.spinner("Model hesaplanıyor, lütfen bekleyin..."):
        aylar = analiz_suresi * 12
        sim_n = 5000 
        tablo = np.zeros((aylar + 1, sim_n))
        tablo[0, :] = sermaye
        
        for ay in range(aylar):
            g_sim = np.random.poisson(s_h, sim_n) * tavsiye_prim * (1 - (reasurans_orani/100))
            h_sim = np.random.poisson(hasar_ort, sim_n)
            gi_sim = np.zeros(sim_n)
            for s in range(sim_n):
                if h_sim[s] > 0:
                    gi_sim[s] = np.sum(np.random.exponential(maliyet, h_sim[s]))
            gi_sim = gi_sim * (1 - (reasurans_orani/100))
            tablo[ay+1, :] = tablo[ay, :] + g_sim - gi_sim

        iflas_sayisi = np.sum(np.min(tablo, axis=0) < 0)
        iflas_riski = (iflas_sayisi / sim_n) * 100
        loss_ratio = (net_gider / (net_gelir if net_gelir > 0 else 1)) * 100
        ortalama_kasa = np.mean(tablo[-1, :])

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Önerilen Prim", f"{tavsiye_prim:,.0f} TL")
        if iflas_riski < 5:
            c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="GÜVENLİ")
        else:
            c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="RİSKLİ", delta_color="inverse")
        c3.metric("Loss Ratio", f"%{loss_ratio:.1f}")
        c4.metric("Tahmini Kasa", f"{ortalama_kasa:,.0f} TL")

        st.markdown("---")
        st.subheader("💡 Aktüeryal Analiz Raporu")
        col_a, col_b = st.columns(2)
        with col_a:
            if iflas_riski > 1:
                en_kotu = np.percentile(tablo[-1, :], 1)
                ek_sermaye = abs(min(0, en_kotu))
                st.error(f"**Sermaye Önerisi:** Yaklaşık {ek_sermaye:,.0f} TL ek kaynak gerekebilir.")
            else:
                st.success("**Sermaye Durumu:** Mevcut sermaye yapınız güçlü.")
        with col_b:
            if loss_ratio > 85:
                st.warning(f"**Karlılık Notu:** %{loss_ratio:.1f}. Fiyat artışı önerilir.")
            else:
                st.info(f"**Karlılık Notu:** %{loss_ratio:.1f}. Hasar/Prim dengesi sağlıklı.")

        with st.expander("🧐 Loss Ratio (Hasar/Prim Oranı) Nedir?"):
            st.latex(r"Loss\ Ratio = \frac{Toplam\ Hasar\ Maliyeti}{Toplam\ Kazanılan\ Prim} \times 100")

        st.subheader(f"📈 {analiz_suresi} Yıllık Sermaye Projeksiyonu")
        fig = go.Figure()
        x_ax = list(range(aylar + 1))
        for i in range(min(100, sim_n)):
            fig.add_trace(go.Scatter(x=x_ax, y=tablo[:, i], mode='lines', line=dict(width=1), opacity=0.15, showlegend=False))

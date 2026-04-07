import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# Akıllı Tasarım: Bilgisayarda Dev, Mobilde Esnek
st.markdown(
    """
    <style>
    /* BİLGİSAYARDA (ASUS TUF GİBİ) TASARIM */
    @media (min-width: 1024px) {
        [data-testid="stSidebar"] { 
            min-width: 380px !important; 
            max-width: 380px !important; 
        }
        .main .block-container {
            padding-left: 5rem !important;
            padding-right: 5rem !important;
        }
    }

    /* MOBİLDE (XIAOMI, IPHONE VB.) TASARIM */
    @media (max-width: 1023px) {
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 1rem !important;
        }
    }

    /* YAZI BOYUTLARI VE RENKLER (İSTEDİĞİN GİBİ BÜYÜK) */
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
        margin-top: 20px;
    }

    /* Metrik Değerlerini Büyük Tut */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. ANA EKRAN ---
st.title("🛡️ Sigorta Risk Analizi & Fiyatlandırma Paneli")
st.markdown("Bu panel, finansal sağlığınızı **Stokastik Simülasyon** (Monte Carlo) yöntemleriyle analiz eder.")
st.markdown("---")

# --- 3. YAN PANEL: VERİ GİRİŞİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Merkezi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin nakit rezervi."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Severity (Şiddet) tahmini."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100,
    help="Aylık beklenen yeni poliçe adedi."
)

st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Sayıları</p>', unsafe_allow_html=True)
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay Adedi", value=35+(i*2), min_value=0)
    h_verileri.append(val)
hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown('<p class="sidebar-subheader">💰 Risk & Kâr</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25)
reasurans_orani = st.sidebar.slider("Risk Devir Oranı (Reasürans %)", 0, 90, 0)
analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

# --- 4. HESAPLAMALAR ---
s_h = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / s_h
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
net_gelir = tavsiye_prim * s_h * (1 - (reasurans_orani / 100))
net_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani / 100))

# --- 5. BUTON VE ANALİZ (SONUÇLAR SADECE BURADA) ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT"):
    with st.spinner("5.000 senaryo analiz ediliyor..."):
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

        # Büyük Metrik Kartları
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Önerilen Prim", f"{tavsiye_prim:,.0f} TL")
        m2.metric("İflas Riski", f"%{iflas_riski:.2f}")
        m3.metric("Loss Ratio", f"%{loss_ratio:.1f}")
        m4.metric("Tahmini Kasa", f"{ortalama_kasa:,.0f} TL")

        st.markdown("---")
        
        # Grafik (Telefonda Yarım Kalmaz)
        st.subheader(f"📈 {analiz_suresi} Yıllık Sermaye Projeksiyonu")
        fig = go.Figure()
        x_ax = list(range(aylar + 1))
        for i in range(min(100, sim_n)):
            fig.add_trace(go.Scatter(x=x_ax, y=tablo[:, i], mode='lines', line=dict(width=1), opacity=0.15, showlegend=False))
        fig.add_trace(go.Scatter(x=x_ax, y=np.mean(tablo, axis=1), mode='lines', name='Ortalama', line=dict(color='yellow', width=3)))
        fig.add_trace(go.Scatter(x=x_ax, y=[0]*(aylar+1), mode='lines', name='İflas Sınırı', line=dict(color='red', width=2, dash='dash')))
        fig.update_layout(xaxis_title="Aylar", yaxis_title="Kasa (TL)", template="plotly_dark", height=600, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # Aktüeryal Rapor
        st.subheader("💡 Aktüeryal Değerlendirme")
        col_a, col_b = st.columns(2)
        with col_a:
            if iflas_riski > 2:
                st.error(f"Sermaye Yeterliliği: Riskli seviye. Ek sermaye gerekebilir.")
            else:
                st.success("Sermaye Yeterliliği: Mevcut rezervler güvenli.")
        with col_b:
            st.info(f"Teknik Kârlılık: Loss Ratio %{loss_ratio:.1f}")
            
        with st.expander("🧐 Formül Detayları"):
            st.latex(r"Loss\ Ratio = \frac{E[Hasar]}{E[Prim]} \times 100")

else:
    st.info("📊 Soldaki menüden verileri girip, 'ANALİZİ BAŞLAT' butonuna tıklayın.")

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Sidebar Tasarımı
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

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25)

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">🏢 Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0)
st.sidebar.info(f"🛡️ Şirket Üzerindeki Risk: %{100 - reasurans_orani}")

st.sidebar.markdown("---")
st.sidebar.markdown('<p class="sidebar-subheader">⏱️ Simülasyon Ayarı</p>', unsafe_allow_html=True)
analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

# --- MATEMATİKSEL HESAPLAMALAR ---
satis_h = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / satis_h
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
net_satis_geliri = tavsiye_prim * satis_h * (1 - (reasurans_orani/100))
net_beklenen_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# --- SİMÜLASYON ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT"):
    aylar = analiz_suresi * 12
    sim_n = 5000 
    tablo = np.zeros((aylar + 1, sim_n))
    tablo[0, :] = sermaye
    
    for ay in range(aylar):
        gelir = np.random.poisson(satis_h, sim_n) * tavsiye_prim * (1 - (reasurans_orani/100))
        hasar_sayisi = np.random.poisson(hasar_ort, sim_n)
        gider = np.zeros(sim_n)
        for s in range(sim_n):
            if hasar_sayisi[s] > 0:
                gider[s] = np.sum(np.random.exponential(maliyet, hasar_sayisi[s]))
        gider = gider * (1 - (reasurans_orani/100))
        tablo[ay + 1, :] = tablo[ay, :] + gelir - gider

    iflas_sayisi = np.sum(np.min(tablo, axis=0) < 0)
    iflas_riski = (iflas_sayisi / sim_n) * 100
    denom = net_satis_geliri if net_satis_geliri > 0 else 1
    loss_ratio = (net_beklenen_gider / denom) * 100
    ortalama_kasa = np.mean(tablo[-1, :])

    # --- SONUÇ KARTLARI ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Önerilen Prim", f"{tavsiye_prim:,.0f} TL")
    if iflas_riski < 5:
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="GÜVENLİ")
    else:
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="RİSKLİ", delta_color="inverse")
        
    c3.metric("Loss Ratio (Hasar/Prim)", f"%{loss_ratio:.1f}")
    c4.metric("Ortalama Kasa", f"{ortalama_kasa:,.0f} TL")

    st.markdown("---")
    st.subheader("💡 Aktüeryal Analiz Raporu")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if iflas_riski > 1:
            en_kotu = np.percentile(tablo[-1, :], 1)
            ek_sermaye = abs(min(0, en_kotu))
            st.error(f"**Sermaye Önerisi:** İflas riskini önlemek için yaklaşık **{ek_sermaye:,.0f} TL** ek sermaye gerekebilir.")
        else:
            st.success("**Sermaye Durumu:** Şirket sermayesi çok güçlü.")
            
    with col_b:
        # LOSS RATIO AÇIKLAMASI BURADA
        if loss_ratio > 100:
            st.error(f"**Karlılık Notu (Loss Ratio):** %{loss_ratio:.1f}. Teknik zarar! Hasar ödemeleri prim gelirini aşıyor. Acil prim artışı şart.")
        elif 85 < loss_ratio <= 100:
            st.warning(f"**Karlılık Notu (Loss Ratio):** %{loss_ratio:.1f}. Sınırda! Teknik kâr çok düşük, operasyonel giderler karşılanamayabilir.")
        else:
            st.info(f"**Karlılık Notu (Loss Ratio):** %{loss_ratio:.1f}. Sağlıklı! Prim gelirleriniz hasarları karşılıyor ve kâr bırakıyor.")

    # --- LOSS RATIO NEDİR? (Şov Kısmı) ---
    with st.expander("🧐 Loss Ratio (Hasar/Prim Oranı) Nedir?"):
        st.write("Sigortacılıkta başarının en temel göstergesidir. Şu formülle hesaplanır:")
        st.latex(r"Loss\ Ratio = \frac{Toplam\ Hasar\ Maliyeti}{Toplam\ Kazanılan\ Prim} \times 100")
        st.write("""
        - **%100'den Büyük:** Şirket topladığı her 100 TL prim için 100 TL'den fazla hasar ödüyor demektir (Zarar).
        - **%100'den Küçük:** Şirket hasarları ödedikten sonra elinde para kalıyor demektir (Kâr).
        - **İdeal Seviye:** Genellikle %70 - %85 arasıdır (Geri kalan %15-30 operasyonel giderler ve kâr içindir).
        """)

    # --- PLOTLY GRAFİK ---
    st.subheader(f"📈 {analiz_suresi} Yıllık Sermaye Gelişimi")
    fig = go.Figure()
    x_ekseni = list(range(aylar + 1))
    for i in range(min(100, sim_n)):
        fig.add_trace(go.Scatter(x=x_ekseni, y=tablo[:, i], mode='lines', line=dict(width=1), opacity=0.2, showlegend=False))
    fig.add_trace(go.Scatter(x=x_ekseni, y=np.mean(tablo, axis=1), mode='lines', name='Ortalama Beklenti', line=dict(color='yellow', width=3)))
    fig.add_trace(go.Scatter(x=x_ekseni, y=[0]*(aylar+1), mode='lines', name='İflas Sınırı', line=dict(color='red', width=2, dash='dash')))
    fig.update_layout(xaxis_title="Aylar", yaxis_title="Kasa Bakiyesi (TL)", template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📊 Başlamak için soldaki verileri kontrol edin ve 'ANALİZİ BAŞLAT' butonuna tıklayın.")

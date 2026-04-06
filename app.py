import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# --- 2. CSS (Tasarım Ayarları) ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { 
        min-width: 380px; 
        max-width: 380px; 
    }
    .sidebar-header { 
        font-size: 30px !important; 
        font-weight: 800; 
        color: #00D1B2; 
        margin-top: 10px; 
        margin-bottom: 10px;
    }
    .sidebar-subheader { 
        font-size: 24px !important; 
        font-weight: 700; 
        color: #F0F2F6; 
        margin-top: 15px; 
        margin-bottom: 10px;
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

# --- 3. ANA EKRAN ÜST KISIM ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("---")

# --- 4. YAN PANEL (VERİ GİRİŞLERİ) ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=1500000, step=50000)
maliyet = st.sidebar.number_input("Dosya Başına Ort. Hasar Maliyeti", value=7500)
satis_hedefi = st.sidebar.slider("Aylık Poliçe Satış Hedefi", 50, 500, 100)

st.sidebar.markdown("---")

st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(str(i+1) + ". Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)
hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---")

st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25)

if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod: Risk yüksek!")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod: İdeal seviye.")
else:
    st.sidebar.success("🛡️ Güvenli Mod: Minimum risk.")

st.sidebar.markdown("---")

st.sidebar.markdown('<p class="sidebar-subheader">🏢 Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0)
st.sidebar.info("🛡️ Şirket Üzerindeki Risk: %" + str(100 - reasurans_orani))

st.sidebar.markdown("---")

st.sidebar.markdown('<p class="sidebar-subheader">⏱️ Simülasyon Ayarı</p>', unsafe_allow_html=True)
analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

st.sidebar.markdown("---")

# --- 5. MATEMATİKSEL ÖN HESAPLAR ---
s_h = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / s_h
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))
net_gelir = tavsiye_prim * s_h * (1 - (reasurans_orani / 100))
net_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani / 100))

# --- 6. BUTON VE ANALİZ ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT", use_container_width=True):
    with st.spinner("Model hesaplanıyor, lütfen bekleyin..."):
        aylar = analiz_suresi * 12
        sim_n = 5000 
        tablo = np.zeros((aylar + 1, sim_n))
        tablo[0, :] = sermaye
        
        for ay in range(aylar):
            g_sim = np.random.poisson(s_h, sim_n) * tavsiye_prim * (1 - (reasurans_orani / 100))
            h_sim = np.random.poisson(hasar_ort, sim_n)
            gi_sim = np.zeros(sim_n)
            for s in range(sim_n):
                if h_sim[s] > 0:
                    gi_sim[s] = np.sum(np.random.exponential(maliyet, h_sim[s]))
            gi_sim = gi_sim * (1 - (reasurans_orani / 100))
            tablo[ay+1, :] = tablo[ay, :] + g_sim - gi_sim

        iflas_sayisi = np.sum(np.min(tablo, axis=0) < 0)
        iflas_riski = (iflas_sayisi / sim_n) * 100
        denom = net_gelir if net_gelir > 0 else 1
        loss_ratio = (net_gider / denom) * 100
        ortalama_kasa = np.mean(tablo[-1, :])

        # --- SONUÇ KARTLARI ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Önerilen Prim", f"{tavsiye_prim:,.0f} TL")
        
        if iflas_riski < 5:
            c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="GÜVENLİ")
        else:
            c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="RİSKLİ", delta_color="inverse")
            
        c3.metric("Loss Ratio", f"%{loss_ratio:.1f}")
        c4.metric("Tahmini Kasa", f"{ortalama_kasa:,.0f} TL")

        st.markdown("---")
        
        # --- AKTÜERYAL RAPOR ---
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

        # --- LOSS RATIO AÇIKLAMASI ---
        with st.expander("🧐 Loss Ratio (Hasar/Prim Oranı) Nedir?"):
            st.write("Sigortacılıkta başarının en temel göstergesidir:")
            st.latex(r"Loss\ Ratio = \frac{Toplam\ Hasar\ Maliyeti}{Toplam\ Kazanılan\ Prim} \times 100")
            st.write("- **%100+:** Zarar. - **%85 Altı:** Sağlıklı Teknik Kâr.")

        # --- GRAFİK ---
        st.subheader(f"📈 {analiz_suresi} Yıllık Sermaye Projeksiyonu")
        fig = go.Figure()
        x_ax = list(range(aylar + 1))
        
        for i in range(min(100, sim_n)):
            fig.add_trace(go.Scatter(x=x_ax, y=tablo[:, i], mode='lines', line=dict(width=1), opacity=0.15, showlegend=False))
            
        fig.add_trace(go.Scatter(x=x_ax, y=np.mean(tablo, axis=1), mode='lines', name='Ortalama', line=dict(color='yellow', width=3)))
        fig.add_trace(go.Scatter(x=x_ax, y=[0]*(aylar+1), mode='lines', name='İflas Sınırı', line=dict(color='red', width=2, dash='dash')))
        
        fig.update_layout(xaxis_title="Aylar", yaxis_title="Kasa (TL)", template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📊 Soldaki menüden verileri girip, en alttaki 'ANALİZİ BAŞLAT' butonuna tıklayın.")

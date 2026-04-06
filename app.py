import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# Sidebar ve Buton Tasarımı
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
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. ANA EKRAN ÜST KISIM ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("Bu panel, finansal sağlığınızı **Stokastik Simülasyon** (Monte Carlo) yöntemleriyle analiz eder.")
st.markdown("---")

# --- 3. YAN PANEL: VERİ GİRİŞ MERKEZİ ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Giriş Merkezi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin hasarları ödemek için hazırda tuttuğu toplam nakit rezervidir."
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
st.sidebar.caption("Gelecekteki hasar sıklığını (Frequency) tahmin etmek için son 6 aylık verileri giriniz.")

h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(
        f"{i+1}. Ay Adedi", 
        value=35+(i*2), 
        min_value=0,
        help=f"{i+1}. ayda gerçekleşen toplam hasar dosyası sayısı."
    )
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

# --- 6. YAN PANEL: RİSK YÖNETİMİ ---
st.sidebar.markdown('<p class="sidebar-subheader">🏢 Gelişmiş Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider(
    "Risk Devir Oranı (%)", 
    0, 90, 0,
    help="Hasarların ne kadarını başka bir reasüröre devretmek istiyorsunuz?"
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
net_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani / 100))

# --- 9. BUTON VE ANALİZ ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT"):
    with st.spinner("5.000 senaryo simüle ediliyor..."):
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

        # Sonuç Kartları
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Önerilen Prim", f"{tavsiye_prim:,.0f} TL")
        if iflas_riski < 5:
            c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="GÜVENLİ")
        else:
            c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="RİSKLİ", delta_color="inverse")
        c3.metric("Loss Ratio", f"%{loss_ratio:.1f}")
        c4.metric("Tahmini Kasa", f"{ortalama_kasa:,.0f} TL")

        st.markdown("---")
        
        # Aktüeryal Rapor
        st.subheader("💡 Aktüeryal Değerlendirme & Reçete")
        col_a, col_b = st.columns(2)
        with col_a:
            if iflas_riski > 1:
                en_kotu = np.percentile(tablo[-1, :], 1)
                ek_sermaye = abs(min(0, en_kotu))
                st.error(f"**Sermaye:** Riski düşürmek için ~{ek_sermaye:,.0f} TL ek kaynak gerekebilir.")
            else:
                st.success("**Sermaye:** Şirketiniz finansal olarak oldukça sağlam durumda.")
        with col_b:
            if loss_ratio > 85:
                st.warning(f"**Karlılık:** %{loss_ratio:.1f}. Hasar/Prim dengesi zayıf. Prim artışı önerilir.")
            else:
                st.info(f"**Karlılık:** %{loss_ratio:.1f}. Hasar/Prim dengesi sağlıklı.")

        # Loss Ratio Açıklaması
        with st.expander("🧐 Loss Ratio (Hasar/Prim Oranı) Nedir?"):
            st.write("Şirketin operasyonel başarısını ölçen temel aktüeryal göstergedir:")
            st.latex(r"Loss\ Ratio = \frac{Toplam\ Hasar\ Maliyeti}{Toplam\ Kazanılan\ Prim} \times 100")
            st.write("- **%100+:** Teknik zarar durumu. - **%85 Altı:** Sağlıklı teknik kâr.")

        # Grafik
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
    st.info("📊 Soldaki menüden verileri girip, en alttaki 'ANALİZİ BAŞLAT' butonuna tıklayın. Soru işaretlerinden (?) yardım alabilirsiniz.")

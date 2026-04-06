import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Sidebar Tasarımı (CSS ile Şov Başlıyor)
st.markdown(
    """
    <style>
    /* Sol Panel Genişliği */
    [data-testid="stSidebar"] {
        min-width: 380px;
        max-width: 380px;
    }
    /* Ana Başlık Stili */
    .sidebar-header {
        font-size: 32px !important;
        font-weight: 800;
        color: #00D1B2;
        margin-bottom: 15px;
        margin-top: 10px;
        line-height: 1.2;
    }
    /* Alt Başlık Stilleri */
    .sidebar-subheader {
        font-size: 26px !important;
        font-weight: 700;
        color: #F0F2F6;
        margin-bottom: 12px;
        margin-top: 15px;
        line-height: 1.2;
    }
    /* Metinlerin Başlıkla Arasındaki Boşluk */
    .stNumberInput, .stSlider {
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- ANA EKRAN ÜST KISIM ---
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("---")

# --- YAN PANEL: 1. BÖLÜM - TEMEL VERİLER ---
st.sidebar.markdown('<p class="sidebar-header">📊 Veri Girişi</p>', unsafe_allow_html=True)

sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)", 
    value=1500000, 
    step=50000,
    help="Şirketin hasarları ödemek için kasasında hazır tuttuğu toplam nakittir."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Gerçekleşen her bir hasar dosyasının şirkete ortalama maliyetidir (Severity)."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100,
    help="Her ay satmayı planladığınız yeni poliçe sayısıdır. Satış arttıkça prim geliri artar."
)

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# --- YAN PANEL: 2. BÖLÜM - HASAR FREKANSI ---
st.sidebar.markdown('<p class="sidebar-subheader">📉 Hasar Frekansı</p>', unsafe_allow_html=True)
st.sidebar.caption("Son 6 aylık hasar adetlerini giriniz:")

h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# --- YAN PANEL: 3. BÖLÜM - FİYATLANDIRMA ---
st.sidebar.markdown('<p class="sidebar-subheader">💰 Fiyatlandırma</p>', unsafe_allow_html=True)
kar_marji = st.sidebar.slider(
    "Hedeflenen Kâr Marjı (%)", 
    0, 100, 25,
    help="Beklenen hasar maliyetinin üzerine eklenen güvenlik payıdır (Security Loading)."
)

if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi Mod: Risk yüksek!")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli Mod: İdeal seviye.")
else:
    st.sidebar.success("🛡️ Güvenli Mod: Minimum risk.")

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# --- YAN PANEL: 4. BÖLÜM - RISK YÖNETİMİ ---
st.sidebar.markdown('<p class="sidebar-subheader">🏢 Risk Yönetimi</p>', unsafe_allow_html=True)
reasurans_orani = st.sidebar.slider(
    "Risk Devir Oranı (%)", 
    0, 90, 0,
    help="Hasarların ve primlerin ne kadarını başka bir şirkete devretmek istiyorsunuz?"
)
st.sidebar.info(f"🛡️ Şirket Üzerindeki Risk: %{100 - reasurans_orani}")

st.sidebar.markdown("---") # AYIRICI ÇİZGİ

# --- YAN PANEL: 5. BÖLÜM - SİMÜLASYON AYARLARI ---
st.sidebar.markdown('<p class="sidebar-subheader">⏱️ Simülasyon Ayarı</p>', unsafe_allow_html=True)
analiz_suresi = st.sidebar.slider(
    "Analiz Süresi (Yıl)", 
    1, 5, 3,
    help="Gelecekte kaç yıllık bir finansal projeksiyon görmek istiyorsunuz?"
)

# --- MATEMATİKSEL HESAPLAMALAR ---
# Payda sıfır hatasını önlemek için kontrol
satis_h = satis_hedefi if satis_hedefi > 0 else 1
saf_prim = (hasar_ort * maliyet) / satis_h
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))

# Reasürans sonrası net rakamlar
net_satis_geliri = tavsiye_prim * satis_h * (1 - (reasurans_orani/100))
net_beklenen_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# --- SİMÜLASYON MOTORU ---
if st.sidebar.button("🚀 ANALİZİ BAŞLAT"):
    aylar = analiz_suresi * 12
    sim_n = 5000 
    tablo = np.zeros((aylar + 1, sim_n))
    tablo[0, :] = sermaye
    
    for ay in range(aylar):
        # Gelir Simülasyonu
        gelir = np.random.poisson(satis_h, sim_n) * tavsiye_prim * (1 - (reasurans_orani/100))
        # Hasar Sayısı Simülasyonu
        hasar_sayisi = np.random.poisson(hasar_ort, sim_n)
        
        # Hasar Maliyeti Simülasyonu
        gider = np.zeros(sim_n)
        for s in range(sim_n):
            if hasar_sayisi[s] > 0:
                gider[s] = np.sum(np.random.exponential(maliyet, hasar_sayisi[s]))
        
        gider = gider * (1 - (reasurans_orani/100))
        tablo[ay + 1, :] = tablo[ay, :] + gelir - gider

    # Analitik Sonuçlar
    iflas_sayisi = np.sum(np.min(tablo, axis=0) < 0)
    iflas_riski = (iflas_sayisi / sim_n) * 100
    denom = net_satis_geliri if net_satis_geliri > 0 else 1
    loss_ratio = (net_beklenen_gider / denom) * 100
    ortalama_kasa = np.mean(tablo[-1, :])

    # --- SONUÇ KARTLARI ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Önerilen Prim", f"{tavsiye_prim:,.0f} TL")
    
    if iflas_riski < 5:
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="GÜVENLİ", delta_color="normal")
    else:
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="RİSKLİ", delta_color="inverse")
        
    c3.metric("Loss Ratio", f"%{loss_ratio:.1f}")
    c4.metric("Ortalama Kasa", f"{ortalama_kasa:,.0f} TL")

    st.markdown("---")
    st.subheader("💡 Aktüeryal Analiz Raporu")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if iflas_riski > 1:
            en_kotu = np.percentile(tablo[-1, :], 1)
            ek_sermaye = abs(min(0, en_kotu))
            st.error(f"**Sermaye Önerisi:** Riski %1'in altına düşürmek için yaklaşık **{ek_sermaye:,.0f} TL** ek sermaye gerekebilir.")
        else:
            st.success("**Sermaye Durumu:** Şirket sermayesi mevcut riskleri karşılamak için fazlasıyla yeterli.")
            
    with col_b:
        if loss_ratio > 85:
            st.warning("**Karlılık Notu:** Hasar/Prim oranı yüksek. Teknik kâr elde etmek için primleri artırmanız önerilir.")
        else:
            st.info("**Karlılık Notu:** Hasar/Prim dengesi sağlıklı. Operasyonel sürdürülebilirlik yüksek.")

    # --- PLOTLY İNTERAKTİF GRAFİK ---
    st.subheader(f"📈 {analiz_suresi} Yıllık Sermaye Gelişimi (Stokastik Projeksiyon)")
    fig = go.Figure()
    x_ekseni = list(range(aylar + 1))
    
    # Senaryo Çizgileri
    for i in range(min(100, sim_n)):
        fig.add_trace(go.Scatter(x=x_ekseni, y=tablo[:, i], mode='lines', line=dict(width=1), opacity=0.2, showlegend=False))
    
    # Ortalama Beklenti
    fig.add_trace(go.Scatter(x=x_ekseni, y=np.mean(tablo, axis=1), mode='lines', name='Ortalama Beklenti', line=dict(color='yellow', width=3)))
    
    # İflas Sınırı
    fig.add_trace(go.Scatter(x=x_ekseni, y=[0]*(aylar+1), mode='lines', name='İflas Sınırı (0 TL)', line=dict(color='red', width=2, dash='dash')))
    
    fig.update_layout(xaxis_title="Aylar", yaxis_title="Kasa Bakiyesi (TL)", hovermode="x unified", template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📊 Başlamak için soldaki verileri kontrol edin ve 'ANALİZİ BAŞLAT' butonuna tıklayın. Soru işaretlerinden (?) detaylı bilgi alabilirsiniz.")

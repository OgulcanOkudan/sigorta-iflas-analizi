import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Sidebar Genişliğini ve Başlık Boyutlarını Ayarlayan CSS
st.markdown(
    """
    <style>
    /* Sol Panel Genişliği (Tam kıvamında: 380px) */
    [data-testid="stSidebar"] {
        min-width: 380px;
        max-width: 380px;
    }
    /* Sidebar Başlık Stilleri */
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
    help="Şirketin tüm hasarları ödemek için hazırda bulundurduğu toplam nakit rezervidir. Kasanız ne kadar doluysa, risklere karşı o kadar dirençli olursunuz."
)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Dosya başına düşen ortalama hasar tutarıdır (Severity). Örn: Toplam Tazminat / Toplam Hasar Dosya Sayısı."
)
satis_hedefi = st.sidebar.slider(
    "Aylık Poliçe Satış Hedefi", 
    50, 500, 100,
    help="Her ay kaç adet yeni sigorta poliçesi satmayı hedefliyorsunuz? Satış arttıkça prim geliri artar ancak risk dağılımı da değişir."
)

# 2. Geçmiş Hasar Verileri
st.sidebar.markdown('<p class="sidebar-subheader">📉 Son 6 Aylık Hasar Sayıları</p>', unsafe_allow_html=True)
st.sidebar.caption("Gelecekteki hasar sıklığını (Frequency) tahmin etmek için son 6 aylık adetleri giriniz.")
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
    help="Aktüeryal dilde 'Security Loading'dir. Beklenen hasarların üzerine, belirsizlikleri ve operasyonel giderleri karşılamak için eklenen emniyet payıdır."
)

# Dinamik Rehberlik Metni
if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi: Pazar payı artar ama risk yüksektir.")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli: İdeal kâr ve güvenlik dengesi.")
else:
    st.sidebar.success("🛡️ Güvenli: İflas riski minimum, primler yüksek.")

# 4. Reasürans & Süre
with st.sidebar.expander("🏢 Gelişmiş Risk Yönetimi"):
    reasurans_orani = st.sidebar.slider(
        "Risk Devir Oranı (%)", 
        0, 90, 0,
        help="Büyük hasar risklerini başka bir şirkete (reasüröre) devrederek sermayenizi koruma yöntemidir. Hasarın bir kısmını onlar öder, siz de primin bir kısmını onlara verirsiniz."
    )
    analiz_suresi = st.sidebar.slider(
        "Analiz Süresi (Yıl)", 
        1, 5, 3,
        help="Simülasyonun ne kadar ileriye dönük bir gelecek tahmini yapacağını belirler."
    )

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
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="GÜVENLİ", delta_color="normal")
    else:
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="RİSKLİ", delta_color="inverse")
    c3.metric("Loss Ratio (Hasar/Prim)", f"%{loss_ratio:.1f}")
    c4.metric("Tahmini Kasa", f"{ortalama_kasa:,.0f} TL")

    st.markdown("---")
    st.subheader("💡 Aktüeryal Değerlendirme & Reçete")
    col_a, col_b = st.columns(2)
    with col_a:
        if iflas_riski > 1:
            en_kotu_senaryo = np.percentile(tablo[-1, :], 1)
            ek_sermaye = abs(min(0, en_kotu_senaryo))
            st.error(f"**Sermaye Yeterliliği:** Mevcut risk seviyesi yüksek. Riski %1'in altına çekmek için yaklaşık **{ek_sermaye:,.0f} TL** ek sermaye veya reasürans desteği önerilir.")
        else:
            st.success("**Sermaye Yeterliliği:** Şirketiniz finansal olarak çok sağlam durumda. Mevcut yapı riskleri karşılamak için yeterli.")
    with col_b:
        if loss_ratio > 85:
            st.warning("**Operasyonel Verimlilik:** Loss Ratio çok yüksek. Primlerinizi artırmayı veya maliyetleri düşürmeyi düşünmelisiniz.")
        else:
            st.info("**Operasyonel Verimlilik:** Hasar/Prim dengesi sağlıklı. Şirket kâr üretebiliyor.")

    # --- PLOTLY GRAFİK ---
    st.subheader(f"📈 {analiz_suresi} Yıllık Sermaye Projeksiyonu")
    fig = go.Figure()
    x_ekseni = list(range(

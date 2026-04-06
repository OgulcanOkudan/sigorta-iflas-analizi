import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Aktüeryal Risk & Fiyatlandırma Paneli", layout="wide")

# Şık bir Başlık ve Açıklama
st.title("🛡️ Sigorta Risk Analizi & Akıllı Fiyatlandırma Paneli")
st.markdown("""
Bu panel, bir sigorta şirketinin finansal sağlığını **Stokastik Simülasyon** yöntemleriyle analiz eder. 
Verileri girin, ideal priminizi bulun ve iflas riskinizi yönetin.
""")

# --- YAN PANEL: VERİ GİRİŞİ ---
st.sidebar.header("📊 Veri Giriş Merkezi")

# 1. Sermaye ve Maliyet
sermaye = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=1500000, step=50000)
maliyet = st.sidebar.number_input(
    "Dosya Başına Ort. Hasar Maliyeti", 
    value=7500,
    help="Geçmiş 1 yıllık: Toplam Tazminat / Toplam Dosya Sayısı. (Severity)"
)
satis_hedefi = st.sidebar.slider("Aylık Poliçe Satış Hedefi", 50, 500, 100)

# 2. Geçmiş Hasar Verileri (Frekans)
st.sidebar.subheader("📉 Son 6 Aylık Hasar Sayıları")
h_verileri = []
cols = st.sidebar.columns(2)
for i in range(6):
    val = cols[i%2].number_input(f"{i+1}. Ay", value=35 + (i*2), min_value=0)
    h_verileri.append(val)

hasar_ort = sum(h_verileri) / 6

# 3. Fiyatlandırma Stratejisi
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Fiyatlandırma & Kâr")
kar_marji = st.sidebar.slider("Hedeflenen Kâr Marjı (%)", 0, 100, 25)

# Dinamik Rehberlik Metni
if kar_marji < 15:
    st.sidebar.warning("⚠️ Rekabetçi: Pazar payı artar ama risk yüksektir.")
elif 15 <= kar_marji <= 35:
    st.sidebar.info("✅ Dengeli: İdeal kâr ve güvenlik dengesi.")
else:
    st.sidebar.success("🛡️ Güvenli: İflas riski minimum, primler yüksek.")

# 4. Reasürans (Gizli/Expander)
with st.sidebar.expander("🏢 Reasürans (Risk Paylaşımı)"):
    reasurans_orani = st.sidebar.slider("Risk Devir Oranı (%)", 0, 90, 0, help="Hasarların ve primlerin ne kadarı reasüröre devredilecek?")
    st.write(f"Şirket Riski: %{100-reasurans_orani}")

analiz_suresi = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 5, 3)

# --- HESAPLAMA MOTORU ---
# Saf Prim ve Brüt Prim
saf_prim = (hasar_ort * maliyet) / satis_hedefi
tavsiye_prim = saf_prim * (1 + (kar_marji / 100))

# Reasürans Etkisi (Quota Share)
satis_geliri = tavsiye_prim * satis_hedefi * (1 - (reasurans_orani/100))
beklenen_gider = (hasar_ort * maliyet) * (1 - (reasurans_orani/100))

# --- SİMÜLASYON ---
if st.sidebar.button("🚀 Analizi Başlat"):
    aylar = analiz_suresi * 12
    sim_n = 5000 
    tablo = np.zeros((aylar + 1, sim_n))
    tablo[0, :] = sermaye
    
    # Simülasyon döngüsü
    for ay in range(aylar):
        # Gelir simülasyonu
        gelir = np.random.poisson(satis_hedefi, sim_n) * tavsiye_prim * (1 - (reasurans_orani/100))
        # Hasar sayısı simülasyonu (Poisson)
        hasar_sayisi = np.random.poisson(hasar_ort, sim_n)
        
        # Toplam hasar maliyeti simülasyonu (Üstel Dağılım)
        gider = np.zeros(sim_n)
        for s in range(sim_n):
            if hasar_sayisi[s] > 0:
                gider[s] = np.sum(np.random.exponential(maliyet, hasar_sayisi[s]))
        
        gider = gider * (1 - (reasurans_orani/100))
        tablo[ay + 1, :] = tablo[ay, :] + gelir - gider

    # Analitik Sonuçlar
    iflas_sayisi = np.sum(np.min(tablo, axis=0) < 0)
    iflas_riski = (iflas_sayisi / sim_n) * 100
    loss_ratio = (beklenen_gider / (satis_geliri if satis_geliri > 0 else 1)) * 100
    ortalama_kasa = np.mean(tablo[-1, :])

    # --- EKRAN ÇIKTILARI ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tavsiye Edilen Prim", f"{tavsiye_prim:,.0f} TL")
    
    # İflas Riski Renklendirme
    if iflas_riski < 5:
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="GÜVENLİ", delta_color="normal")
    else:
        c2.metric("İflas Riski", f"%{iflas_riski:.2f}", delta="RİSKLİ", delta_color="inverse")
        
    c3.metric("Loss Ratio (Hasar/Prim)", f"%{loss_ratio:.1f}")
    c4.metric("Tahmini Kasa", f"{ortalama_kasa:,.0f} TL")

    # --- PROFESYONEL TAVSİYE ---
    st.markdown("---")
    st.subheader("💡 Aktüeryal Değerlendirme & Reçete")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if iflas_riski > 1:
            # En kötü %1'lik senaryoyu bulma
            en_kotu_senaryo = np.percentile(tablo[-1, :], 1)
            ek_sermaye = abs(min(0, en_kotu_senaryo))
            st.error(f"**Sermaye Yeterliliği:** Mevcut risk seviyesi yüksek. Riski %1'in altına çekmek için yaklaşık **{ek_sermaye:,.0f} TL** ek sermaye veya daha yüksek reasürans desteği önerilir.")
        else:
            st.success("**Sermaye Yeterliliği:** Şirketiniz finansal olarak çok sağlam durumda. Mevcut prim ve sermaye yapısı riskleri karşılamak için yeterli.")

    with col_b:
        if loss_ratio > 85:
            st.warning("**Operasyonel Verimlilik:** Loss Ratio çok yüksek. Primlerinizi artırmayı veya hasar yönetim süreçlerini gözden geçirmeyi düşünmelisiniz.")
        else:
            st.info("**Operasyonel Verimlilik:** Hasar/Prim dengesi sağlıklı. Bu oran şirketin operasyonel giderlerini karşılamak ve kâr etmek için alan bırakıyor.")

    # --- PLOTLY İNTERAKTİF GRAFİK ---
    st.subheader(f"📈 {analiz_suresi} Yıllık Sermaye Projeksiyonu (5.000 Senaryo)")
    fig = go.Figure()
    
    # Performans için ilk 100 senaryoyu çiz
    x_ekseni = list(range(aylar + 1))
    for i in range(min(100, sim_n)):
        fig.add_trace(go.Scatter(x=x_ekseni, y=tablo[:, i], mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
    
    # Ortalama Beklenti Çizgisi
    fig.add_trace(go.Scatter(x=x_ekseni, y=np.mean(tablo, axis=1), mode='lines', name='Ortalama Beklenti', line=dict(color='yellow', width=3)))
    
    # İflas Sınırı
    fig.add_trace(go.Scatter(x=x_ekseni, y=[0]*(aylar+1), mode='lines', name='İflas Sınırı (0 TL)', line=dict(color='red', width=2, dash='dash')))
    
    fig.update_layout(xaxis_title="Aylar", yaxis_title="Kasa Bakiyesi (TL)", hovermode="x unified", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Yandaki verileri kontrol edin ve analizi başlatmak için butona basın.")

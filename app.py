import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sigorta Risk Analizörü", layout="wide")

st.title("🛡️ Profesyonel Sigorta Risk & İflas Analizörü")
st.markdown("Bu uygulama, gerçek şirket verilerine dayanarak gelecekteki **İflas Riskini** simüle eder.")

# YAN PANEL
st.sidebar.header("📊 Veri Giriş Merkezi")
yontem = st.sidebar.radio("Parametre Belirleme:", ("Manuel Tahmin", "Geçmiş Veriden Hesapla"))

if yontem == "Manuel Tahmin":
    satis_ort = st.sidebar.number_input("Aylık Beklenen Satış", value=100)
    hasar_ort = st.sidebar.number_input("Aylık Beklenen Hasar", value=30)
else:
    st.sidebar.info("Son 6 Ayın Hasar Sayılarını Girin:")
    h_verileri = [st.sidebar.number_input(f"{i+1}. Ay Hasar", value=25+i) for i in range(6)]
    hasar_ort = sum(h_verileri) / 6
    satis_ort = 100
    st.sidebar.success(f"📈 Ort. Hasar: {hasar_ort:.2f}")

st.sidebar.markdown("---")
yil = st.sidebar.slider("Analiz Süresi (Yıl)", 1, 20, 5)
kasa = st.sidebar.number_input("Başlangıç Sermayesi (TL)", value=1000000)
prim = st.sidebar.number_input("Birim Prim (TL)", value=2500)
maliyet = st.sidebar.number_input("Ort. Hasar Maliyeti (TL)", value=6000)

if st.sidebar.button("🚀 Analizi Başlat"):
    aylar = yil * 12
    sim_n = 10000
    tablo = np.zeros((aylar + 1, sim_n))
    tablo[0, :] = kasa
    
    for ay in range(aylar):
        gelir = np.random.poisson(satis_ort, sim_n) * prim
        gider = np.random.poisson(hasar_ort, sim_n) * np.random.exponential(maliyet, sim_n)
        tablo[ay + 1, :] = tablo[ay, :] + gelir - gider
    
    iflas = (np.sum(np.min(tablo, axis=0) < 0) / sim_n) * 100
    
    # METRİKLER
    c1, c2, c3 = st.columns(3)
    c1.metric("Analiz Süresi", f"{yil} Yıl")
    c2.metric("İflas Riski", f"% {iflas:.2f}")
    c3.metric("Tahmini Kasa", f"{np.mean(tablo[-1,:]):,.0f} TL")
    
    # GRAFİK
    st.markdown("---")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(tablo[:, :100], alpha=0.3, color='#3498db')
    ax.axhline(0, color='red', linewidth=2, label="İflas Sınırı")
    ax.set_title(f"{yil} Yıllık Sermaye Akış Simülasyonu")
    st.pyplot(fig)

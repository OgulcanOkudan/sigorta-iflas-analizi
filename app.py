# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# Agresif Mobil ve PC Uyumluluk Ayarı
st.markdown(
    """
    <style>
    /* 1. GENEL EKAN BOŞLUKLARINI SIFIRLAMA (MOBİL ODAKLI) */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* 2. BİLGİSAYARDA (Geniş Ekran) YAN PANEL GENİŞLİĞİ */
    @media (min-width: 1024px) {
        [data-testid="stSidebar"] { 
            min-width: 380px !important; 
            max-width: 380px !important; 
        }
        .main .block-container {
            padding-left: 5rem;
            padding-right: 5rem;
        }
    }

    /* 3. MOBİLDE (Dar Ekran) TÜM BOŞLUKLARI KALDIRMA */
    @media (max-width: 1023px) {
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 1rem !important;
        }
        /* Metriklerin (Önerilen Prim vb.) düzgün görünmesi için */
        [data-testid="stMetric"] {
            width: 100% !important;
            margin-bottom: 10px;
        }
    }

    /* TASARIM ÖGELERİ (BUTON VE BAŞLIK) */
    .sidebar-header { font-size: 28px; font-weight: 800; color: #00D1B2; }
    .sidebar-subheader { font-size: 20px; font-weight: 700; color: #F0F2F6; }
    
    div.stButton > button {
        background-color: #00D1B2 !important;
        color: white !important;
        font-weight: bold !important;
        height: 50px !important;
        border-radius: 10px !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

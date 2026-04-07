import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aktüeryal Risk Paneli", layout="wide")

# Akıllı Responsive (Duyarlı) Tasarım
st.markdown(
    """
    <style>
    /* BİLGİSAYAR (Büyük Ekran) AYARLARI */
    @media (min-width: 1024px) {
        [data-testid="stSidebar"] { 
            min-width: 380px !important; 
            max-width: 380px !important; 
        }
    }

    /* MOBİL VE TABLET (Küçük Ekran) AYARLARI */
    @media (max-width: 1023px) {
        [data-testid="stSidebar"] { 
            min-width: 100% !important; 
        }
        .sidebar-header { font-size: 24px !important; }
        .sidebar-subheader { font-size: 18px !important; }
    }

    /* ORTAK TASARIM ÖGELERİ */
    .sidebar-header { font-size: 32px; font-weight: 800; color: #00D1B2; margin-bottom: 10px; }
    .sidebar-subheader { font-size: 24px; font-weight: 700; color: #F0F2F6; margin-top: 15px; }
    
    div.stButton > button {
        background-color: #00D1B2 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 55px !important;
        border-radius: 10px !important;
        width: 100% !important;
    }

    /* Metrik kartlarının mobilde patlamaması için */
    [data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #31333F;
    }
    </style>
    """,
    unsafe_allow_html=True
)

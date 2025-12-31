import streamlit as st
import random
import requests
import pandas as pd

# 1. INICIALIZAÇÃO DE MEMÓRIA (Session State)
if 'total_gerado' not in st.session_state:
    st.session_state.total_gerado = 0
if 'historico_premios' not in st.session_state:
    st.session_state.historico_premios = {"Sena": 0, "Quina": 0, "Quadra": 0}

st.set_page_config(page_title="Mega-Sena Premium v2", page_icon="📈", layout="wide")

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #004691; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .bola { background-color: #ffab00; color: #004691; padding: 12px; border-radius: 50%; 
            text-align: center; font-weight: bold; width: 45px; height: 45px; display: inline-block; margin: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE BUSCA ---
@st.cache_data(ttl=3600)
def obter_resultado():
    try:
        r = requests.get("https://loteriascaixa-api.herokuapp.com/api/megasena/latest")
        return r.json() if r.status_code == 200 else None
    except: return None

resultado_real = obter_resultado()

# --- PAINEL DE ESTATÍSTICAS (DASHBOARD) ---
st.title("📈 Painel de Performance Mega-Sena")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><h3>Total Gerado</h3><h2>{st.session_state.total_gerado}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-left-color: gold;"><h3>Senas</h3><h2>{st.session_state.historico_premios["Sena"]}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-left-color: silver;"><h3>Quinas</h3><h2>{st.session_state.historico_premios["Quina"]}</h2></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card" style="border-left-color: #cd7f32;"><h3>Quadras</h3><h2>{st.session_state.historico_premios["Quadra"]}</h2></div>', unsafe_allow_html=True)

st.divider()

tab1, tab2 = st.tabs(["🎲 Gerador de Apostas", "🔍 Verificador e Histórico"])

with tab1:
    qtd = st.number_input("Quantidade de jogos:", 1, 50, 5)
    if st.button("Gerar e Registrar"):
        st.session_state.total_gerado += qtd
        for _ in range(qtd):
            jogo = sorted(random.sample(range(1, 61), 6))
            cols = st.columns(6)
            for i, n in enumerate(jogo):
                cols[i].markdown(f'<div class="bola">{n:02d}</div>', unsafe_allow_html=True)
        st.rerun() # Atualiza os números no topo instantaneamente

with tab2:
    if resultado_real:
        st.write(f"Conferindo com Concurso **{resultado_real['concurso']}**")
        aposta = st.text_input("Cole sua aposta para validar e salvar no histórico:")
        
        if st.button("Validar e Contabilizar"):
            nums = [int(n) for n in aposta.replace(',', ' ').split() if n.strip()]
            if len(nums) == 6:
                acertos = len(set(nums).intersection(set([int(x) for x in resultado_real['dezenas']])))
                
                if acertos == 6: st.session_state.historico_premios["Sena"] += 1
                elif acertos == 5: st.session_state.historico_premios["Quina"] += 1
                elif acertos == 4: st.session_state.historico_premios["Quadra"] += 1
                
                st.success(f"Você teve {acertos} acertos!")
                st.rerun()
    else:
        st.error("API offline. Verifique a conexão.")

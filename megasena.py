import streamlit as st
import random
import requests

# --- CONFIGURAÇÕES DE VENDA ---
NOME_SISTEMA = "LotoExpert Pro v1.0"
COR_CAIXA_MEGA = "#004691"
COR_CAIXA_LOTO = "#930089" # Roxo característico da Lotofácil

st.set_page_config(page_title=NOME_SISTEMA, page_icon="🍀", layout="wide")

# --- BARRA LATERAL (MENU) ---
st.sidebar.title(f"🎰 {NOME_SISTEMA}")
tipo_loteria = st.sidebar.selectbox("Escolha a Loteria:", ["Mega-Sena", "Lotofácil"])

st.sidebar.divider()
st.sidebar.info("Este gerador usa filtros estatísticos para aumentar suas chances.")

# --- FUNÇÃO: BUSCA RESULTADOS REAIS ---
@st.cache_data(ttl=3600)
def buscar_resultado(loteria):
    nome_api = "megasena" if loteria == "Mega-Sena" else "lotofacil"
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{nome_api}/latest")
        return r.json()
    except:
        return None

# --- FUNÇÕES DE GERAÇÃO ---
def gerar_mega():
    while True:
        jogo = sorted(random.sample(range(1, 61), 6))
        pares = len([n for n in jogo if n % 2 == 0])
        if 2 <= pares <= 4: return jogo

def gerar_lotofacil():
    while True:
        # Lotofácil: 15 números entre 1 e 25
        jogo = sorted(random.sample(range(1, 26), 15))
        pares = len([n for n in jogo if n % 2 == 0])
        # Filtro: O padrão mais comum é 7 ou 8 pares
        if 7 <= pares <= 8: return jogo

# --- INTERFACE PRINCIPAL ---
resultado = buscar_resultado(tipo_loteria)

st.title(f"💰 Gerador Inteligente: {tipo_loteria}")

if resultado:
    st.caption(f"Último Sorteio: Concurso {resultado['concurso']} em {resultado['data']}")
    
tab1, tab2 = st.tabs(["🎲 Gerar Jogos", "🔍 Conferir Resultado"])

with tab1:
    col_input, _ = st.columns([1, 2])
    with col_input:
        qtd = st.number_input("Quantos jogos deseja?", 1, 20, 5)
    
    if st.button(f"Gerar {tipo_loteria}"):
        for i in range(qtd):
            jogo = gerar_mega() if tipo_loteria == "Mega-Sena" else gerar_lotofacil()
            
            # Estilo visual diferente para cada loteria
            cor = COR_CAIXA_MEGA if tipo_loteria == "Mega-Sena" else COR_CAIXA_LOTO
            
            # Exibição em formato de grade
            cols = st.columns(len(jogo) if tipo_loteria == "Mega-Sena" else 5)
            for idx, n in enumerate(jogo):
                # Ajuste de colunas para os 15 números da Lotofácil (3 linhas de 5)
                col_idx = idx % 5 if tipo_loteria == "Lotofácil" else idx
                with cols[col_idx]:
                    st.markdown(f"""
                        <div style="background-color:{cor}; color:white; padding:10px; 
                        border-radius:50%; text-align:center; font-weight:bold; margin:2px;">
                        {n:02d}</div>
                    """, unsafe_allow_html=True)
            st.divider()

with tab2:
    if resultado:
        st.subheader("Dezenas Oficiais:")
        oficiais = [int(n) for n in resultado['dezenas']]
        st.write(" , ".join(map(str, oficiais)))
        
        st.divider()
        st.write("Cole seus números abaixo para conferir acertos:")
        aposta_txt = st.text_area("Números (ex: 01 02 03...)")
        
        if st.button("Conferir"):
            try:
                meus_nums = [int(n) for n in aposta_txt.replace(',', ' ').split()]
                acertos = set(meus_nums).intersection(set(oficiais))
                st.info(f"Você acertou {len(acertos)} números!")
            except:
                st.error("Formato inválido.")

# Rodapé de Venda
st.markdown("---")
st.markdown(f"<center>© 2026 {NOME_SISTEMA} | Desenvolvido por Tecnomodal</center>", unsafe_allow_html=True)




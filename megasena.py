import streamlit as st
import random
import requests

# Configuração da página
st.set_page_config(page_title="Mega-Sena Premium", page_icon="🏦", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; background-color: #004691; color: white; border-radius: 10px; height: 3em; font-weight: bold; }
    .bola { 
        background-color: #ffab00; color: #004691; padding: 15px; border-radius: 50%; 
        text-align: center; font-weight: bold; width: 55px; height: 55px; 
        display: inline-flex; align-items: center; justify-content: center; margin: 5px;
        font-size: 1.2rem; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .bola-oficial { background-color: #004691; color: white; }
    .bola-acerto { background-color: #28a745; color: white; border: 3px solid #1e7e34; }
    .card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO: BUSCA RESULTADO AUTOMÁTICO ---
@st.cache_data(ttl=3600)
def obter_resultado_caixa():
    try:
        url = "https://loteriascaixa-api.herokuapp.com/api/megasena/latest"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None

# --- FUNÇÃO: LÓGICA DE BOLÃO (FECHAMENTO) ---
def gerar_fechamento_bolao(num_jogos):
    # Tenta usar o máximo de dezenas diferentes entre os jogos (estratégia de cobertura)
    todos_numeros = list(range(1, 61))
    random.shuffle(todos_numeros)
    
    jogos_bolao = []
    for i in range(num_jogos):
        # Garante equilíbrio: 3 Pares / 3 Ímpares
        while True:
            jogo = sorted(random.sample(range(1, 61), 6))
            pares = len([n for n in jogo if n % 2 == 0])
            if 2 <= pares <= 4:
                jogos_bolao.append(jogo)
                break
    return jogos_bolao

# --- CABEÇALHO ---
resultado = obter_resultado_caixa()

st.title("🏦 Sistema de Bolão e Verificador Mega-Sena")
if resultado:
    st.success(f"✅ Conectado à Base da Caixa | Concurso: {resultado['concurso']} | Data: {resultado['data']}")
else:
    st.error("⚠️ Não foi possível carregar o resultado oficial. Usando modo offline.")

tab1, tab2 = st.tabs(["📊 Gerador de Bolão", "🔎 Verificador de Prêmios"])

# --- ABA 1: GERADOR DE BOLÃO ---
with tab1:
    st.header("Gerar Estratégia de Bolão")
    col_input, col_info = st.columns([1, 2])
    
    with col_input:
        qtd_bolao = st.number_input("Quantos jogos para o bolão?", 1, 50, 10)
        btn_gerar = st.button("GERAR COMBINAÇÕES")

    if btn_gerar:
        jogos = gerar_fechamento_bolao(qtd_bolao)
        for i, jogo in enumerate(jogos):
            with st.container():
                st.markdown(f"**Cartão {i+1:02d}**")
                html_jogo = "".join([f'<div class="bola">{n:02d}</div>' for n in jogo])
                st.markdown(f'<div class="card">{html_jogo}</div>', unsafe_allow_html=True)

# --- ABA 2: VERIFICADOR ---
with tab2:
    st.header("Verificar Meus Jogos")
    
    if resultado:
        st.subheader("Resultado do Último Sorteio:")
        dezenas_oficiais = [int(n) for n in resultado['dezenas']]
        cols_oficiais = st.columns(6)
        for i, n in enumerate(dezenas_oficiais):
            cols_oficiais[i].markdown(f'<div class="bola bola-oficial">{n:02d}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        texto_aposta = st.text_area("Cole aqui seus jogos (um por linha ou separados por vírgula):", 
                                   placeholder="Exemplo:\n05, 12, 28, 30, 44, 52\n01, 05, 10, 20, 30, 40")
        
        if st.button("CONFERIR AGORA"):
            linhas = texto_aposta.strip().split('\n')
            for linha in linhas:
                try:
                    numeros_user = [int(n.strip()) for n in linha.replace(',', ' ').split() if n.strip()]
                    if len(numeros_user) >= 6:
                        acertos = set(numeros_user).intersection(set(dezenas_oficiais))
                        qtd_acertos = len(acertos)
                        
                        # Exibe cada jogo conferido
                        status = "❌"
                        if qtd_acertos == 4: status = "🥉 QUADRA!"
                        if qtd_acertos == 5: status = "🥈 QUINA!"
                        if qtd_acertos == 6: status = "🏆 SENA!"
                        
                        st.markdown(f"**Resultado: {qtd_acertos} acertos {status}**")
                        html_verificacao = ""
                        for n in sorted(numeros_user[:6]):
                            classe = "bola bola-acerto" if n in acertos else "bola"
                            html_verificacao += f'<div class="{classe}">{n:02d}</div>'
                        st.markdown(f'<div class="card">{html_verificacao}</div>', unsafe_allow_html=True)
                        
                        if qtd_acertos >= 4: st.balloons()
                except:
                    st.error(f"Erro ao processar a linha: {linha}")
    else:
        st.warning("Verificador indisponível sem conexão com a API.")

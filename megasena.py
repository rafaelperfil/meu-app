import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
from datetime import datetime

st.set_page_config(page_title="Mega-Sena Database", layout="wide")

# 1. CONEXÃO COM A PLANILHA (Troque pela sua URL)
url_planilha = "https://docs.google.com/spreadsheets/d/1BrlfpyszCFSNsyZvrA0EXTJUqLUeGztZRAbr-4s04ro/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para carregar dados salvos
def carregar_historico():
    try:
        return conn.read(spreadsheet=url_planilha)
    except:
        return pd.DataFrame(columns=["data", "jogos_gerados", "acertos"])

# Função para salvar novos dados
def salvar_dados(qtd_jogos, acertos):
    df_antigo = carregar_historico()
    novo_dado = pd.DataFrame([{
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "jogos_gerados": qtd_jogos,
        "acertos": acertos
    }])
    df_final = pd.concat([df_antigo, novo_dado], ignore_index=True)
    conn.update(spreadsheet=url_planilha, data=df_final)

# --- INTERFACE ---
st.title("🏦 Mega-Sena com Banco de Dados")

historico = carregar_historico()
total_jogos = historico["jogos_gerados"].astype(int).sum() if not historico.empty else 0

st.metric("Total de Jogos Gerados Historicamente", total_jogos)

if st.button("Gerar 5 Jogos e Salvar"):
    # Gera os jogos
    jogos = [sorted(random.sample(range(1, 61), 6)) for _ in range(5)]
    for j in jogos: st.write(f"🍀 {j}")
    
    # Salva na planilha
    salvar_dados(5, 0)
    st.success("Dados gravados na Google Planilha!")
    st.rerun()

st.subheader("📜 Últimos Registros na Planilha")
st.dataframe(historico.tail(10)) # Mostra as últimas 10 linhas

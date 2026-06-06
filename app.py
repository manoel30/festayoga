import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Arraiá do Grupo! 🌽", page_icon="🔥", layout="centered")

## Com duas hashtags (Equivale ao st.header)
st.markdown("#### 🔥 Confraternização São João YOGA! 🍿")
st.write("Escolha o que você vai trazer para a nossa festa junina!")

# Arquivo para simular o banco de dados localmente
DATA_FILE = "itens_festa.csv"

# Itens iniciais da festa se o arquivo não existir
if not os.path.exists(DATA_FILE):
    dados_iniciais = {
        "Item": ["Bolo de Fubá", "Canjica/Canjiquinha", "Pamonha", "Laranja", "Quentão", "Refrigerante", "Salgados", "Doces Juninos (Paçoca/Pé de Moleque)"],
        "Responsável": ["Disponível"] * 8
    }
    df = pd.DataFrame(dados_iniciais)
    df.to_csv(DATA_FILE, index=False)

# Carregar dados
df = pd.read_csv(DATA_FILE)

# Exibir a tabela atual de contribuições
st.markdown("#### 📋 Lista de Comes & Bebes")
st.dataframe(df, use_container_width=True)

# LINHA DIVISÓRIA CORRIGIDA AQUI:
st.divider()

st.subheader("🙋‍♂️ Quero Contribuir!")

# Formulário para o usuário preencher
with st.form(key="form_festa"):
    nome = st.text_input("Qual é o seu nome?")
    
    # Filtra apenas os itens que ainda estão "Disponíveis"
    itens_disponiveis = df[df["Responsável"] == "Disponível"]["Item"].tolist()
    
    if itens_disponiveis:
        item_escolhido = st.selectbox("O que você vai levar?", itens_disponiveis)
        botao_enviar = st.form_submit_button("Confirmar meu Item! 🤠")
        
        if botao_enviar:
            if nome.strip() == "":
                st.error("Por favor, digite seu nome para confirmar!")
            else:
                # Atualiza o dataframe com o nome de quem escolheu
                df.loc[df["Item"] == item_escolhido, "Responsável"] = nome
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Uai, que beleza! {nome} garantiu o/a {item_escolhido}! 🎉")
                st.sidebar.markdown("Atualizando...") # Apenas um feedback visual rápido
                st.rerun()
    else:
        st.write("🥳 Eita! Todos os itens já foram preenchidos! Obrigado, pessoal!")
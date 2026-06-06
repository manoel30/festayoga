import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Arraiá do Grupo! 🌽", page_icon="🔥", layout="centered")

st.markdown("#### 🔥 Confraternização São João YOGA! 🍿")
st.write("Escolha o que você vai trazer para a nossa festa junina!")

# 1. Estabelece a conexão com o Google Sheets
# (Ele vai buscar a URL da planilha nas configurações secretas que faremos no Passo 3)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Lê os dados da planilha em tempo real (limpa o cache para sempre trazer o dado mais recente)
df = conn.read(ttl=0)

# Exibir a tabela atual de contribuições
st.markdown("#### 📋 Lista de Comes & Bebes")
st.dataframe(df, use_container_width=True)

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
                # Atualiza o dataframe na memória
                df.loc[df["Item"] == item_escolhido, "Responsável"] = nome
                
                # 3. Salva o dataframe atualizado de volta na Planilha do Google!
                conn.update(data=df)
                
                st.success(f"Uai, que beleza! {nome} garantiu o/a {item_escolhido}! 🎉")
                st.rerun()
    else:
        st.write("🥳 Eita! Todos os itens já foram preenchidos! Obrigado, pessoal!")

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Arraiá do Grupo! 🌽", page_icon="🔥", layout="centered")

st.markdown("#### 🔥 Confraternização São João YOGA! 🍿")
st.write("Escolha o que você vai trazer para a nossa festa junina!")

# 1. Estabelece a conexão básica
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. COLE O LINK DA SUA PLANILHA AQUI ABAIXO:
URL_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1ONeix1YCJllovKWUCy927FvflphfVl4RxWC933kxqGg/edit?gid=0#gid=0"

# 3. Lê os dados passando a URL diretamente como argumento
df = conn.read(spreadsheet=URL_DA_PLANILHA, ttl=0)

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
                
                # 4. Salva de volta na planilha passando a URL explicitamente também
                conn.update(spreadsheet=URL_DA_PLANILHA, data=df)
                
                st.success(f"Uai, que beleza! {nome} garantiu o/a {item_escolhido}! 🎉")
                st.rerun()
    else:
        st.write("🥳 Eita! Todos os itens já foram preenchidos! Obrigado, pessoal!")

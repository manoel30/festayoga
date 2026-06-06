import streamlit as st
import pandas as pd
import psycopg2
import os

# Configuração da página
st.set_page_config(page_title="Arraiá do Grupo! 🌽", page_icon="🔥", layout="centered")

st.markdown("#### 🔥 Confraternização São João YOGA! 🍿")
st.write("Escolha o que você vai trazer para a nossa festa junina!")

# =========================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS (RENDER VS LOCAL)
# =========================================================================
# 1. Tenta buscar primeiro nas variáveis de ambiente do Render
DATABASE_URL = os.environ.get("DATABASE_URL")

# 2. Se não achar (ambiente local), busca no arquivo .streamlit/secrets.toml
if not DATABASE_URL:
    try:
        DATABASE_URL = st.secrets["DATABASE_URL"]
    except (KeyError, FileNotFoundErr):
        st.error("Erro: A configuração do banco de dados (DATABASE_URL) não foi encontrada!")
        st.stop()

def executar_query(query, retorno=False, valores=None):
    """Função auxiliar para conectar e rodar comandos no banco"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    if valores:
        cur.execute(query, valores)
    else:
        cur.execute(query)
    
    resultado = None
    if retorno:
        resultado = cur.fetchall()
        colunas = [desc[0] for desc in cur.description]
        resultado = pd.DataFrame(resultado, columns=colunas)
        
    conn.commit()
    cur.close()
    conn.close()
    return resultado

# =========================================================================
# ESTRUTURAÇÃO DO BANCO (CRIAÇÃO E POVOAMENTO INICIAL)
# =========================================================================
# Cria a tabela automaticamente se não existir no banco conectado
executar_query("""
    CREATE TABLE IF NOT EXISTS itens_festa (
        id SERIAL PRIMARY KEY,
        item VARCHAR(200) NOT NULL,
        responsavel VARCHAR(200) DEFAULT 'Disponível'
    )
""")

# Povoa o banco com a pré-lista na primeira vez que o sistema rodar
df_verificacao = executar_query("SELECT * FROM itens_festa", retorno=True)
if df_verificacao.empty:
    itens_iniciais = [
        "Bolo de Fubá", "Canjica/Canjiquinha", "Pamonha", "Laranja", 
        "Quentão", "Refrigerante", "Salgados", "Doces Juninos (Paçoca/Pé de Moleque)"
    ]
    for item in itens_iniciais:
        executar_query("INSERT INTO itens_festa (item) VALUES (%s)", valores=(item,))

# Carrega os dados atualizados para exibir na tela
df = executar_query("SELECT item AS \"Item\", responsavel AS \"Responsável\" FROM itens_festa ORDER BY id", retorno=True)

# Exibir a tabela atual de contribuições
st.markdown("#### 📋 Lista de Comes & Bebes")
st.dataframe(df, use_container_width=True)

st.divider()

# =========================================================================
# FORMULÁRIO 1: ESCOLHER ITEM EXISTENTE DA PRÉ-LISTA
# =========================================================================
st.subheader("🙋‍♂️ Quero Contribuir com a Lista!")

with st.form(key="form_festa"):
    nome = st.text_input("Qual é o seu nome?")
    itens_disponiveis = df[df["Responsável"] == "Disponível"]["Item"].tolist()
    
    if itens_disponiveis:
        item_escolhido = st.selectbox("O que você vai levar?", itens_disponiveis)
        botao_enviar = st.form_submit_button("Confirmar meu Item! 🤠")
        
        if botao_enviar:
            if nome.strip() == "":
                st.error("Por favor, digite seu nome para confirmar!")
            else:
                executar_query(
                    "UPDATE itens_festa SET responsavel = %s WHERE item = %s",
                    valores=(nome.strip(), item_escolhido)
                )
                st.success(f"Uai, que beleza! {nome} garantiu o/a {item_escolhido}! 🎉")
                st.rerun()
    else:
        st.write("🥳 Eita! Todos os itens sugeridos já foram preenchidos!")

st.divider()

# =========================================================================
# FORMULÁRIO 2: INCLUIR UM NOVO ITEM QUE NÃO ESTAVA NA LISTA
# =========================================================================
st.subheader("➕ O que você quer trazer não está na lista?")
st.write("Adicione um novo item e coloque seu nome como responsável de uma vez só!")

with st.form(key="form_novo_item"):
    seu_nome_novo = st.text_input("Qual é o seu nome? (Novo Item)")
    novo_item_sugerido = st.text_input("Qual prato ou bebida quer adicionar?")
    botao_adicionar = st.form_submit_button("Adicionar à Lista! 🚀")
    
    if botao_adicionar:
        if seu_nome_novo.strip() == "" or novo_item_sugerido.strip() == "":
            st.error("Por favor, preencha o seu nome e o nome do item!")
        else:
            # Evita que adicionem itens duplicados (ignora maiúsculas/minúsculas)
            item_existe = df[df["Item"].str.lower() == novo_item_sugerido.strip().lower()]
            
            if not item_existe.empty:
                st.warning(f"O item '{novo_item_sugerido}' já existe na lista lá em cima!")
            else:
                # Insere o novo prato já associado diretamente à pessoa
                executar_query(
                    "INSERT INTO itens_festa (item, responsavel) VALUES (%s, %s)",
                    valores=(novo_item_sugerido.strip(), seu_nome_novo.strip())
                )
                st.success(f"Uai, que chique! '{novo_item_sugerido}' foi adicionado e reservado para {seu_nome_novo}! 🌽")
                st.rerun()

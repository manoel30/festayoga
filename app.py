import streamlit as st
import pandas as pd
import psycopg2
import os

# Configuração da página
st.set_page_config(page_title="Arraiá do Grupo! 🌽", page_icon="🔥", layout="centered")

st.markdown("#### 🔥 Confraternização São João YOGA! 🍿")
st.write("Escolha o que você vai trazer para a nossa festa junina!")

# =========================================================================
# =========================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# =========================================================================
# O Render injeta isso automaticamente se você cadastrou na aba Environment
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    try:
        DATABASE_URL = st.secrets["DATABASE_URL"]
    except Exception:
        # COLE AQUI A "INTERNAL DATABASE URL" QUE VOCÊ COPIOU DO RENDER
        DATABASE_URL = "SUA_INTERNAL_DATABASE_URL_AQUI"

# Força a conversão para string limpa para o psycopg2 não se perder
DATABASE_URL = str(DATABASE_URL).strip()

def executar_query(query, retorno=False, valores=None):
    try:
        conn = psycopg2.connect(str(DATABASE_URL).strip())
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
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        st.stop()

# Garantir existência da tabela
executar_query("""
    CREATE TABLE IF NOT EXISTS itens_festa (
        id SERIAL PRIMARY KEY,
        item VARCHAR(200) NOT NULL,
        responsavel VARCHAR(200) DEFAULT 'Disponível'
    )
""")

# Povoamento inicial se vazio
df_verificacao = executar_query("SELECT * FROM itens_festa", retorno=True)
if df_verificacao is not None and df_verificacao.empty:
    itens_iniciais = [
        "Bolo de Fubá", "Canjica/Canjiquinha", "Pamonha", "Laranja", 
        "Quentão", "Refrigerante", "Salgados", "Doces Juninos (Paçoca/Pé de Moleque)"
    ]
    for item in itens_iniciais:
        executar_query("INSERT INTO itens_festa (item) VALUES (%s)", valores=(item,))

# Carregar dados atualizados
df = executar_query("SELECT item AS \"Item\", responsavel AS \"Responsável\" FROM itens_festa ORDER BY id", retorno=True)

if df is None:
    st.stop()

# Mostrar a tabela
st.markdown("#### 📋 Lista de Comes & Bebes")
st.dataframe(df, use_container_width=True)

st.divider()

# =========================================================================
# FORMULÁRIO 1: ESCOLHER ITEM EXISTENTE
# =========================================================================
st.subheader("🙋‍♂️ Quero Contribuir com a Lista!")

form1 = st.form(key="meu_form_festa")
nome = form1.text_input("Qual é o seu nome?")
itens_disponiveis = df[df["Responsável"] == "Disponível"]["Item"].tolist()

if itens_disponiveis:
    item_escolhido = form1.selectbox("O que você vai levar?", itens_disponiveis)
    # O botão de envio atrelado diretamente à variável do formulário
    botao_enviar = form1.form_submit_button("Confirmar meu Item! 🤠")
    
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
    form1.write("🥳 Todos os itens já foram preenchidos!")
    # Formulários vazios ainda precisam de um botão para não gerarem erro de compilação
    form1.form_submit_button("Atualizar Lista 🔄")

st.divider()

# =========================================================================
# FORMULÁRIO 2: INCLUIR NOVO ITEM
# =========================================================================
st.subheader("➕ O que você quer trazer não está na lista?")
st.write("Adicione um novo item e coloque seu nome como responsável!")

form2 = st.form(key="meu_form_novo_item")
seu_nome_novo = form2.text_input("Qual é o seu nome? (Novo Item)")
novo_item_sugerido = form2.text_input("Qual prato ou bebida quer adicionar?")
botao_adicionar = form2.form_submit_button("Adicionar à Lista! 🚀")

if botao_adicionar:
    if seu_nome_novo.strip() == "" or novo_item_sugerido.strip() == "":
        st.error("Por favor, preencha o seu nome e o nome do item!")
    else:
        item_existe = df[df["Item"].str.lower() == novo_item_sugerido.strip().lower()]
        if not item_existe.empty:
            st.warning(f"O item '{novo_item_sugerido}' já existe na lista!")
        else:
            executar_query(
                "INSERT INTO itens_festa (item, responsavel) VALUES (%s, %s)",
                valores=(novo_item_sugerido.strip(), seu_nome_novo.strip())
            )
            st.success(f"'{novo_item_sugerido}' foi adicionado por {seu_nome_novo}! 🌽")
            st.rerun()

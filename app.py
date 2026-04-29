import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Sistema de Vendas", layout="wide")

st.title("🍫 Sistema de Vendas de Chocolates")

# =========================
# PRODUTOS
# =========================
if not os.path.exists("produtos.csv"):
    pd.DataFrame({"produto": [
        "Trento - Chocolate branco",
        "Trento - Chocolate",
        "Trento - Chocolate com avelã",
        "Trento - Limão",
        "Trento - Maracujá",
        "Stikadinho",
        "Twix",
        "Barrinha de cereal",
        "Ouro branco",
        "Chup Chup - doce de leite",
        "Pingo de leite"
    ]}).to_csv("produtos.csv", index=False)

df_prod = pd.read_csv("produtos.csv")
produtos = df_prod["produto"].tolist()

# =========================
# VENDAS
# =========================
if not os.path.exists("vendas.csv"):
    pd.DataFrame(columns=[
        "data", "cliente", "produto", "quantidade",
        "preco", "custo", "lucro",
        "pagamento", "status"
    ]).to_csv("vendas.csv", index=False)

df = pd.read_csv("vendas.csv")

pagamentos = ["Dinheiro", "Pix", "Cartão", "Fiado"]
status_pagamento = ["Pago", "Pendente"]

# =========================
# NOVA VENDA
# =========================
st.subheader("🛒 Nova Venda")

col1, col2, col3 = st.columns(3)

with col1:
    cliente = st.text_input("Nome do cliente")
    produto = st.selectbox("Produto", produtos)
    quantidade = st.number_input("Quantidade", min_value=1)

with col2:
    preco = st.number_input("Preço de venda", min_value=0.0)
    custo = st.number_input("Custo", min_value=0.0)

with col3:
    pagamento = st.selectbox("Forma de pagamento", pagamentos)
    status = st.selectbox("Status do pagamento", status_pagamento)

if st.button("Registrar Venda"):
    lucro = (preco - custo) * quantidade

    nova_venda = pd.DataFrame([{
        "data": datetime.now(),
        "cliente": cliente,
        "produto": produto,
        "quantidade": quantidade,
        "preco": preco,
        "custo": custo,
        "lucro": lucro,
        "pagamento": pagamento,
        "status": status
    }])

    df = pd.concat([df, nova_venda], ignore_index=True)
    df.to_csv("vendas.csv", index=False)

    st.success(f"Venda registrada! Lucro: R$ {lucro:.2f}")

# =========================
# CADASTRO DE PRODUTO
# =========================
st.subheader("➕ Cadastrar Produto")

novo_produto = st.text_input("Nome do novo produto")

if st.button("Adicionar Produto"):
    if novo_produto:
        df_prod = pd.read_csv("produtos.csv")

        if novo_produto not in df_prod["produto"].values:
            df_prod = pd.concat([df_prod, pd.DataFrame({"produto": [novo_produto]})])
            df_prod.to_csv("produtos.csv", index=False)
            st.success("Produto adicionado!")
        else:
            st.warning("Produto já existe!")

# =========================
# RESUMO
# =========================
st.subheader("📊 Resumo")

if len(df) > 0:
    total_vendido = (df["quantidade"] * df["preco"]).sum()
    lucro_total = df["lucro"].sum()

    col1, col2 = st.columns(2)
    col1.metric("💰 Total Vendido", f"R$ {total_vendido:.2f}")
    col2.metric("📈 Lucro Total", f"R$ {lucro_total:.2f}")

# =========================
# HISTÓRICO
# =========================
st.subheader("📋 Histórico de Vendas")
st.dataframe(df)

# =========================
# EDITAR / EXCLUIR
# =========================
st.subheader("✏️ Editar ou Excluir Venda")

if len(df) > 0:

    idx = st.selectbox("Selecione a venda (índice)", df.index)

    venda = df.loc[idx]

    cliente = st.text_input("Cliente", value=str(venda["cliente"]))
    produto = st.text_input("Produto", value=str(venda["produto"]))
    quantidade = st.number_input("Quantidade", value=int(venda["quantidade"]))
    preco = st.number_input("Preço", value=float(venda["preco"]))
    custo = st.number_input("Custo", value=float(venda["custo"]))
    pagamento = st.text_input("Pagamento", value=str(venda["pagamento"]))
    status = st.text_input("Status", value=str(venda["status"]))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salvar edição"):
            df.loc[idx, "cliente"] = cliente
            df.loc[idx, "produto"] = produto
            df.loc[idx, "quantidade"] = quantidade
            df.loc[idx, "preco"] = preco
            df.loc[idx, "custo"] = custo
            df.loc[idx, "lucro"] = (preco - custo) * quantidade
            df.loc[idx, "pagamento"] = pagamento
            df.loc[idx, "status"] = status

            df.to_csv("vendas.csv", index=False)
            st.success("Venda atualizada!")

    with col2:
        if st.button("🗑️ Excluir venda"):
            df = df.drop(idx)
            df.to_csv("vendas.csv", index=False)
            st.success("Venda excluída!")

# =========================
# DASHBOARD
# =========================
st.markdown("## 📊 Dashboard")

if len(df) > 0:

    # FIADO TOTAL
    st.markdown("### 💰 Fiado Total (Pendente)")

    fiado = df[df["status"] == "Pendente"]
    total_fiado = (fiado["quantidade"] * fiado["preco"]).sum()

    st.metric("Total em aberto", f"R$ {total_fiado:.2f}")
    st.dataframe(fiado)

    # PRODUTOS MAIS VENDIDOS
    st.markdown("### 🏆 Produtos Mais Vendidos")

    ranking = df.groupby("produto")["quantidade"].sum()
    st.bar_chart(ranking)

    # LUCRO POR PRODUTO
    st.markdown("### 📈 Lucro por Produto")

    lucro_prod = df.groupby("produto")["lucro"].sum()
    st.bar_chart(lucro_prod)

    # ESTOQUE SIMPLES
    st.markdown("### 📦 Estoque (Base 10 unidades)")

    estoque = {}
    for p in produtos:
        vendido = df[df["produto"] == p]["quantidade"].sum()
        estoque[p] = max(0, 10 - vendido)

    st.bar_chart(pd.Series(estoque))

else:
    st.warning("Nenhuma venda registrada ainda.")
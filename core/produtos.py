import streamlit as st
from dados.db import execute_query, fetch_all, fetch_one

def show():
    st.title("📦 Gerenciamento de Produtos")
    
    # Mensagens
    if 'msg' in st.session_state:
        st.success(st.session_state.msg)
        del st.session_state.msg
    
    # Cadastro rápido
    with st.expander("➕ Cadastrar Novo Produto"):
        with st.form("novo_produto"):
            item = st.text_input("Item*")
            valor_str = st.text_input("Valor Unitário*", value="0.00", placeholder="Ex: 19.99, 45.50, 100.00")
            
            if st.form_submit_button("Cadastrar"):
                if item and valor_str:
                    try:
                        valor_unitario = float(valor_str)
                        if valor_unitario >= 0:
                            execute_query(
                                "INSERT INTO produtos (item, valor_unitario) VALUES (?, ?)",
                                (item, valor_unitario)
                            )
                            st.session_state.msg = "Produto cadastrado!"
                            st.rerun()
                        else:
                            st.error("O valor não pode ser negativo!")
                    except ValueError:
                        st.error("Digite um valor válido (ex: 19.99)")
                else:
                    st.error("Item e valor são obrigatórios!")
    
    # Lista de produtos
    produtos = fetch_all("SELECT * FROM produtos ORDER BY item")
    
    if not produtos:
        st.info("Nenhum produto cadastrado")
        return
    
    # Selecionar produto para editar
    produto_id = st.selectbox(
        "Selecionar produto:",
        options=[p['id'] for p in produtos],
        format_func=lambda x: f"{next(p['item'] for p in produtos if p['id'] == x)} - R$ {next(p['valor_unitario'] for p in produtos if p['id'] == x):.2f}"
    )
    
    if produto_id:
        produto = next(p for p in produtos if p['id'] == produto_id)
        
        # Edição rápida
        with st.form("editar_produto"):
            st.subheader(f"Editando: {produto['item']}")
            
            novo_item = st.text_input("Item", value=produto['item'])
            novo_valor_str = st.text_input("Valor Unitário", value=f"{produto['valor_unitario']:.2f}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Salvar"):
                    try:
                        novo_valor = float(novo_valor_str)
                        if novo_valor >= 0:
                            execute_query(
                                "UPDATE produtos SET item=?, valor_unitario=? WHERE id=?",
                                (novo_item, novo_valor, produto_id)
                            )
                            st.session_state.msg = "Produto atualizado!"
                            st.rerun()
                        else:
                            st.error("O valor não pode ser negativo!")
                    except ValueError:
                        st.error("Digite um valor válido!")
            with col2:
                if st.form_submit_button("🗑 Excluir"):
                    execute_query("DELETE FROM produtos WHERE id=?", (produto_id,))
                    st.session_state.msg = "Produto excluído!"
                    st.rerun()
    
    # Estatísticas simples
    total = len(produtos)
    valor_total = sum(p['valor_unitario'] for p in produtos)
    st.metric("📊 Estatísticas", f"{total} produtos, Valor total: R$ {valor_total:.2f}")
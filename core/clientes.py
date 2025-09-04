import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dados.db import execute_query, fetch_all, fetch_one

def show():
    st.title("👥 Gerenciamento de Clientes")
    
    # Mensagens de sucesso
    if 'cliente_mensagem' in st.session_state:
        st.success(st.session_state.cliente_mensagem)
        del st.session_state.cliente_mensagem
    
    # SECTION 1: FORMULÁRIO DE CADASTRO (simplificado)
    with st.expander("➕ Cadastrar Novo Cliente", expanded=False):
        with st.form("form_novo_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Cliente*", max_chars=255)
                cidade = st.text_input("Cidade", max_chars=100)
                cep = st.text_input("CEP", max_chars=10)
            
            with col2:
                endereco = st.text_area("Endereço", max_chars=255)
                telefone = st.text_input("Telefone", max_chars=20)
            
            submitted = st.form_submit_button("✅ Cadastrar Cliente")
            
            if submitted:
                if not nome:
                    st.error("❌ Nome do cliente é obrigatório!")
                else:
                    success = execute_query(
                        "INSERT INTO clientes (nome, cidade, cep, endereco, telefone) VALUES (?, ?, ?, ?, ?)",
                        (nome, cidade, cep, endereco, telefone)
                    )
                    if success:
                        st.session_state.cliente_mensagem = "✅ Cliente cadastrado com sucesso!"
                        st.rerun()
    
    # SECTION 2: SELECTBOX PARA GERENCIAR CLIENTES EXISTENTES
    st.header("📋 Gerenciar Clientes Existentes")
    
    # Buscar todos os clientes
    clientes = fetch_all("SELECT id, nome FROM clientes ORDER BY nome")
    
    if not clientes:
        st.info("📝 Nenhum cliente cadastrado ainda.")
        return
    
    # Selectbox para escolher o cliente
    opcoes_clientes = [f"{c['id']} - {c['nome']}" for c in clientes]
    opcoes_clientes.insert(0, "Selecione um cliente...")
    
    cliente_selecionado = st.selectbox(
        "Escolha um cliente para visualizar/editar:",
        options=opcoes_clientes,
        key="selectbox_gerenciar_cliente"
    )
    
    # Se um cliente foi selecionado
    if cliente_selecionado and cliente_selecionado != "Selecione um cliente...":
        # Extrai o ID do cliente selecionado
        cliente_id = cliente_selecionado.split(" - ")[0]
        
        # Busca informações completas do cliente
        cliente_info = fetch_one(
            "SELECT * FROM clientes WHERE id = ?", 
            (cliente_id,)
        )
        
        if cliente_info:
            st.divider()
            st.subheader(f"👤 Informações do Cliente: {cliente_info['nome']}")
            
            # Exibe informações em colunas
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write(f"*ID:* {cliente_info['id']}")
                st.write(f"*Cidade:* {cliente_info['cidade'] or 'Não informado'}")
                st.write(f"*CEP:* {cliente_info['cep'] or 'Não informado'}")
            
            with col_info2:
                st.write(f"*Endereço:* {cliente_info['endereco'] or 'Não informado'}")
                st.write(f"*Telefone:* {cliente_info['telefone'] or 'Não informado'}")
            
            st.divider()
            
            # SECTION 3: EDIÇÃO DO CLIENTE SELECIONADO
            st.subheader("✏ Editar Cliente")
            
            with st.form("form_editar_cliente"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_nome = st.text_input(
                        "Nome*", 
                        value=cliente_info['nome'], 
                        max_chars=255,
                        key="edit_nome_input"
                    )
                    edit_cidade = st.text_input(
                        "Cidade", 
                        value=cliente_info['cidade'] or '', 
                        max_chars=100,
                        key="edit_cidade_input"
                    )
                    edit_cep = st.text_input(
                        "CEP", 
                        value=cliente_info['cep'] or '', 
                        max_chars=10,
                        key="edit_cep_input"
                    )
                
                with col2:
                    edit_endereco = st.text_area(
                        "Endereço", 
                        value=cliente_info['endereco'] or '', 
                        max_chars=255,
                        key="edit_endereco_input"
                    )
                    edit_telefone = st.text_input(
                        "Telefone", 
                        value=cliente_info['telefone'] or '', 
                        max_chars=20,
                        key="edit_telefone_input"
                    )
                
                col_salvar, col_excluir = st.columns(2)
                
                with col_salvar:
                    btn_salvar = st.form_submit_button("💾 Salvar Alterações")
                
                with col_excluir:
                    btn_excluir = st.form_submit_button("🗑 Excluir Cliente")
                
                if btn_salvar:
                    if not edit_nome:
                        st.error("❌ Nome do cliente é obrigatório!")
                    else:
                        success = execute_query(
                            "UPDATE clientes SET nome = ?, cidade = ?, cep = ?, endereco = ?, telefone = ? WHERE id = ?",
                            (edit_nome, edit_cidade, edit_cep, edit_endereco, edit_telefone, cliente_id)
                        )
                        if success:
                            st.session_state.cliente_mensagem = "✅ Cliente atualizado com sucesso!"
                            st.rerun()
                
                if btn_excluir:
                    # Confirmação de exclusão
                    if st.session_state.get('confirmar_exclusao') != cliente_id:
                        st.session_state.confirmar_exclusao = cliente_id
                        st.warning("⚠ Clique novamente em 'Excluir Cliente' para confirmar a exclusão!")
                    else:
                        if execute_query("DELETE FROM clientes WHERE id = ?", (cliente_id,)):
                            st.session_state.cliente_mensagem = "✅ Cliente excluído com sucesso!"
                            st.session_state.confirmar_exclusao = None
                            st.rerun()
    
    # SECTION 4: ESTATÍSTICA SIMPLES
    st.divider()
    total_clientes = fetch_one("SELECT COUNT(*) as total FROM clientes")
    if total_clientes:
        st.metric("📊 Total de Clientes Cadastrados", total_clientes['total'])

# Esta linha é necessária para que o app.py possa importar a função show()
if __name__ != "__main__":
    # Esta função será importada pelo app.py
    pass
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dados.db import execute_query, fetch_all, fetch_one

def show():
    st.title("🏢 Cadastro de Fornecedores")
    
    # Formulário de cadastro
    with st.form("form_fornecedor"):
        col1, col2 = st.columns(2)
        
        with col1:
            razao_social = st.text_input("Razão Social*", max_chars=255)
            apelido = st.text_input("Apelido", max_chars=100)
            cnpj = st.text_input("CNPJ", max_chars=18)
        
        with col2:
            endereco = st.text_area("Endereço", max_chars=255)
            cep = st.text_input("CEP", max_chars=10)
            telefone = st.text_input("Telefone", max_chars=20)
        
        submitted = st.form_submit_button("Cadastrar Fornecedor")
        
        if submitted:
            if not razao_social:
                st.error("Razão social é obrigatória!")
            else:
                success = execute_query(
                    """INSERT INTO fornecedores 
                    (razao_social, apelido, cnpj, endereco, cep, telefone) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (razao_social, apelido, cnpj, endereco, cep, telefone)
                )
                if success:
                    st.success("Fornecedor cadastrado com sucesso!")
                    st.rerun()
    
    # Lista de fornecedores cadastrados
    st.subheader("📋 Fornecedores Cadastrados")
    fornecedores = fetch_all("SELECT * FROM fornecedores ORDER BY razao_social")
    
    if fornecedores:
        for fornecedor in fornecedores:
            with st.expander(f"{fornecedor['razao_social']} ({fornecedor['apelido'] or 'Sem apelido'})"):
                st.write(f"**CNPJ**: {fornecedor['cnpj'] or 'Não informado'}")
                st.write(f"**Endereço**: {fornecedor['endereco'] or 'Não informado'}")
                st.write(f"**CEP**: {fornecedor['cep'] or 'Não informado'}")
                st.write(f"**Telefone**: {fornecedor['telefone'] or 'Não informado'}")
                
                # Botão para excluir
                if st.button("Excluir Fornecedor", key=f"del_{fornecedor['id']}"):
                    execute_query("DELETE FROM fornecedores WHERE id = %s", (fornecedor['id'],))
                    st.success("Fornecedor excluído com sucesso!")
                    st.rerun()
    else:
        st.info("Nenhum fornecedor cadastrado ainda.")
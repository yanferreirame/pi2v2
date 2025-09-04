import streamlit as st
from dados.db import execute_query, fetch_all, fetch_one
import os
from datetime import datetime
from fpdf import FPDF
import pandas as pd

def show():
    st.title("🛒 Fazer Pedido")
    
    if 'msg' in st.session_state:
        st.success(st.session_state.msg)
        del st.session_state.msg
    
    # Inicializar estado do desconto
    if 'desconto_aplicado' not in st.session_state:
        st.session_state.desconto_aplicado = False
    if 'percentual_desconto' not in st.session_state:
        st.session_state.percentual_desconto = 0.0
    
    # Buscar clientes e produtos
    clientes = fetch_all("SELECT id, nome FROM clientes ORDER BY nome")
    produtos = fetch_all("SELECT id, item, valor_unitario FROM produtos ORDER BY item")
    
    if not clientes or not produtos:
        st.warning("Cadastre clientes e produtos primeiro!")
        return
    
    with st.form("form_pedido"):
        # Selecionar cliente
        cliente_id = st.selectbox(
            "Cliente*",
            options=[c['id'] for c in clientes],
            format_func=lambda x: next(c['nome'] for c in clientes if c['id'] == x)
        )
        
        # Selecionar produto
        produto_id = st.selectbox(
            "Produto*",
            options=[p['id'] for p in produtos],
            format_func=lambda x: f"{next(p['item'] for p in produtos if p['id'] == x)} - R$ {next(p['valor_unitario'] for p in produtos if p['id'] == x):.2f}"
        )
        
        quantidade = st.number_input("Quantidade*", min_value=1, value=1)
        
        # Método de pagamento
        metodo_pagamento = st.selectbox(
            "Método de Pagamento*",
            options=["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito", "Transferência"]
        )
        
        # Campo de desconto com digitação livre
        desconto_input = ""
        aplicar_desconto_btn = None
        
        if metodo_pagamento in ["Dinheiro", "PIX"]:
            desconto_input = st.text_input(
                "Desconto (%)", 
                value=str(st.session_state.percentual_desconto),
                help="Digite qualquer valor de porcentagem (ex: 15.5, 20, 7.25)"
            )
            
            # Botão para aplicar desconto
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                aplicar_desconto_btn = st.form_submit_button("💸 Aplicar Desconto")
            with col_btn2:
                remover_desconto_btn = st.form_submit_button("❌ Remover Desconto")
            
            if aplicar_desconto_btn and desconto_input:
                try:
                    desconto_percent = float(desconto_input.replace(',', '.'))
                    if 0 <= desconto_percent <= 100:
                        st.session_state.desconto_aplicado = True
                        st.session_state.percentual_desconto = desconto_percent
                    else:
                        st.error("Desconto deve estar entre 0% e 100%")
                except ValueError:
                    st.error("Digite um valor numérico válido (ex: 15.5)")
            
            if remover_desconto_btn:
                st.session_state.desconto_aplicado = False
                st.session_state.percentual_desconto = 0.0
        else:
            st.info("💡 Desconto disponível apenas para pagamentos em Dinheiro ou PIX")
            st.session_state.desconto_aplicado = False
            st.session_state.percentual_desconto = 0.0
        
        # Calcular valores
        produto = next(p for p in produtos if p['id'] == produto_id)
        valor_unitario = produto['valor_unitario']
        valor_bruto = valor_unitario * quantidade
        
        # Aplicar desconto apenas se estiver ativo
        if st.session_state.desconto_aplicado and st.session_state.percentual_desconto > 0:
            valor_desconto = (valor_bruto * st.session_state.percentual_desconto) / 100
            valor_total = valor_bruto - valor_desconto
            desconto_status = f"✅ {st.session_state.percentual_desconto}% aplicado"
        else:
            valor_desconto = 0.0
            valor_total = valor_bruto
            desconto_status = "❌ Não aplicado"
        
        # Exibir resumo
        st.divider()
        st.subheader("🧾 Resumo do Pedido")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Valor Bruto", f"R$ {valor_bruto:.2f}")
        
        if st.session_state.desconto_aplicado and st.session_state.percentual_desconto > 0:
            col2.metric(f"Desconto ({st.session_state.percentual_desconto}%)", f"-R$ {valor_desconto:.2f}")
            col3.metric("Valor Total", f"R$ {valor_total:.2f}", delta_color="inverse")
        else:
            col2.metric("Desconto", "R$ 0,00")
            col3.metric("Valor Total", f"R$ {valor_total:.2f}")
        
        col_status1, col_status2 = st.columns(2)
        col_status1.write(f"**Status desconto:** {desconto_status}")
        col_status2.write(f"**Pagamento:** {metodo_pagamento}")
        
        # Botão de submit do pedido
        if st.form_submit_button("✅ Fazer Pedido"):
            try:
                # Usar o desconto da session state (que pode estar aplicado ou não)
                desconto_final = st.session_state.percentual_desconto if st.session_state.desconto_aplicado else 0
                
                success = execute_query(
                    "INSERT INTO pedidos (cliente_id, produto_id, quantidade, metodo_pagamento, desconto, valor_total) VALUES (?, ?, ?, ?, ?, ?)",
                    (cliente_id, produto_id, quantidade, metodo_pagamento, desconto_final, valor_total)
                )
                
                if success:
                    # Buscar o último ID inserido
                    ultimo_id = fetch_one("SELECT last_insert_rowid() as id")
                    if ultimo_id:
                        pedido_id = ultimo_id['id']
                        st.session_state.msg = f"Pedido #{pedido_id} realizado com sucesso! Valor: R$ {valor_total:.2f}"
                        
                        # Gerar nota fiscal automaticamente
                        gerar_nota_fiscal(pedido_id, cliente_id, produto_id, quantidade, metodo_pagamento, desconto_final, valor_total)
                        
                    else:
                        st.session_state.msg = f"Pedido realizado com sucesso! Valor: R$ {valor_total:.2f}"
                    
                    # Resetar desconto após pedido
                    st.session_state.desconto_aplicado = False
                    st.session_state.percentual_desconto = 0.0
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Erro ao processar pedido: {e}")
    
    # Listar pedidos recentes com opções de exclusão
    st.divider()
    st.subheader("📋 Pedidos Recentes")
    
    pedidos = fetch_all("""
        SELECT p.id, c.nome as cliente, pr.item as produto, p.quantidade, 
               p.metodo_pagamento, p.desconto, p.valor_total, p.created_at
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN produtos pr ON p.produto_id = pr.id
        ORDER BY p.created_at DESC LIMIT 10
    """)
    
    if pedidos:
        for pedido in pedidos:
            with st.expander(f"Pedido #{pedido['id']} - {pedido['cliente']} - R$ {pedido['valor_total']:.2f}"):
                col1, col2 = st.columns(2)
                col1.write(f"**Produto:** {pedido['produto']}")
                col1.write(f"**Quantidade:** {pedido['quantidade']}")
                col2.write(f"**Pagamento:** {pedido['metodo_pagamento']}")
                if pedido['desconto'] > 0:
                    col2.write(f"**Desconto:** {pedido['desconto']}%")
                col2.write(f"**Data:** {pedido['created_at']}")
                
                # Botões de ação para cada pedido
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"📄 Gerar Nota Fiscal", key=f"nota_{pedido['id']}"):
                        gerar_nota_fiscal(
                            pedido['id'], 
                            next(c['id'] for c in clientes if c['nome'] == pedido['cliente']),
                            next(p['id'] for p in produtos if p['item'] == pedido['produto']),
                            pedido['quantidade'],
                            pedido['metodo_pagamento'],
                            pedido['desconto'],
                            pedido['valor_total']
                        )
                        st.success(f"Nota fiscal gerada para pedido #{pedido['id']}!")
                
                with col_btn2:
                    if st.button(f"🗑 Excluir", key=f"excluir_{pedido['id']}"):
                        if execute_query("DELETE FROM pedidos WHERE id = ?", (pedido['id'],)):
                            st.session_state.msg = f"Pedido #{pedido['id']} excluído com sucesso!"
                            st.rerun()
    else:
        st.info("Nenhum pedido realizado ainda.")

def gerar_nota_fiscal(pedido_id, cliente_id, produto_id, quantidade, metodo_pagamento, desconto, valor_total):
    """Gera nota fiscal em PDF para o pedido"""
    try:
        # Buscar informações completas
        cliente = fetch_one("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        produto = fetch_one("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        
        if not cliente or not produto:
            st.error("Erro ao gerar nota fiscal: dados não encontrados")
            return
        
        # Criar pasta notas se não existir
        os.makedirs("notas", exist_ok=True)
        
        # Criar PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Configurar fonte
        pdf.set_font("Arial", 'B', 16)
        
        # Cabeçalho
        pdf.cell(0, 10, "NOTA FISCAL", 0, 1, 'C')
        pdf.ln(5)
        
        # Informações da empresa
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, "Empresa: MEI Comércio", 0, 1)
        pdf.cell(0, 8, "CNPJ: 12.345.678/0001-90", 0, 1)
        pdf.cell(0, 8, "Endereço: Rua Exemplo, 123 - Centro", 0, 1)
        pdf.cell(0, 8, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
        pdf.cell(0, 8, f"Nº Pedido: {pedido_id}", 0, 1)
        pdf.ln(5)
        
        # Linha divisória
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Informações do cliente
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "DADOS DO CLIENTE", 0, 1)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Nome: {cliente['nome']}", 0, 1)
        if cliente['endereco']:
            pdf.cell(0, 8, f"Endereço: {cliente['endereco']}", 0, 1)
        if cliente['cidade']:
            pdf.cell(0, 8, f"Cidade: {cliente['cidade']}", 0, 1)
        if cliente['telefone']:
            pdf.cell(0, 8, f"Telefone: {cliente['telefone']}", 0, 1)
        pdf.ln(5)
        
        # Itens do pedido
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "ITENS DO PEDIDO", 0, 1)
        pdf.set_font("Arial", '', 12)
        
        # Tabela de itens
        pdf.cell(100, 8, "Descrição", 1)
        pdf.cell(30, 8, "Qtd", 1)
        pdf.cell(30, 8, "Valor Unit.", 1)
        pdf.cell(30, 8, "Total", 1)
        pdf.ln()
        
        pdf.cell(100, 8, produto['item'], 1)
        pdf.cell(30, 8, str(quantidade), 1)
        pdf.cell(30, 8, f"R$ {produto['valor_unitario']:.2f}", 1)
        pdf.cell(30, 8, f"R$ {produto['valor_unitario'] * quantidade:.2f}", 1)
        pdf.ln()
        
        # Totais
        pdf.ln(5)
        pdf.cell(0, 8, f"Subtotal: R$ {produto['valor_unitario'] * quantidade:.2f}", 0, 1)
        if desconto > 0:
            pdf.cell(0, 8, f"Desconto ({desconto}%): -R$ {(produto['valor_unitario'] * quantidade * desconto / 100):.2f}", 0, 1)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"VALOR TOTAL: R$ {valor_total:.2f}", 0, 1)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Forma de Pagamento: {metodo_pagamento}", 0, 1)
        
        # Rodapé
        pdf.ln(15)
        pdf.cell(0, 8, "________________________________________", 0, 1, 'C')
        pdf.cell(0, 8, "Assinatura", 0, 1, 'C')
        
        # Salvar arquivo
        filename = f"notas/nota_fiscal_{pedido_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        
        st.success(f"Nota fiscal gerada: {filename}")
        
    except Exception as e:
        st.error(f"Erro ao gerar nota fiscal: {e}")

# Instalar dependência se necessário
try:
    from fpdf import FPDF
except ImportError:
    st.warning("Instalando biblioteca FPDF...")
    os.system("pip install fpdf")
    from fpdf import FPDF
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dados.db import execute_query, fetch_all, fetch_one
import pandas as pd
from datetime import datetime, timedelta

# Tenta importar Plotly, mas não quebra se não tiver
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly não instalado. Instale com: pip install plotly")

def parse_datetime(datetime_str):
    """Função robusta para parse de datas em diferentes formatos"""
    if not datetime_str:
        return None
    
    # Remove microssegundos se existirem
    if '.' in datetime_str:
        datetime_str = datetime_str.split('.')[0]
    
    # Remove qualquer caractere extra
    datetime_str = datetime_str.strip()
    
    # Tenta diferentes formatos de data
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y',
        '%Y%m%d %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    return None

def safe_date_convert(date_str):
    """Conversão segura de datas para evitar erros"""
    try:
        if not date_str:
            return None
        return parse_datetime(str(date_str))
    except:
        return None

def show():
    st.title("📈 PAINEL DE CONTROLE")
    
    try:
        # Filtros de data
        st.sidebar.header("🔍 Filtros")
        
        # Obter datas mínima e máxima do banco com tratamento robusto
        date_range = fetch_one("SELECT MIN(created_at) as min_date, MAX(created_at) as max_date FROM pedidos")
        
        if date_range and date_range['min_date'] and date_range['max_date']:
            min_date = safe_date_convert(date_range['min_date'])
            max_date = safe_date_convert(date_range['max_date'])
            
            if min_date and max_date:
                min_date = min_date.date()
                max_date = max_date.date()
            else:
                min_date = datetime.now().date() - timedelta(days=30)
                max_date = datetime.now().date()
        else:
            min_date = datetime.now().date() - timedelta(days=30)
            max_date = datetime.now().date()
        
        date_range = st.sidebar.date_input(
            "Período de Análise",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Converter para string para usar na query
        if len(date_range) == 2:
            start_date, end_date = date_range
            end_date += timedelta(days=1)  # Para incluir o dia final
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
        else:
            start_date_str = min_date.strftime('%Y-%m-%d')
            end_date_str = (max_date + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Construir query base com filtros
        query_where = "WHERE p.created_at BETWEEN ? AND ?"
        params = [start_date_str, end_date_str]
        
        # Métricas principais
        st.subheader("📊 Métricas Principais")
        
        # Buscar dados para as métricas
        metricas = fetch_one(f"""
            SELECT 
                COUNT(*) as total_pedidos,
                SUM(p.valor_total) as valor_total,
                AVG(p.valor_total) as valor_medio,
                COUNT(DISTINCT p.cliente_id) as clientes_ativos,
                SUM(p.quantidade) as total_itens
            FROM pedidos p
            {query_where}
        """, params)
        
        if metricas:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total de Pedidos", metricas['total_pedidos'] or 0)
            
            with col2:
                st.metric("Valor Total", f"R$ {metricas['valor_total'] or 0:,.2f}")
            
            with col3:
                st.metric("Ticket Médio", f"R$ {metricas['valor_medio'] or 0:,.2f}")
            
            with col4:
                st.metric("Clientes Ativos", metricas['clientes_ativos'] or 0)
            
            with col5:
                st.metric("Itens Vendidos", metricas['total_itens'] or 0)
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        
        # Dados para gráficos
        vendas_por_dia = fetch_all(f"""
            SELECT 
                DATE(p.created_at) as data,
                COUNT(*) as pedidos,
                SUM(p.valor_total) as valor_total,
                SUM(p.quantidade) as itens
            FROM pedidos p
            {query_where}
            GROUP BY DATE(p.created_at)
            ORDER BY data
        """, params)
        
        if vendas_por_dia:
            df_vendas = pd.DataFrame(vendas_por_dia)
            
            # Converter datas de forma segura
            df_vendas['data'] = pd.to_datetime(df_vendas['data'], errors='coerce')
            df_vendas = df_vendas.dropna(subset=['data'])
            
            if not df_vendas.empty:
                st.subheader("📈 Tendência de Vendas")
                
                if PLOTLY_AVAILABLE:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_vendas['data'], y=df_vendas['valor_total'], 
                                            mode='lines+markers', name='Valor Total',
                                            line=dict(color='#1f77b4', width=3)))
                    fig.add_trace(go.Bar(x=df_vendas['data'], y=df_vendas['pedidos'], 
                                        name='Nº de Pedidos', opacity=0.6,
                                        marker_color='#ff7f0e'))
                    
                    fig.update_layout(
                        title='Evolução de Vendas e Pedidos',
                        xaxis_title='Data',
                        yaxis_title='Valor (R$)',
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback se Plotly não estiver disponível
                    st.line_chart(df_vendas.set_index('data')['valor_total'])
                    st.bar_chart(df_vendas.set_index('data')['pedidos'])
            else:
                st.info("Não há dados suficientes para o gráfico de tendência.")
        
        # Tabela de últimos pedidos
        st.subheader("📋 Últimos Pedidos")
        ultimos_pedidos = fetch_all(f"""
            SELECT 
                p.id,
                c.nome as cliente,
                pr.item as produto,
                p.quantidade,
                p.valor_total,
                p.metodo_pagamento,
                p.created_at
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            JOIN produtos pr ON p.produto_id = pr.id
            ORDER BY p.created_at DESC
            LIMIT 10
        """)
        
        if ultimos_pedidos:
            df_ultimos = pd.DataFrame(ultimos_pedidos)
            # Formatar data de forma segura
            df_ultimos['created_at'] = pd.to_datetime(df_ultimos['created_at'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
            
            st.dataframe(
                df_ultimos,
                column_config={
                    "id": "Pedido ID",
                    "cliente": "Cliente",
                    "produto": "Produto",
                    "quantidade": "Qtd",
                    "valor_total": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "metodo_pagamento": "Pagamento",
                    "created_at": "Data"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Nenhum pedido encontrado.")
        
        # Estatísticas simples
        st.subheader("📊 Estatísticas Gerais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Total de clientes
            total_clientes = fetch_one("SELECT COUNT(*) as total FROM clientes")
            st.metric("Total de Clientes", total_clientes['total'] if total_clientes else 0)
            
            # Total de produtos
            total_produtos = fetch_one("SELECT COUNT(*) as total FROM produtos")
            st.metric("Total de Produtos", total_produtos['total'] if total_produtos else 0)
        
        with col2:
            # Valor total em vendas
            vendas_total = fetch_one("SELECT SUM(valor_total) as total FROM pedidos")
            st.metric("Vendas Totais", f"R$ {vendas_total['total'] or 0:,.2f}")
            
            # Média de vendas
            media_vendas = fetch_one("SELECT AVG(valor_total) as media FROM pedidos")
            st.metric("Média por Pedido", f"R$ {media_vendas['media'] or 0:,.2f}")
    
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")
        st.info("💡 Dica: Verifique se os dados foram populados corretamente no banco.")

# Esta linha é necessária para que o app.py possa importar a função show()
if __name__ != "__main__":
    pass
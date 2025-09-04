import streamlit as st
import sys
import os
import importlib
import time
from datetime import datetime

# Configuração do path
sys.path.append(os.path.dirname(__file__))

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gerenciamento",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    .menu-item {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.3s ease;
        background: #f8f9fa;
        border-left: 4px solid #1E88E5;
    }
    .menu-item:hover {
        background: #e3f2fd;
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(30, 136, 229, 0.2);
    }
    .menu-item.active {
        background: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .company-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .company-logo h1 {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
        margin: 0;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Estado da sessão para controlar a página atual
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = "Dashboard"

# Função para importar módulos
def carregar_modulo(nome_modulo):
    try:
        if nome_modulo == "dashboard":
            from core.dash import show
            return show
        elif nome_modulo == "clientes":
            from core.clientes import show
            return show
        elif nome_modulo == "produtos":
            from core.produtos import show
            return show
        elif nome_modulo == "fornecedores":
            from core.fornecedores import show
            return show
        elif nome_modulo == "pedidos":
            from core.pedidos import show
            return show
    except ImportError as e:
        st.error(f"Erro ao importar {nome_modulo}: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return None

# Menu lateral
with st.sidebar:
    st.title("📊 Menu de Navegação")
    
    # Mostra última atualização
    st.sidebar.markdown(f"**Última atualização:** <span style='color: green;'>{datetime.now().strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)
    
    # Itens do menu
    menu_itens = [
        {"nome": "Dashboard", "icone": "📈", "modulo": "dashboard"},
        {"nome": "Clientes", "icone": "👥", "modulo": "clientes"},
        {"nome": "Produtos", "icone": "📦", "modulo": "produtos"},
        {"nome": "Fornecedores", "icone": "🏢", "modulo": "fornecedores"},
        {"nome": "Pedidos", "icone": "🛒", "modulo": "pedidos"}
    ]
    
    for item in menu_itens:
        if st.button(f"{item['icone']} {item['nome']}", key=item['nome'], 
                    use_container_width=True, 
                    type="primary" if st.session_state.pagina_atual == item['nome'] else "secondary"):
            st.session_state.pagina_atual = item['nome']
            st.session_state.modulo_atual = item['modulo']
            st.rerun()

# Botão de recarregamento
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Recarregar Tudo", use_container_width=True):
    st.rerun()

# Conteúdo principal
if 'modulo_atual' in st.session_state:
    funcao = carregar_modulo(st.session_state.modulo_atual)
    if funcao:
        try:
            funcao()
        except Exception as e:
            st.error(f"Erro ao executar {st.session_state.modulo_atual}: {e}")
else:
    # Carregar dashboard por padrão
    funcao = carregar_modulo("dashboard")
    if funcao:
        try:
            funcao()
        except Exception as e:
            st.error(f"Erro ao executar dashboard: {e}")
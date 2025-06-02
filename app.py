import streamlit as st
import os
from dotenv import load_dotenv
from controllers.pedido_controller import PedidoController
from views.pedido_view import PedidoView
from views.pedido_historico_view import PedidoHistoricoView
from views.pedido_form_view import PedidoFormView
from views.configuracoes_view import ConfiguracoesView
from pathlib import Path
from views.pedido_dashboard_gerencial import mostrar_dashboard_gerencial

# Carregar variáveis de ambiente
load_dotenv()

# Configurar página Streamlit
st.set_page_config(
    page_title="Sistema de Pedidos de Bobina",
    page_icon="📦",
    layout="wide"
)

# Forçar tema claro
st.markdown(
    '''
    <style>
    body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        background-color: #fff !important;
        color: #222 !important;
    }
    </style>
    ''',
    unsafe_allow_html=True
)


# CSS personalizado

# CSS para remover completamente o cabeçalho do Streamlit
custom_css = """
    <style>
        /* Remove completamente o cabeçalho da aplicação Streamlit */
        header.stAppHeader {
            display: none !important;
            z-index: none !important;
        }
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)



# Caminho da planilha de mapeamento
PLANILHA_MAPEAMENTO = os.getenv('CAMINHO_PLANILHA', os.path.join(
    'pedidos',
    'Mapeamento de Racks - Cabos.xlsx'
))

def estilizar_sidebar():
    st.sidebar.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            padding: 2rem 1rem;
        }
        .sidebar-menu {
            margin-bottom: 2rem;
            text-align: center;
        }
        .sidebar-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        /* Estilo para os botões */
        .stButton button {
            width: 100%;
            margin: 0.3rem 0 !important;
            padding: 0.5rem !important;
            border: 1px solid #e0e0e0 !important;
            background-color: white !important;
            color: #333 !important;
        }
        .stButton button:hover {
            border-color: #0d6efd !important;
            color: #0d6efd !important;
        }
        /* Remove o espaço extra entre markdown */
        .sidebar-menu div.stMarkdown {
            margin: 0 !important;
            padding: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    try:
        # Estilizar sidebar
        estilizar_sidebar()
        
        # Título no sidebar
        st.sidebar.markdown('<div class="sidebar-title">Yazaki<br>Sistema de Requisição</div>', unsafe_allow_html=True)
        
        # Menu com botões separados
        st.sidebar.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
        
        # Inicializar o estado do menu se não existir
        if 'menu_atual' not in st.session_state:
            st.session_state.menu_atual = "📝 Novo Pedido"
        
        # Botões de navegação
        if st.sidebar.button("📝 Novo Pedido", use_container_width=True):
            st.session_state.menu_atual = "📝 Novo Pedido"
            
        st.sidebar.markdown('<div style="margin: 0.2rem 0;"></div>', unsafe_allow_html=True)
            
        if st.sidebar.button("📋 Pedidos", use_container_width=True):
            st.session_state.menu_atual = "📋 Histórico"
            
        st.sidebar.markdown('<div style="margin: 0.2rem 0;"></div>', unsafe_allow_html=True)
            
        if st.sidebar.button("⚙️ Configurações", use_container_width=True):
            st.session_state.menu_atual = "⚙️ Configurações"
        
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        # Informações úteis no sidebar
        with st.sidebar:
            st.markdown("---")
            st.markdown("### ℹ️ Informações")
            st.markdown("""
            - 📝 **Novo Pedido**: Criar requisição
            - 📋 **Histórico**: Ver/Imprimir pedidos
            """)
            
            st.markdown("---")
            st.markdown("### 🔍 Ajuda Rápida")
            with st.expander("Como criar um pedido?"):
                st.markdown("""
                1. Selecione "Criar Novo Pedido"
                2. Escolha o cliente
                3. Selecione o RACK
                4. Escolha a localização
                5. Preencha os dados
                """)
            
            with st.expander("Como imprimir um pedido?"):
                st.markdown("""
                1. Vá para "Ver Histórico"
                2. Encontre o pedido desejado
                3. Clique em "🖨️ Imprimir"
                """)

        # Inicializar controlador
        pedido_controller = PedidoController(PLANILHA_MAPEAMENTO)
        
        # Inicializar views
        pedido_view = PedidoView(pedido_controller)
        historico_view = PedidoHistoricoView(pedido_controller)
        configuracoes_view = ConfiguracoesView()
        
        # Mostrar interface baseado na seleção do menu
        if "Novo Pedido" in st.session_state.menu_atual:
            pedido_view.mostrar_interface()
        elif "Histórico" in st.session_state.menu_atual:
            mostrar_dashboard_gerencial(pedido_controller)
            historico_view.mostrar_interface()
        else:
            configuracoes_view.mostrar_interface()
        
    except Exception as e:
        # Mensagem de erro clara para planilha de mapeamento e Google Sheets
        st.error(f"""
        ❌ Erro ao inicializar o sistema

        Verifique:
        1. Se o arquivo .env está correto
        2. Se o caminho da planilha de mapeamento existe: {PLANILHA_MAPEAMENTO}
        3. Se você tem permissão de acesso à planilha de mapeamento
        4. Se deseja sincronizar pedidos com Google Sheets, configure as credenciais de conta de serviço corretamente (com o campo 'client_email')
        
        Detalhes: {str(e)}
        """)

if __name__ == "__main__":
    main()

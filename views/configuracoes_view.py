import streamlit as st
import os
from datetime import datetime
import platform
from utils.sheets_pedidos_sync import SheetsPedidosSync

class ConfiguracoesView:
    def __init__(self):
        self.base_dir = os.path.join(
            os.path.expanduser("~"),
            "OneDrive - Yazaki",
            "Solicitação",
            "Pedidos"
        )
        self.arquivo_backup = os.path.join(self.base_dir, "backup")
        self.sheets_sync = SheetsPedidosSync()

    def mostrar_interface(self):
        st.markdown("### ⚙️ Configurações do Sistema", unsafe_allow_html=True)
        
        # Proteção por senha
        if 'config_senha_ok' not in st.session_state:
            st.session_state['config_senha_ok'] = False
        if not st.session_state['config_senha_ok']:
            senha = st.text_input("Digite a senha para acessar as configurações:", type="password")
            if st.button("Acessar Configurações"):
                if senha == "pyh#1874":
                    st.session_state['config_senha_ok'] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta! Tente novamente.")
            return
        
        # Tabs para diferentes configurações
        tab1, tab2, tab3 = st.tabs(["Sistema", "Google Sheets", "Backups"])
        
        with tab1:
            self._mostrar_info_sistema()
            
        with tab2:
            self._mostrar_config_sheets()
            
        with tab3:
            self._mostrar_backups()

    def _mostrar_info_sistema(self):
        # Informações do Sistema
        st.markdown("#### 💻 Informações do Sistema")
        st.markdown(f"""
        - **Sistema Operacional:** {platform.system()}
        - **Versão Python:** {platform.python_version()}
        - **Ambiente:** {"Streamlit Cloud" if os.getenv('IS_STREAMLIT_CLOUD', '0') == '1' else "Local"}
        """)
        
        st.markdown("---")
        
        # Mostrar localização dos arquivos
        st.markdown("#### 📁 Localização dos Arquivos")
        st.markdown(f"""
        **Pasta Principal:** {self.base_dir}  
        **Pasta de Backup:** {self.arquivo_backup}        """)

    def _mostrar_config_sheets(self):
        self.sheets_sync.render_config_page()

    def _mostrar_backups(self):
        # Mostrar backups disponíveis
        st.markdown("#### 💾 Backups Disponíveis")
        
        if not os.path.exists(self.arquivo_backup):
            os.makedirs(self.arquivo_backup, exist_ok=True)
            
        backups = sorted([
            f for f in os.listdir(self.arquivo_backup)
            if f.endswith('.xlsx')
        ], reverse=True)
        
        if not backups:
            st.info("Nenhum backup encontrado")
        else:
            for backup in backups:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(backup)
                with col2:
                    if st.button("📥 Restaurar", key=f"restore_{backup}"):
                        try:
                            # Restaurar backup                            backup_path = os.path.join(self.arquivo_backup, backup)
                            os.replace(backup_path, self.arquivo_pedidos)
                            st.success("Backup restaurado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao restaurar backup: {str(e)}")
        
        # Informações sobre backups
        st.markdown("#### ℹ️ Informações")
        st.markdown("""
        - O sistema mantém automaticamente os últimos 10 backups
        - Um novo backup é criado sempre que há alterações nos pedidos
        - Os backups são nomeados com data e hora para fácil identificação
        - Use o botão "Restaurar" para voltar a uma versão anterior dos dados
        """)
        
        # Aviso importante
        st.warning("""
        **⚠️ Atenção!**  
        Ao restaurar um backup, a versão atual dos dados será substituída.
        Certifique-se de que deseja realmente fazer isso antes de prosseguir.
        """)
import os
import json
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SheetsPedidosSync:
    def __init__(self):
        # URL da planilha do Google Sheets (você pode alterar isso nas configurações)
        self.config_file = "config.json"
        self.SPREADSHEET_URL = None
        self.client = None
        self.load_config()
        self.initialize_client()

    def load_config(self):
        """Carrega as credenciais do Google Sheets"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    # Usar URL da planilha do config se existir, senão usar vazio
                    self.SPREADSHEET_URL = self.config.get('sheets_url', '')
            else:
                self.config = {
                    'sheets_credentials': None,
                    'sheets_url': ''
                }
                self.SPREADSHEET_URL = self.config['sheets_url']
                self.save_config()
        except Exception as e:
            st.error(f"Erro ao carregar configurações: {str(e)}")
            self.config = {'sheets_credentials': None}
            self.SPREADSHEET_URL = ''

    def save_config(self):
        """Salva configuração atual"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            st.error(f"Erro ao salvar configurações: {str(e)}")

    def initialize_client(self):
        """Inicializa o cliente do Google Sheets"""
        try:
            if "sheets_credentials" in st.secrets:
                creds = json.loads(st.secrets["sheets_credentials"])
            else:
                creds = self.config.get('sheets_credentials')
            
            if creds:
                if not creds.get('client_email'):
                    st.warning('Credenciais do Google Sheets inválidas: falta o campo "client_email".')
                    self.client = None
                    return
                
                self.client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(
                    creds,
                    scopes=['https://spreadsheets.google.com/feeds', 
                           'https://www.googleapis.com/auth/drive']
                ))
                # Testar conexão
                try:
                    self.client.open_by_url(self.SPREADSHEET_URL)
                except Exception as e:
                    st.warning(f"Erro ao acessar planilha: {str(e)}")
                    self.client = None
        except Exception as e:
            st.error(f"Erro ao inicializar cliente do Google Sheets: {str(e)}")
            self.client = None

    def _get_or_create_worksheet(self, sheet, name, rows=100, cols=20):
        """Obtém ou cria uma aba na planilha"""
        try:
            return sheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            return sheet.add_worksheet(title=name, rows=rows, cols=cols)

    def salvar_pedido_completo(self, df_pedidos: pd.DataFrame, df_itens: pd.DataFrame) -> tuple[bool, str]:
        """Salva pedidos e itens em abas separadas no Google Sheets"""
        try:
            if not self.client:
                raise ValueError("Cliente do Google Sheets não configurado. Verifique as credenciais.")

            if not self.SPREADSHEET_URL:
                raise ValueError("URL da planilha não configurada.")

            # Abrir a planilha pelo URL
            try:
                sheet = self.client.open_by_url(self.SPREADSHEET_URL)
            except Exception as e:
                raise ValueError(f"Erro ao abrir planilha: {str(e)}")

            # Preparar os dados dos pedidos
            df_pedidos = df_pedidos.fillna("")
            pedidos_values = [df_pedidos.columns.tolist()] + df_pedidos.values.tolist()
            pedidos_values = [[str(cell) if pd.notna(cell) else "" for cell in row] for row in pedidos_values]

            # Preparar os dados dos itens
            df_itens = df_itens.fillna("")
            itens_values = [df_itens.columns.tolist()] + df_itens.values.tolist()
            itens_values = [[str(cell) if pd.notna(cell) else "" for cell in row] for row in itens_values]

            # Atualizar aba de Pedidos
            worksheet_pedidos = self._get_or_create_worksheet(sheet, "Pedidos")
            worksheet_pedidos.clear()
            worksheet_pedidos.append_rows(pedidos_values, value_input_option="USER_ENTERED")

            # Atualizar aba de Itens
            worksheet_itens = self._get_or_create_worksheet(sheet, "Itens")
            worksheet_itens.clear()
            worksheet_itens.append_rows(itens_values, value_input_option="USER_ENTERED")

            # Formatar as abas
            self._format_worksheets(sheet)

            return True, "Pedido salvo com sucesso no Google Sheets!"
        except Exception as e:
            return False, f"Erro ao salvar no Google Sheets: {str(e)}"

    def _format_worksheets(self, sheet):
        """Aplica formatação básica nas abas"""
        try:
            # Formatar aba de Pedidos
            ws_pedidos = sheet.worksheet("Pedidos")
            ws_pedidos.format('A1:Z1', {
                "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8},
                "horizontalAlignment": "CENTER",
                "textFormat": {"bold": True}
            })
            ws_pedidos.freeze(rows=1)

            # Formatar aba de Itens
            ws_itens = sheet.worksheet("Itens")
            ws_itens.format('A1:Z1', {
                "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8},
                "horizontalAlignment": "CENTER",
                "textFormat": {"bold": True}
            })
            ws_itens.freeze(rows=1)
        except Exception as e:
            st.warning(f"Aviso: Não foi possível aplicar a formatação: {str(e)}")

    def sincronizar_mapeamento(self, arquivo_mapeamento: str) -> tuple[bool, str]:
        """Sincroniza o arquivo de mapeamento com o Google Sheets"""
        try:
            if not self.client:
                raise ValueError("Cliente do Google Sheets não configurado. Verifique as credenciais.")

            if not self.SPREADSHEET_URL:
                raise ValueError("URL da planilha não configurada.")

            # Ler o arquivo de mapeamento
            try:
                df = pd.read_excel(
                    arquivo_mapeamento,
                    sheet_name='Projeto',
                    dtype={
                        'RACK': str,
                        'CÓD Yazaki': str,
                        'Codigo Cabo': str,
                        'Secção': str,
                        'Cor': str,
                        'Cliente': str,
                        'Locação': str,
                        'Projeto': str,
                        'Cod OES': str
                    }
                )
            except Exception as e:
                raise ValueError(f"Erro ao ler arquivo de mapeamento: {str(e)}")

            # Abrir a planilha do Google Sheets
            try:
                sheet = self.client.open_by_url(self.SPREADSHEET_URL)
            except Exception as e:
                raise ValueError(f"Erro ao abrir planilha: {str(e)}")

            # Preparar os dados
            df = df.fillna("")
            values = [df.columns.tolist()] + df.values.tolist()
            values = [[str(cell) if pd.notna(cell) else "" for cell in row] for row in values]

            # Atualizar ou criar a aba Projeto
            worksheet = self._get_or_create_worksheet(sheet, "Projeto", rows=len(values)+100, cols=len(values[0])+5)
            worksheet.clear()
            worksheet.append_rows(values, value_input_option="USER_ENTERED")

            # Formatar a aba
            worksheet.format('A1:Z1', {
                "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8},
                "horizontalAlignment": "CENTER",
                "textFormat": {"bold": True}
            })
            worksheet.freeze(rows=1)

            return True, "Mapeamento sincronizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao sincronizar mapeamento: {str(e)}"

    def render_config_page(self):
        """Renderiza página de configuração do Google Sheets"""
        st.title("⚙️ Configuração do Google Sheets")

        # URL da planilha
        st.markdown("### URL da Planilha")
        sheets_url = st.text_input(
            "URL da Planilha do Google Sheets",
            value=self.SPREADSHEET_URL or ""
        )
        if st.button("💾 Salvar URL") and sheets_url:
            self.config['sheets_url'] = sheets_url
            self.SPREADSHEET_URL = sheets_url
            self.save_config()
            st.success("✅ URL salva com sucesso!")
            st.experimental_rerun()

        # Status da conexão
        st.markdown("### Status da Conexão")
        if self.client:
            st.success("✅ Conectado ao Google Sheets")
            if st.button("🔄 Testar Conexão"):
                try:
                    self.client.open_by_url(self.SPREADSHEET_URL)
                    st.success("✅ Conexão testada com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro na conexão: {str(e)}")

            # Botão para sincronizar mapeamento
            st.markdown("### Sincronização do Mapeamento")
            if st.button("🔄 Sincronizar Mapeamento"):
                arquivo_mapeamento = "Mapeamento de Racks - Cabos.xlsx"
                if os.path.exists(arquivo_mapeamento):
                    with st.spinner("Sincronizando mapeamento..."):
                        success, message = self.sincronizar_mapeamento(arquivo_mapeamento)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("Arquivo de mapeamento não encontrado!")
        else:
            st.error("❌ Não conectado ao Google Sheets")
            st.info("Configure as credenciais nas configurações para conectar.")

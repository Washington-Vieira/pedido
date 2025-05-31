import pandas as pd
from datetime import datetime
from models.pedido import Pedido
from typing import List, Optional
import streamlit as st
import os
import shutil
from utils.sheets_pedidos_sync import SheetsPedidosSync
import webbrowser
import pathlib
import base64

class PedidoController:
    def __init__(self, caminho_planilha: str):
        """
        Inicializa o controlador com o caminho da planilha de localizações
        Args:
            caminho_planilha: Caminho da planilha que contém as localizações (definido no .env)
        """
        self.caminho_planilha = caminho_planilha
        self.pedidos = []
        self.arquivo_pedidos = os.path.join('pedidos', 'pedidos.xlsx')
        self.diretorio_backup = os.path.join('pedidos', 'backup')
        self.sheets_sync = SheetsPedidosSync()
        
        # Criar diretório de backup se não existir
        os.makedirs(self.diretorio_backup, exist_ok=True)

    @staticmethod
    @st.cache_data
    def _carregar_planilha(caminho: str) -> List[Pedido]:
        """
        Carrega os dados da planilha SOMENTE do Google Sheets.
        """
        try:
            sheets_sync = SheetsPedidosSync()
            if sheets_sync.client and sheets_sync.SPREADSHEET_URL:
                sheet = sheets_sync.client.open_by_url(sheets_sync.SPREADSHEET_URL)
                worksheet = sheet.worksheet("Projeto")
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
            else:
                raise Exception("Não foi possível conectar ao Google Sheets. Verifique as credenciais e a URL da planilha.")
            
            # Mapeia os nomes das colunas da planilha
            colunas_mapeadas = {
                'RACK': 'rack',
                'CÓD Yazaki': 'cod_yazaki',
                'Codigo Cabo': 'codigo_cabo',
                'Secção': 'seccao',
                'Cor': 'cor',
                'Cliente': 'cliente',
                'Locação': 'locacao',
                'Projeto': 'projeto',
                'Cod OES': 'cod_oes'
            }
            
            # Renomeia as colunas para corresponder aos nomes dos atributos da classe
            df = df.rename(columns=colunas_mapeadas)
            
            # Limpa os dados
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].fillna('').astype(str).str.strip()
            
            # Converte o DataFrame para lista de objetos Pedido
            pedidos = [
                Pedido(
                    id=idx + 1,
                    rack=row['rack'],
                    cod_yazaki=row['cod_yazaki'],
                    codigo_cabo=row['codigo_cabo'],
                    seccao=row['seccao'],
                    cor=row['cor'],
                    cliente=row['cliente'],
                    locacao=row['locacao'],
                    projeto=row['projeto'],
                    cod_oes=row['cod_oes']
                )
                for idx, row in df.iterrows()
            ]
            
            return pedidos
            
        except Exception as e:
            raise Exception(f"Erro ao carregar dados da planilha do Google Sheets: {str(e)}")

    def carregar_dados(self):
        """Carrega os dados usando a função cacheada"""
        self.pedidos = self._carregar_planilha(self.caminho_planilha)
        return self.pedidos

    def _fazer_backup(self):
        """Faz backup do arquivo antes de modificá-lo"""
        if os.path.exists(self.arquivo_pedidos):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(
                self.diretorio_backup, 
                f"pedidos_backup_{timestamp}.xlsx"
            )
            
            # Copiar arquivo atual para backup
            pd.read_excel(self.arquivo_pedidos).to_excel(backup_path, index=False)
            
            # Manter apenas os últimos 10 backups
            backups = sorted([
                os.path.join(self.diretorio_backup, f) 
                for f in os.listdir(self.diretorio_backup)
                if f.endswith('.xlsx')
            ])
            while len(backups) > 10:
                os.remove(backups.pop(0))

    def _ler_pedidos(self) -> pd.DataFrame:
        """Lê a aba 'Pedidos' do Google Sheets com cache"""
        try:
            # Verificar cache
            if 'cache_pedidos' in st.session_state:
                return st.session_state['cache_pedidos']

            if self.sheets_sync.client and self.sheets_sync.SPREADSHEET_URL:
                sheet = self.sheets_sync.client.open_by_url(self.sheets_sync.SPREADSHEET_URL)
                worksheet = sheet.worksheet("Pedidos")
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
                # Garantir que as colunas existam
                if 'Ultima_Atualizacao' not in df.columns:
                    df['Ultima_Atualizacao'] = ""
                if 'Responsavel_Atualizacao' not in df.columns:
                    df['Responsavel_Atualizacao'] = ""
                
                # Salvar no cache
                st.session_state['cache_pedidos'] = df
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            if "Quota exceeded" in str(e) or "[429]" in str(e):
                # Se tiver cache, usa ele
                if 'cache_pedidos' in st.session_state:
                    return st.session_state['cache_pedidos']
                return pd.DataFrame()
            return pd.DataFrame()

    def _ler_itens(self) -> pd.DataFrame:
        """Lê a aba 'Itens' do Google Sheets com cache"""
        try:
            # Verificar cache
            if 'cache_itens' in st.session_state:
                return st.session_state['cache_itens']

            if self.sheets_sync.client and self.sheets_sync.SPREADSHEET_URL:
                sheet = self.sheets_sync.client.open_by_url(self.sheets_sync.SPREADSHEET_URL)
                worksheet = sheet.worksheet("Itens")
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
                
                # Salvar no cache
                st.session_state['cache_itens'] = df
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            if "Quota exceeded" in str(e) or "[429]" in str(e):
                # Se tiver cache, usa ele
                if 'cache_itens' in st.session_state:
                    return st.session_state['cache_itens']
                return pd.DataFrame()
            return pd.DataFrame()

    def _gerar_numero_pedido(self) -> str:
        """Gera um número único para o pedido"""
        try:
            df = self._ler_pedidos()
            if df.empty:
                return "REQ-001"
            ultimo_numero = df["Numero_Pedido"].iloc[-1]
            numero = int(ultimo_numero.split("-")[1]) + 1
            return f"REQ-{numero:03d}"
        except:
            return "REQ-001"

    def salvar_pedido(self, pedido_info: dict) -> str:
        """Salva o pedido localmente e sincroniza com Google Sheets"""
        numero_pedido = self._gerar_numero_pedido()
        
        try:
            # Carregar dados existentes
            df_pedidos = self._ler_pedidos()
            df_itens = self._ler_itens()
            
            # Criar novo registro de pedido
            novo_pedido = pd.DataFrame([{
                "Numero_Pedido": numero_pedido,
                "Data": pedido_info["data"].strftime('%d/%m/%Y %H:%M'),
                "Cliente": pedido_info["cliente"],
                "RACK": pedido_info["rack"],
                "Localizacao": pedido_info["locacao"],
                "Solicitante": pedido_info["solicitante"],
                "Observacoes": pedido_info["observacoes"] if pedido_info["observacoes"] else "",
                "Urgente": "Sim" if pedido_info.get("urgente") else "Não",
                "Status": "Pendente",
                "Ultima_Atualizacao": datetime.now().strftime('%d/%m/%Y %H:%M'),
                "Responsavel_Atualizacao": pedido_info["solicitante"]
            }])
            
            # Criar registros de itens
            novos_itens = []
            for item in pedido_info["itens"]:
                novos_itens.append({
                    "Numero_Pedido": numero_pedido,
                    "cod_yazaki": item["cod_yazaki"],
                    "codigo_cabo": item["codigo_cabo"],
                    "seccao": item["seccao"],
                    "cor": item["cor"],
                    "quantidade": item["quantidade"]
                })
            
            df_novos_itens = pd.DataFrame(novos_itens)
            
            # Concatenar com dados existentes
            df_pedidos = pd.concat([df_pedidos, novo_pedido], ignore_index=True)
            df_itens = pd.concat([df_itens, df_novos_itens], ignore_index=True)
            
            # Fazer backup antes de salvar
            self._fazer_backup()
            
            # Salvar localmente
            with pd.ExcelWriter(self.arquivo_pedidos, engine='openpyxl') as writer:
                df_pedidos.to_excel(writer, sheet_name='Pedidos', index=False)
                df_itens.to_excel(writer, sheet_name='Itens', index=False)
            
            # Sincronizar com Google Sheets
            success, message = self.sheets_sync.salvar_pedido_completo(df_pedidos, df_itens)
            if not success:
                st.warning(f"Aviso: {message}")
            
            return numero_pedido
            
        except Exception as e:
            raise Exception(f"Erro ao salvar pedido: {str(e)}")

    def buscar_pedidos(self, 
                      numero_pedido: Optional[str] = None,
                      cliente: Optional[str] = None,
                      status: Optional[str] = None) -> pd.DataFrame:
        """Busca pedidos com filtros opcionais"""
        try:
            df = self._ler_pedidos()
            
            # Se não conseguiu ler os pedidos, retorna DataFrame vazio
            if df.empty:
                return df
            
            # Preencher valores NaN com string vazia
            df = df.fillna("")
            
            if numero_pedido:
                df = df[df["Numero_Pedido"].str.contains(numero_pedido, case=False)]
            if cliente:
                df = df[df["Cliente"].str.contains(cliente, case=False)]
            if status:
                df = df[df["Status"] == status]
            
            return df
        except Exception as e:
            # Retorna DataFrame vazio em caso de erro
            return pd.DataFrame()

    def get_pedido_detalhes(self, numero_pedido: str) -> dict:
        """Retorna os detalhes completos de um pedido, consultando apenas o Google Sheets, com cache e tratamento de quota."""
        try:
            # Usar cache em session_state
            cache_key = f"detalhes_pedido_{numero_pedido}"
            if cache_key in st.session_state:
                return st.session_state[cache_key]
            if not hasattr(self, 'sheets_sync') or not self.sheets_sync.client:
                st.warning("Por favor, recarregue a página e aguarde um minuto antes de tentar novamente.")
                return {}
            detalhes = self.sheets_sync.get_pedido_detalhes(numero_pedido)
            st.session_state[cache_key] = detalhes
            return detalhes
        except Exception as e:
            if "Quota exceeded" in str(e) or "[429]" in str(e):
                st.warning("Por favor, recarregue a página e aguarde um minuto antes de tentar novamente.")
            return {}

    def atualizar_status_pedido(self, numero_pedido: str, novo_status: str, responsavel: str):
        """Atualiza o status de um pedido localmente e no Google Sheets."""
        try:
            # Carregar dados existentes do Sheets
            df_pedidos = self._ler_pedidos()
            df_itens = self._ler_itens()

            # Encontrar o índice do pedido no DataFrame
            idx = df_pedidos[df_pedidos['Numero_Pedido'] == numero_pedido].index[0]

            # Atualizar status no DataFrame
            ultima_atualizacao = datetime.now().strftime('%d/%m/%Y %H:%M')
            df_pedidos.loc[idx, 'Status'] = novo_status
            df_pedidos.loc[idx, 'Ultima_Atualizacao'] = ultima_atualizacao
            df_pedidos.loc[idx, 'Responsavel_Atualizacao'] = responsavel

            # Fazer backup antes de salvar localmente
            self._fazer_backup()

            # Salvar localmente
            with pd.ExcelWriter(self.arquivo_pedidos, engine='openpyxl') as writer:
                df_pedidos.to_excel(writer, sheet_name='Pedidos', index=False)
                df_itens.to_excel(writer, sheet_name='Itens', index=False)

            # Atualizar apenas o status no Google Sheets
            success_sheets, message_sheets = self.sheets_sync.atualizar_status_pedido_sheets(
                numero_pedido=numero_pedido,
                novo_status=novo_status,
                ultima_atualizacao=ultima_atualizacao,
                responsavel=responsavel
            )

            # Limpar cache após atualização
            if 'cache_pedidos' in st.session_state:
                del st.session_state['cache_pedidos']
            cache_key = f"detalhes_pedido_{numero_pedido}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]

        except Exception as e:
            # Não exibe mensagem de erro, apenas retorna silenciosamente
            pass

    @staticmethod
    @st.cache_data
    def filtrar_dados(pedidos: List[Pedido], cliente: Optional[str] = None, 
                     rack: Optional[str] = None) -> List[Pedido]:
        """Filtra os dados com cache"""
        resultado = pedidos
        if cliente:
            cliente = cliente.lower()
            resultado = [p for p in resultado if p.cliente.lower() == cliente]
        if rack:
            rack = rack.lower()
            resultado = [p for p in resultado if p.rack.lower() == rack]
        return resultado

    def buscar_por_cliente(self, cliente: str) -> List[Pedido]:
        """Busca pedidos por cliente (case-insensitive)"""
        return self.filtrar_dados(self.pedidos, cliente=cliente)

    def buscar_por_rack(self, rack: str) -> List[Pedido]:
        """Busca pedidos por rack (case-insensitive)"""
        return self.filtrar_dados(self.pedidos, rack=rack)

    def buscar_por_cliente_e_rack(self, cliente: str, rack: str) -> List[Pedido]:
        """Busca pedidos por cliente e rack (case-insensitive)"""
        return self.filtrar_dados(self.pedidos, cliente=cliente, rack=rack)

    def imprimir_pedido(self, numero_pedido: str):
        """Gera um arquivo HTML do pedido e retorna o link HTML para visualização e impressão no navegador do usuário"""
        try:
            # Buscar detalhes do pedido
            detalhes = self.get_pedido_detalhes(numero_pedido)
            
            # Criar diretório temporário se não existir
            temp_dir = os.path.join(os.getcwd(), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Gerar caminho absoluto para o arquivo HTML
            temp_html = os.path.join(temp_dir, f"pedido_{numero_pedido}.html")
            
            # Gerar HTML para impressão
            html = f"""
            <html>
            <head>
                <meta charset=\"utf-8\">
                <title>Pedido #{numero_pedido}</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{ 
                        text-align: center;
                        margin-bottom: 30px;
                        padding-bottom: 20px;
                        border-bottom: 2px solid #eee;
                    }}
                    .info {{ 
                        margin-bottom: 30px;
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 6px;
                    }}
                    .item {{ 
                        margin-bottom: 20px;
                        padding: 15px;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                    }}
                    .item h3 {{
                        margin-top: 0;
                        color: #2c3e50;
                    }}
                    .signatures {{ 
                        margin-top: 50px;
                        text-align: center;
                        display: flex;
                        justify-content: space-around;
                        page-break-inside: avoid;
                    }}
                    .signature-line {{ 
                        width: 200px; 
                        border-top: 1px solid black; 
                        margin: 50px auto 10px auto; 
                    }}
                    .print-button {{
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    }}
                    .print-button:hover {{
                        background-color: #0056b3;
                    }}
                    @media print {{
                        body {{ 
                            background-color: white;
                            margin: 0;
                            padding: 0;
                        }}
                        .container {{
                            box-shadow: none;
                            padding: 0;
                            max-width: 100%;
                        }}
                        .print-button {{
                            display: none;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class=\"container\">
                    <div class=\"header\">
                        <h1>Pedido de Requisição #{numero_pedido}</h1>
                        <p>Data: {detalhes['info']['Data']}</p>
                    </div>
                    
                    <div class=\"info\">
                        <h2>Informações do Pedido</h2>
                        <p><strong>Cliente:</strong> {detalhes['info']['Cliente']}</p>
                        <p><strong>RACK:</strong> {detalhes['info']['RACK']}</p>
                        <p><strong>Localização:</strong> {detalhes['info']['Localizacao']}</p>
                        <p><strong>Solicitante:</strong> {detalhes['info']['Solicitante']}</p>
                        <p><strong>Status:</strong> {detalhes['status']}</p>
                    </div>
                    
                    <div class=\"items\">
                        <h2>Itens</h2>
            """
            
            # Adicionar itens
            for idx, item in enumerate(detalhes['itens'], 1):
                html += f"""
                        <div class=\"item\">
                            <h3>Item {idx}</h3>
                            <p><strong>CÓD Yazaki:</strong> {item['cod_yazaki']}</p>
                            <p><strong>Código Cabo:</strong> {item['codigo_cabo']}</p>
                            <p><strong>Seção:</strong> {item['seccao']}</p>
                            <p><strong>Cor:</strong> {item['cor']}</p>
                            <p><strong>Quantidade:</strong> {item['quantidade']}</p>
                        </div>
                """
            
            # Adicionar área de assinaturas e botão de impressão
            html += """
                    </div>
                    
                    <div class=\"signatures\">
                        <div>
                            <div class=\"signature-line\"></div>
                            <p>Solicitante</p>
                        </div>
                        
                        <div>
                            <div class=\"signature-line\"></div>
                            <p>Aprovação</p>
                        </div>
                    </div>
                </div>
                <button onclick=\"window.print()\" class=\"print-button\">Imprimir Pedido</button>
            </body>
            </html>
            """
            
            # Salvar HTML temporário
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html)
            
            # Lê o HTML para base64
            with open(temp_html, "rb") as f:
                html_bytes = f.read()
                b64 = base64.b64encode(html_bytes).decode()
            
            href = f'data:text/html;base64,{b64}'
            link_html = (
                f'<a href="{href}" target="_blank" style="font-size:18px;color:#007bff;font-weight:bold;">'
                '🔗 Abrir comprovante do pedido em nova guia</a>'
            )
            return link_html
        except Exception as e:
            return None
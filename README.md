# Sistema de Gestão de Pedidos de Bobina

Sistema desenvolvido em Python com Streamlit para gerenciamento de pedidos de requisição, integrado ao Google Sheets e com suporte a importação/exportação via Excel.

---

## Requisitos

- Python 3.10+ (recomendado)
- Conta Google com permissão de edição na planilha
- Credenciais de serviço do Google (JSON)
- [Streamlit](https://streamlit.io/)
- [gspread](https://gspread.readthedocs.io/)
- Outras dependências listadas em `requirements.txt`

---

## Instalação

1. **Clone este repositório**
   ```bash
   git clone https://github.com/SEU_USUARIO/pedido.git
   cd pedido
   ```

2. **Crie e ative o ambiente virtual**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as credenciais do Google Sheets**
   - Crie um arquivo `secrets.toml` em `.streamlit/` com:
     ```
     [general]
     sheets_url = "URL_DA_SUA_PLANILHA"
     sheets_credentials = 'CONTEUDO_JSON_DAS_CREDENCIAIS'
     ```
   - Compartilhe a planilha com o e-mail do campo `client_email` das credenciais.

---

## Uso

1. Ative o ambiente virtual (se ainda não estiver ativo)
2. Execute o aplicativo:
   ```bash
   streamlit run app.py
   ```
3. O app abrirá no navegador. Acesse a aba de configurações para conectar ao Google Sheets e importar localizações.

---

## Funcionalidades

- Criação e edição de pedidos de bobina
- Visualização e filtro de pedidos por cliente, status, data, etc.
- Atualização de status dos pedidos
- Integração total com Google Sheets (leitura e escrita)
- Importação de localizações via arquivo Excel (aba "Projeto")
- Backup automático dos dados locais
- Interface amigável e responsiva

---

## Estrutura do Projeto

```
.
├── app.py                  # Arquivo principal do Streamlit
├── requirements.txt        # Dependências do projeto
├── config.json             # Configurações locais
├── .streamlit/
│   └── secrets.toml        # Credenciais e URL do Google Sheets
├── models/
│   └── pedido.py           # Modelo de dados do pedido
├── views/
│   ├── configuracoes_view.py
│   ├── pedido_form_view.py
│   ├── pedido_view.py
│   └── pedido_historico_view.py
├── controllers/
│   └── pedido_controller.py
├── utils/
│   ├── sheets_pedidos_sync.py
│   └── sheets_sync.py
└── pedidos/
    └── (backups, arquivos locais, etc.)
```

---

## Fluxo do Sistema (Mermaid)

```mermaid
flowchart TD
    A[Usuário acessa o app] --> B{Configuração inicial?}
    B -- Sim --> C[Configura Google Sheets e credenciais]
    B -- Não --> D[Menu principal]
    C --> D
    D --> E[Criação de Pedido]
    D --> F[Histórico de Pedidos]
    D --> G[Configurações]
    E --> H[Preenche formulário]
    H --> I[Salva pedido]
    I --> J{Google Sheets disponível?}
    J -- Sim --> K[Salva no Google Sheets e local]
    J -- Não --> L[Salva apenas localmente]
    F --> M[Visualiza, filtra e exporta pedidos]
    G --> N[Importa localizações via Excel]
    N --> O[Sobrescreve aba Projeto no Google Sheets]
```

---

## Dicas e Observações

- **Importação de localizações:** Use a aba de configurações para importar um arquivo Excel com a aba "Projeto". Isso sobrescreve as localizações no Google Sheets.
- **Backup:** O sistema faz backup automático dos dados locais antes de qualquer alteração.
- **Limite de arquivos grandes:** Não faça commit de arquivos Excel grandes no repositório. Use `.gitignore` para evitar problemas.
- **Problemas de autenticação:** Certifique-se de que as credenciais do Google estão corretas e que a planilha está compartilhada com o e-mail do serviço.

---

## Licença

MIT

# Sistema de Gestão de Pedidos

Sistema desenvolvido em Python com Streamlit para gerenciamento de pedidos de requisição, integrado com planilha Excel em rede.

## Requisitos

- Python 3.13.3
- Acesso à planilha Excel em rede

## Instalação

1. Clone este repositório
2. Crie um ambiente virtual:
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/Mac:
```bash
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure o arquivo `.env`:
- Crie uma cópia do arquivo `.env.example` e renomeie para `.env`
- Edite o arquivo `.env` e configure o caminho da planilha:
```
CAMINHO_PLANILHA=\\caminho\para\sua\planilha.xlsx
```

## Uso

1. Ative o ambiente virtual (se ainda não estiver ativo)
2. Execute o aplicativo:
```bash
streamlit run app.py
```

3. O aplicativo abrirá automaticamente no seu navegador padrão

## Funcionalidades

- Criação de novos pedidos
- Visualização de pedidos existentes
- Atualização de status dos pedidos
- Filtros por cliente e status
- Integração com planilha Excel em rede
- Interface amigável e responsiva

## Estrutura do Projeto

```
.
├── app.py              # Arquivo principal
├── requirements.txt    # Dependências do projeto
├── .env               # Configurações de ambiente
├── models/            # Modelos de dados
│   └── pedido.py
├── views/             # Interface do usuário
│   └── pedido_view.py
└── controllers/       # Lógica de negócios
    └── pedido_controller.py
``` # pedidos_bobina
# pedido

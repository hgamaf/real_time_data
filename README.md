# 📊 Real-Time Data Processing System

![Dashboard Preview](img/dashboard_img.png)

Sistema completo de processamento e visualização de dados em tempo real que monitora um arquivo CSV, processa via Kafka e exibe os dados em um dashboard interativo usando Streamlit.

## 🎯 Funcionalidades Principais

✅ **Dashboard Interativo**: Interface web moderna com Streamlit  
✅ **Tempo Real**: Atualização automática a cada 3 segundos  
✅ **Visualizações Ricas**: Gráficos de barras, histogramas, pizza e scatter  
✅ **Métricas Dinâmicas**: Valor total, médio, contadores e estatísticas  
✅ **Kafka Integration**: Processamento de dados via Apache Kafka  
✅ **UI do Kafka**: Interface web para monitorar tópicos e mensagens (AKHQ)  
✅ **Sincronização Completa**: Remoção de dados do CSV reflete no dashboard  
✅ **Testes Automatizados**: Bateria completa de testes com pytest  
✅ **Fácil de Usar**: Adicione/remova dados no CSV ou via UI e veja as mudanças instantaneamente  

## 🚀 Início Rápido

### Método Completo (Recomendado)
```bash
# 1. Iniciar infraestrutura Kafka
docker-compose up -d

# 2. Executar o producer CSV
python csv-monitor/csv_producer.py

# 3. Executar dashboard (novo terminal)
python streamlit/dashboard.py

# 4. Acessar interfaces
# Dashboard: http://localhost:8501
# Kafka UI: http://localhost:8080
```

### Método Simples (Apenas Dashboard)
```bash
# 1. Executar apenas o dashboard
python streamlit/dashboard.py

# 2. Abrir no navegador
# http://localhost:8501

# 3. Testar adicionando dados
echo "8,Roberto,45,Fortaleza,275.50" >> data/input.csv
```

## 📊 Dashboard Features

### Métricas em Tempo Real
- 💰 **Valor Total**: Soma de todos os valores
- 📈 **Valor Médio**: Média dos valores  
- 📋 **Total Registros**: Quantidade de linhas
- 👥 **Idade Média**: Média das idades

### Visualizações Interativas
- 📊 **Gráfico de Barras**: Valor por cidade
- 📈 **Histograma**: Distribuição de idades  
- 🥧 **Gráfico de Pizza**: Percentual por cidade
- 🔍 **Scatter Plot**: Relação valor x idade

### Controles
- 🔄 **Auto-refresh**: Atualização automática (3s)
- 🗑️ **Limpar Cache**: Remove dados antigos do dashboard
- 📋 **Tabelas Dinâmicas**: Dados completos e estatísticas
- 📄 **Info do Arquivo**: Metadados em tempo real

## 🏗️ Arquitetura

### Arquitetura Completa (Atual)
```
📁 CSV File → 🔍 CSV Monitor → 📡 Kafka → 📊 Dashboard
    ↓              ↓              ↓         ↓
data/input.csv → csv_producer.py → Topic → Streamlit
                                    ↓
                              🖥️ AKHQ UI (Kafka Management)
```

### Fluxo de Dados
1. **CSV Monitor** detecta mudanças no arquivo `data/input.csv`
2. **Producer** envia dados para o tópico Kafka `csv-data`
3. **Dashboard** consome dados do Kafka em tempo real
4. **AKHQ UI** permite monitorar e inserir dados manualmente

## 📁 Estrutura do Projeto

```
real_time_data/
├── 📂 streamlit/           # Dashboard principal
│   └── dashboard.py        # Interface web Streamlit
├── 📂 csv-monitor/         # Monitor e Producer Kafka
│   └── csv_producer.py     # Monitora CSV e envia para Kafka
├── 📂 data/               # Dados de entrada  
│   └── input.csv          # Arquivo CSV monitorado
├── 📂 tests/              # Testes automatizados
│   ├── __init__.py        # Pacote de testes
│   ├── test_csv_producer.py    # Testes do CSV producer
│   ├── test_dashboard.py       # Testes do dashboard
│   └── test_integration.py     # Testes de integração
├── 📂 img/                # Imagens da documentação
│   └── dashboard_img.png   # Preview do dashboard
├── 🐳 docker-compose.yml  # Infraestrutura (Kafka, Zookeeper, AKHQ)
├── 📄 pyproject.toml      # Dependências Python
└── 📖 README.md           # Esta documentação
```

## 🔧 Configuração

### Formato do CSV
```csv
id,nome,idade,cidade,valor
1,João,25,São Paulo,100.50
2,Maria,30,Rio de Janeir`o,200.75
```

### Serviços Disponíveis
- **Dashboard Streamlit**: http://localhost:8501
- **Kafka UI (AKHQ)**: http://localhost:8080
- **Kafka Broker**: localhost:9092  
- **Zookeeper**: localhost:2181

### Como Inserir/Remover Dados

#### Via CSV (Automático)
```bash
# Adicionar nova linha no CSV
echo "11,Fernanda,29,Fortaleza,680.90" >> data/input.csv

# Remover dados (editar arquivo)
# O dashboard será automaticamente atualizado para refletir as mudanças
```

#### Via Kafka UI
1. Acesse http://localhost:8080
2. Clique em "Topics" → "csv-data"
3. Clique em "Produce to topic"
4. Use este formato JSON:
```json
{
  "id": 200,
  "nome": "Novo Usuario",
  "idade": 28,
  "cidade": "Recife",
  "valor": 450.00,
  "timestamp": "2025-08-26T19:47:00"
}
```

## 🧪 Testes

O projeto inclui uma bateria completa de testes automatizados:

### Executar Todos os Testes
```bash
# Executar todos os testes
uv run pytest tests/ -v

# Executar com cobertura
uv add pytest-cov --dev
uv run pytest tests/ --cov=. --cov-report=html
```

### Testes Específicos
```bash
# Testes do CSV Producer
uv run pytest tests/test_csv_producer.py -v

# Testes do Dashboard  
uv run pytest tests/test_dashboard.py -v

# Testes de Integração
uv run pytest tests/test_integration.py -v
```

### Cobertura dos Testes
- ✅ **CSV Producer**: Inicialização, leitura de CSV, envio para Kafka
- ✅ **Dashboard**: Processamento de mensagens, deduplicação, métricas
- ✅ **Integração**: Fluxo completo, tratamento de erros, monitoramento

## 🛠️ Tecnologias

### Backend & Processamento
- **Python 3.12+**: Linguagem principal
- **Apache Kafka**: Message broker para streaming de dados
- **Confluent Kafka Python**: Cliente Kafka para Python
- **Pandas**: Manipulação e análise de dados

### Frontend & Visualização
- **Streamlit**: Framework web para dashboards
- **Plotly**: Gráficos interativos e responsivos
- **AKHQ**: Interface web para gerenciamento do Kafka

### Infraestrutura
- **Docker & Docker Compose**: Containerização e orquestração
- **Apache Zookeeper**: Coordenação de serviços Kafka
- **UV**: Gerenciador de dependências Python moderno

## 🔧 Pré-requisitos

- **Docker & Docker Compose**: Para executar Kafka e serviços
- **Python 3.12+**: Para executar os scripts
- **UV** (opcional): Para gerenciamento de dependências

### Instalação do UV
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv
```

## 🐛 Troubleshooting

### Kafka não conecta
```bash
# Verificar se containers estão rodando
docker ps

# Reiniciar serviços
docker-compose restart

# Ver logs
docker logs kafka
docker logs akhq
```

### Dashboard não atualiza
- Verifique se o CSV producer está rodando
- Confirme se há dados no tópico Kafka via AKHQ UI
- Use o botão "🗑️ Limpar Cache" no dashboard
- Reinicie o dashboard Streamlit

### Dados removidos do CSV não somem do dashboard
- O sistema agora envia comandos de reset automaticamente
- Use o botão "🗑️ Limpar Cache" se necessário
- Verifique se o CSV producer detectou a mudança no arquivo

### Testes falhando
```bash
# Verificar dependências
uv sync

# Executar testes individualmente
uv run pytest tests/test_csv_producer.py -v -s
```

## 🎯 Casos de Uso

- 📊 **Monitoramento de Vendas**: Acompanhar vendas em tempo real
- 📈 **Dashboards Executivos**: Métricas para tomada de decisão  
- 🔍 **Análise de Dados**: Explorar padrões e tendências
- 📋 **Relatórios Dinâmicos**: Relatórios que se atualizam sozinhos

## 🤝 Contribuição

Contribuições são bem-vindas! Veja como:

1. Fork do projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

## 🎉 Resultado Final

### Interfaces Disponíveis

1. **📊 Dashboard Streamlit** (http://localhost:8501)
   - Visualizações em tempo real
   - Métricas dinâmicas
   - Gráficos interativos

2. **🖥️ Kafka UI - AKHQ** (http://localhost:8080)
   - Monitoramento de tópicos
   - Inserção manual de dados
   - Visualização de mensagens

### Status do Sistema
✅ **Kafka**: Processamento de streaming  
✅ **Dashboard**: Visualização em tempo real  
✅ **CSV Monitor**: Detecção automática de mudanças  
✅ **Sincronização**: Remoção de dados reflete no dashboard  
✅ **UI Management**: Interface para gerenciar dados  
✅ **Testes**: Bateria completa de testes automatizados  

### Funcionalidades Avançadas
- 🔄 **Reset Automático**: Quando dados são removidos do CSV, o dashboard é limpo automaticamente
- 🧪 **Testes Completos**: 9 testes cobrindo todas as funcionalidades principais
- 🗑️ **Controle Manual**: Botão para limpar cache quando necessário
- 📊 **Métricas Precisas**: Cálculos com tratamento de precisão decimal

**🚀 Sistema completo de streaming de dados com sincronização total funcionando!**
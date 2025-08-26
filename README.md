# 📊 Real-Time Data Processing System

![Dashboard Preview](img/dashboard_img.png)

Sistema de processamento e visualização de dados em tempo real que monitora um arquivo CSV e exibe os dados em um dashboard interativo usando Streamlit.

## 🎯 Funcionalidades Principais

✅ **Dashboard Interativo**: Interface web moderna com Streamlit  
✅ **Tempo Real**: Atualização automática a cada 3 segundos  
✅ **Visualizações Ricas**: Gráficos de barras, histogramas, pizza e scatter  
✅ **Métricas Dinâmicas**: Valor total, médio, contadores e estatísticas  
✅ **Fácil de Usar**: Adicione dados no CSV e veja as mudanças instantaneamente  

## 🚀 Início Rápido

### Método Simples (Recomendado)
```bash
# 1. Instalar UV (se não tiver)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Criar ambiente e instalar dependências
cd real_time_data
uv sync

# 3. Executar dashboard
cd streamlit
uv run streamlit run dashboard.py

# 4. Abrir no navegador
# http://localhost:8501

# 5. Testar adicionando dados
echo "8,Roberto,45,Fortaleza,275.50" >> data/input.csv
```

### Método Completo (com Kafka)
```bash
# 1. Iniciar infraestrutura
uv run python start.py

# 2. Executar componentes
cd csv-monitor && uv run python csv_producer.py  # Terminal 1
cd streamlit && uv run streamlit run dashboard.py  # Terminal 2
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
- 📋 **Tabelas Dinâmicas**: Dados completos e estatísticas
- 📄 **Info do Arquivo**: Metadados em tempo real

## 🏗️ Arquitetura

```
📁 CSV File → 🔍 Monitor → 📊 Dashboard
    ↓              ↓           ↓
data/input.csv → Python → Streamlit Web UI
```

**Arquitetura Avançada (Opcional):**
```
📁 CSV → 🔍 Monitor → 📡 Kafka → 🔄 Flink → 📊 Dashboard
```

## 📁 Estrutura do Projeto

```
real_time_data/
├── 📂 streamlit/           # Dashboard principal
│   └── dashboard.py        # Interface web
├── 📂 data/               # Dados de entrada  
│   └── input.csv          # Arquivo monitorado
├── 📂 csv-monitor/        # Monitor Kafka (opcional)
├── 🐳 docker-compose.yml  # Infraestrutura
├── 📖 DOCUMENTATION.md    # Documentação completa
└── 🚀 QUICK_START.md      # Guia rápido
```

## 🔧 Configuração

### Formato do CSV
```csv
id,nome,idade,cidade,valor
1,João,25,São Paulo,100.50
2,Maria,30,Rio de Janeiro,200.75
```

### Serviços (Modo Completo)
- **Streamlit**: http://localhost:8501
- **Kafka**: localhost:9092  
- **Flink**: http://localhost:8081
- **Zookeeper**: localhost:2181

## 🛠️ Tecnologias

- **Python 3.12+**: Linguagem principal
- **UV**: Gerenciador de dependências e ambiente virtual
- **Streamlit**: Framework web para dashboards
- **Plotly**: Gráficos interativos
- **Pandas**: Manipulação de dados
- **Apache Kafka**: Message broker (opcional)
- **Docker**: Containerização

## 📖 Documentação

- 📖 **[Documentação Completa](DOCUMENTATION.md)**: Guia detalhado
- 🚀 **[Quick Start](QUICK_START.md)**: Início em 5 minutos
- 🐛 **[Troubleshooting](DOCUMENTATION.md#-troubleshooting)**: Soluções para problemas

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

![Dashboard Preview](https://via.placeholder.com/800x400/1f77b4/ffffff?text=Dashboard+Real-Time+CSV)

**🚀 Sistema completo funcionando com visualizações em tempo real!**
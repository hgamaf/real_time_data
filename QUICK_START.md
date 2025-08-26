# 🚀 Quick Start Guide - Real-Time Data System

## ⚡ Início Rápido (5 minutos)

### 1. Pré-requisitos
```bash
# Verificar se tem Python 3.12+ e Docker
python --version
docker --version
```

### 2. Instalar Dependências
```bash
cd real_time_data
pip install -e .
```

### 3. Iniciar Dashboard
```bash
cd streamlit
streamlit run dashboard.py
```

### 4. Abrir no Navegador
```
http://localhost:8501
```

### 5. Testar Adicionando Dados
```bash
# Em outro terminal
echo "8,Roberto,45,Fortaleza,275.50" >> data/input.csv
```

## 🎯 Resultado Esperado

✅ Dashboard abre no navegador  
✅ Mostra dados existentes do CSV  
✅ Atualiza automaticamente a cada 3 segundos  
✅ Novos dados aparecem quando você adiciona no CSV  

## 📊 Funcionalidades Principais

- **💰 Métricas**: Valor total, médio, registros, idade média
- **📈 Gráficos**: Barras, histograma, pizza, scatter
- **📋 Tabelas**: Dados completos e estatísticas por cidade
- **🔄 Auto-refresh**: Atualização automática em tempo real

## 🛠️ Comandos Úteis

```bash
# Parar Streamlit
Ctrl+C

# Reiniciar Dashboard
streamlit run dashboard.py

# Adicionar dados de teste
echo "9,Ana,32,Recife,180.25" >> data/input.csv
echo "10,Carlos,28,Curitiba,320.75" >> data/input.csv
```

## 🎉 Pronto!

Seu sistema de dados em tempo real está funcionando! 

Para funcionalidades avançadas (Kafka, Flink), consulte a [documentação completa](DOCUMENTATION.md).
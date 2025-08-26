import pytest
import pandas as pd
import json
from unittest.mock import Mock, patch
import sys
import os

# Mock do streamlit antes de importar
sys.modules['streamlit'] = Mock()
sys.modules['plotly.express'] = Mock()

# Adicionar o diretório streamlit ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit'))

from dashboard import load_kafka_data, update_data


def test_load_kafka_data_with_valid_messages():
    """Testa carregamento de dados válidos do Kafka"""
    # Mock do consumer
    mock_consumer = Mock()
    
    # Mock de mensagem válida
    mock_message = Mock()
    mock_message.error.return_value = None
    mock_message.value.return_value = b'{"id": 1, "nome": "Joao", "idade": 25, "cidade": "Sao Paulo", "valor": 100.50}'
    
    # Configurar retorno do poll: primeira chamada retorna mensagem, segunda retorna None
    mock_consumer.poll.side_effect = [mock_message, None]
    
    with patch('dashboard.get_kafka_consumer', return_value=mock_consumer):
        df = load_kafka_data()
        
        assert not df.empty
        assert len(df) == 1
        assert df.iloc[0]['nome'] == 'Joao'
        assert df.iloc[0]['valor'] == 100.50
        assert 'timestamp_load' in df.columns


def test_data_deduplication():
    """Testa remoção de duplicatas por ID"""
    # Dados com IDs duplicados
    df = pd.DataFrame({
        'id': [1, 2, 1, 3],
        'nome': ['Joao', 'Maria', 'Joao Updated', 'Pedro'],
        'valor': [100, 200, 150, 300]
    })
    
    # Remover duplicatas mantendo o último registro
    df_unique = df.drop_duplicates(subset=['id'], keep='last')
    
    assert len(df_unique) == 3  # Deve ter apenas 3 registros únicos
    
    # Verificar se manteve o registro mais recente do ID 1
    joao_record = df_unique[df_unique['id'] == 1].iloc[0]
    assert joao_record['nome'] == 'Joao Updated'
    assert joao_record['valor'] == 150


def test_metrics_calculation():
    """Testa cálculo de métricas básicas"""
    sample_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'nome': ['Joao', 'Maria', 'Pedro', 'Ana', 'Carlos'],
        'idade': [25, 30, 35, 28, 42],
        'cidade': ['Sao Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasilia'],
        'valor': [100.50, 250.75, 180.25, 320.00, 95.80]
    })
    
    # Calcular métricas
    total_valor = sample_data['valor'].sum()
    valor_medio = sample_data['valor'].mean()
    total_registros = len(sample_data)
    idade_media = sample_data['idade'].mean()
    
    # Verificar resultados
    assert total_valor == 947.30
    assert valor_medio == 189.46
    assert total_registros == 5
    assert idade_media == 32.0
    
    # Testar agregação por cidade
    city_stats = sample_data.groupby('cidade')['valor'].sum()
    assert len(city_stats) == 5  # 5 cidades diferentes
    assert city_stats['Sao Paulo'] == 100.50
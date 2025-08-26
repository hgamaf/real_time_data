import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, patch
import sys

# Adicionar o diretório csv-monitor ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from csv_monitor.csv_producer import CSVMonitor


def test_csv_monitor_initialization():
    """Testa se o CSVMonitor inicializa corretamente com arquivo válido"""
    # Criar arquivo CSV temporário
    sample_data = pd.DataFrame({
        'id': [1, 2, 3],
        'nome': ['João', 'Maria', 'Pedro'],
        'idade': [25, 30, 35],
        'cidade': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte'],
        'valor': [100.50, 250.75, 180.25]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_data.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        # Mock do Kafka Producer
        with patch('csv_monitor.csv_producer.Producer') as mock_producer:
            mock_producer.return_value = Mock()
            
            # Testar inicialização
            monitor = CSVMonitor(temp_file, 'test-topic')
            
            assert monitor.csv_file == temp_file
            assert monitor.kafka_topic == 'test-topic'
            assert monitor.last_modified == 0
            assert len(monitor.processed_rows) == 0
            
    finally:
        os.unlink(temp_file)


def test_csv_reading():
    """Testa se o CSV é lido corretamente"""
    sample_data = pd.DataFrame({
        'id': [1, 2],
        'nome': ['Ana', 'Carlos'],
        'idade': [28, 42],
        'cidade': ['Salvador', 'Brasília'],
        'valor': [320.00, 95.80]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_data.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        with patch('csv_monitor.csv_producer.Producer') as mock_producer:
            mock_producer.return_value = Mock()
            
            monitor = CSVMonitor(temp_file, 'test-topic')
            df = monitor.read_csv()
            
            assert not df.empty
            assert len(df) == 2
            assert list(df.columns) == ['id', 'nome', 'idade', 'cidade', 'valor']
            assert df.iloc[0]['nome'] == 'Ana'
            assert df.iloc[1]['nome'] == 'Carlos'
            
    finally:
        os.unlink(temp_file)


def test_kafka_message_sending():
    """Testa se as mensagens são enviadas corretamente para o Kafka"""
    sample_data = pd.DataFrame({
        'id': [1],
        'nome': ['Teste'],
        'idade': [30],
        'cidade': ['Teste City'],
        'valor': [150.00]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_data.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        # Mock do Kafka Producer
        mock_producer = Mock()
        
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_producer):
            monitor = CSVMonitor(temp_file, 'test-topic')
            monitor.send_all_data()
            
            # Verificar se produce foi chamado
            assert mock_producer.produce.called
            assert mock_producer.flush.called
            
            # Verificar argumentos da chamada
            call_args = mock_producer.produce.call_args
            assert call_args[0][0] == 'test-topic'  # Tópico correto
            
    finally:
        os.unlink(temp_file)
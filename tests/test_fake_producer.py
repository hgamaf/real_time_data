import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Adicionar o diretório csv-monitor ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'csv-monitor'))

from fake_data_producer import FakeDataProducer


def test_fake_data_producer_initialization():
    """Testa se o FakeDataProducer inicializa corretamente"""
    with patch('fake_data_producer.KafkaProducer') as mock_producer:
        mock_instance = Mock()
        mock_producer.return_value = mock_instance
        
        # Testar inicialização
        producer = FakeDataProducer('test-topic')
        
        assert producer.kafka_topic == 'test-topic'
        assert producer.fake is not None
        assert len(producer.cidades) > 0
        assert 'São Paulo' in producer.cidades
        assert 'Rio de Janeiro' in producer.cidades


def test_fake_data_generation():
    """Testa se os dados fake são gerados no formato correto"""
    with patch('fake_data_producer.KafkaProducer') as mock_producer:
        mock_instance = Mock()
        mock_producer.return_value = mock_instance
        
        producer = FakeDataProducer('test-topic')
        fake_data = producer.generate_fake_data()
        
        # Verificar estrutura dos dados
        required_fields = ['id', 'nome', 'idade', 'cidade', 'valor', 'timestamp']
        for field in required_fields:
            assert field in fake_data
        
        # Verificar tipos de dados
        assert isinstance(fake_data['id'], int)
        assert isinstance(fake_data['nome'], str)
        assert isinstance(fake_data['idade'], int)
        assert isinstance(fake_data['cidade'], str)
        assert isinstance(fake_data['valor'], float)
        assert isinstance(fake_data['timestamp'], str)
        
        # Verificar ranges
        assert 1000 <= fake_data['id'] <= 9999
        assert 18 <= fake_data['idade'] <= 80
        assert 50.0 <= fake_data['valor'] <= 2000.0
        assert fake_data['cidade'] in producer.cidades


def test_kafka_message_sending():
    """Testa se as mensagens são enviadas corretamente para o Kafka"""
    mock_producer = Mock()
    mock_future = Mock()
    mock_future.get.return_value = None
    mock_producer.send.return_value = mock_future
    
    with patch('fake_data_producer.KafkaProducer', return_value=mock_producer):
        producer = FakeDataProducer('test-topic')
        
        # Dados de teste
        test_data = {
            'id': 1234,
            'nome': 'João Silva',
            'idade': 30,
            'cidade': 'São Paulo',
            'valor': 150.50,
            'timestamp': '2024-01-01T10:00:00'
        }
        
        # Testar envio
        result = producer.send_data(test_data)
        
        assert result is True
        assert mock_producer.send.called
        
        # Verificar argumentos da chamada
        call_args = mock_producer.send.call_args
        assert call_args[0][0] == 'test-topic'  # Tópico correto
        assert call_args[1]['key'] == test_data['id']  # Key correto
        assert call_args[1]['value'] == test_data  # Value correto


def test_kafka_connection_error_handling():
    """Testa tratamento de erros de conexão com Kafka"""
    # Simular erro de conexão
    with patch('fake_data_producer.KafkaProducer', side_effect=Exception("Connection failed")):
        with pytest.raises(Exception) as exc_info:
            FakeDataProducer('test-topic')
        
        assert "Connection failed" in str(exc_info.value)


def test_send_data_error_handling():
    """Testa tratamento de erros no envio de dados"""
    mock_producer = Mock()
    mock_future = Mock()
    mock_future.get.side_effect = Exception("Send failed")
    mock_producer.send.return_value = mock_future
    
    with patch('fake_data_producer.KafkaProducer', return_value=mock_producer):
        producer = FakeDataProducer('test-topic')
        
        test_data = {
            'id': 1234,
            'nome': 'João Silva',
            'idade': 30,
            'cidade': 'São Paulo',
            'valor': 150.50,
            'timestamp': '2024-01-01T10:00:00'
        }
        
        # Testar envio com erro
        result = producer.send_data(test_data)
        
        assert result is False


def test_data_consistency():
    """Testa consistência dos dados gerados"""
    with patch('fake_data_producer.KafkaProducer') as mock_producer:
        mock_instance = Mock()
        mock_producer.return_value = mock_instance
        
        producer = FakeDataProducer('test-topic')
        
        # Gerar múltiplos dados e verificar consistência
        for _ in range(10):
            fake_data = producer.generate_fake_data()
            
            # Verificar se todos os campos obrigatórios estão presentes
            assert all(field in fake_data for field in ['id', 'nome', 'idade', 'cidade', 'valor', 'timestamp'])
            
            # Verificar se os valores estão nos ranges esperados
            assert len(fake_data['nome']) > 0
            assert fake_data['cidade'] in producer.cidades
            assert fake_data['valor'] > 0
            
            # Verificar formato do timestamp (ISO format)
            assert 'T' in fake_data['timestamp']
            assert len(fake_data['timestamp']) > 10


def test_brazilian_data_generation():
    """Testa se os dados gerados são brasileiros"""
    with patch('fake_data_producer.KafkaProducer') as mock_producer:
        mock_instance = Mock()
        mock_producer.return_value = mock_instance
        
        producer = FakeDataProducer('test-topic')
        
        # Verificar se as cidades são brasileiras
        brazilian_cities = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador',
            'Fortaleza', 'Brasília', 'Curitiba', 'Recife'
        ]
        
        for city in brazilian_cities:
            assert city in producer.cidades
        
        # Gerar dados e verificar se usa cidades brasileiras
        fake_data = producer.generate_fake_data()
        assert fake_data['cidade'] in producer.cidades
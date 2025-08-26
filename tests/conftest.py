import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, MagicMock
from confluent_kafka import Producer, Consumer


@pytest.fixture
def sample_csv_data():
    """Fixture com dados de exemplo para testes"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'nome': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos'],
        'idade': [25, 30, 35, 28, 42],
        'cidade': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília'],
        'valor': [100.50, 250.75, 180.25, 320.00, 95.80]
    })


@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Fixture que cria um arquivo CSV temporário para testes"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_csv_data.to_csv(f.name, index=False)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_kafka_producer():
    """Mock do Kafka Producer"""
    producer = Mock(spec=Producer)
    producer.produce = Mock()
    producer.flush = Mock()
    producer.close = Mock()
    return producer


@pytest.fixture
def mock_kafka_consumer():
    """Mock do Kafka Consumer"""
    consumer = Mock(spec=Consumer)
    consumer.subscribe = Mock()
    consumer.poll = Mock()
    consumer.close = Mock()
    return consumer


@pytest.fixture
def kafka_message_mock():
    """Mock de uma mensagem Kafka"""
    message = Mock()
    message.error.return_value = None
    message.value.return_value = b'{"id": 1, "nome": "João", "idade": 25, "cidade": "São Paulo", "valor": 100.50}'
    message.key.return_value = b'1'
    return message


@pytest.fixture
def kafka_config():
    """Configuração padrão do Kafka para testes"""
    return {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'test-client',
        'group.id': 'test-group'
    }


@pytest.fixture
def empty_csv_file():
    """Fixture que cria um arquivo CSV vazio"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('id,nome,idade,cidade,valor\n')
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def invalid_csv_file():
    """Fixture que cria um arquivo CSV com dados inválidos"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('id,nome,idade,cidade,valor\n')
        f.write('1,João,invalid_age,São Paulo,100.50\n')
        yield f.name
    os.unlink(f.name)
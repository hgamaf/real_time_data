from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common import Time
from pyflink.datastream.functions import MapFunction, RuntimeContext
import json

class ParseJsonFunction(MapFunction):
    def map(self, value):
        return json.loads(value)

class ProcessDataFunction(MapFunction):
    def map(self, value):
        # Exemplo de processamento: adicionar campo processado e calcular imposto
        value['processado'] = True
        if 'valor' in value:
            value['imposto'] = float(value['valor']) * 0.1  # 10% de imposto
        return value

class StringifyJsonFunction(MapFunction):
    def map(self, value):
        return json.dumps(value)

def process_stream():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Adicionar connector Kafka ao classpath
    env.add_jars("file:///opt/flink/lib/flink-sql-connector-kafka-1.17.2.jar")
    
    # Consumir do Kafka
    kafka_consumer = FlinkKafkaConsumer(
        'csv-data',
        SimpleStringSchema(),
        {'bootstrap.servers': 'localhost:9092', 'group.id': 'flink-group'}
    ).set_start_from_earliest()
    
    # Produzir para o Kafka processado
    kafka_producer = FlinkKafkaProducer(
        'csv-data-processed',
        SimpleStringSchema(),
        {'bootstrap.servers': 'localhost:9092'}
    )
    
    # Pipeline de processamento
    stream = env.add_source(kafka_consumer)
    
    processed_stream = stream \
        .map(ParseJsonFunction()) \
        .map(ProcessDataFunction()) \
        .map(StringifyJsonFunction())
    
    # Enviar dados processados de volta para Kafka
    processed_stream.add_sink(kafka_producer)
    
    # Executar o job
    env.execute("CSV Data Processing")

if __name__ == '__main__':
    process_stream()
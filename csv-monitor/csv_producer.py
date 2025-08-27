import pandas as pd
from kafka import KafkaProducer
import json
import time
import os
from datetime import datetime

class CSVMonitor:
    def __init__(self, csv_file, kafka_topic, bootstrap_servers='localhost:9092'):
        self.csv_file = csv_file
        self.kafka_topic = kafka_topic
        
        # Verificar se arquivo CSV existe
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_file}")
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[bootstrap_servers],
                client_id='csv-producer',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                request_timeout_ms=10000,
                retries=3
            )
            print(f"Conectado ao Kafka em {bootstrap_servers}")
        except Exception as e:
            print(f"Erro ao conectar com Kafka: {e}")
            print("Certifique-se de que o Kafka está rodando em localhost:9092")
            raise
            
        self.last_modified = 0
        self.processed_rows = set()
        
    def read_csv(self):
        """Lê o arquivo CSV e retorna os dados"""
        try:
            df = pd.read_csv(self.csv_file)
            return df
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
            return pd.DataFrame()
    
    def get_row_hash(self, row):
        """Gera um hash único para uma linha"""
        return hash(tuple(row))
    
    def send_all_data(self):
        """Envia todos os dados do CSV para o Kafka"""
        print("Enviando todos os dados do CSV...")
        
        df = self.read_csv()
        if df.empty:
            return
        
        for _, row in df.iterrows():
            # Converter a linha para dicionário
            row_data = row.to_dict()
            row_data['timestamp'] = datetime.now().isoformat()
            
            # Enviar para o Kafka
            future = self.producer.send(
                self.kafka_topic,
                key=row_data['id'],
                value=row_data
            )
            # Aguardar confirmação
            future.get(timeout=10)
            print(f"Enviado: {row_data}")

    def send_new_data(self):
        """Verifica por novas linhas e envia para o Kafka"""
        current_modified = os.path.getmtime(self.csv_file)
        
        if current_modified > self.last_modified:
            print("Arquivo modificado. Enviando snapshot completo...")
            self.last_modified = current_modified
            
            # Primeiro, enviar mensagem de reset para limpar dados antigos
            reset_message = {
                'action': 'reset',
                'timestamp': datetime.now().isoformat()
            }
            future = self.producer.send(
                self.kafka_topic,
                key='__reset__',
                value=reset_message
            )
            future.get(timeout=10)
            print("Enviado comando de reset")
            
            # Limpar dados processados para reenviar tudo
            self.processed_rows.clear()
            
            df = self.read_csv()
            if df.empty:
                print("CSV vazio - todos os dados foram removidos")
                return
            
            # Enviar todos os dados atuais do CSV
            for _, row in df.iterrows():
                row_hash = self.get_row_hash(row)
                
                # Converter a linha para dicionário
                row_data = row.to_dict()
                row_data['timestamp'] = datetime.now().isoformat()
                row_data['action'] = 'upsert'  # Indicar que é inserção/atualização
                
                # Enviar para o Kafka
                future = self.producer.send(
                    self.kafka_topic,
                    key=row_data['id'],
                    value=row_data
                )
                future.get(timeout=10)
                print(f"Enviado: {row_data}")
                
                self.processed_rows.add(row_hash)
    
    def run(self, interval=5):
        """Executa o monitor continuamente"""
        print(f"Monitorando {self.csv_file} a cada {interval} segundos...")
        
        # Processar dados existentes na primeira execução
        self.send_new_data()
        
        try:
            while True:
                time.sleep(interval)
                self.send_new_data()
        except KeyboardInterrupt:
            print("Interrompendo monitor...")
        finally:
            self.producer.close()

if __name__ == "__main__":
    # Configurações - usar caminho absoluto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    CSV_FILE = os.path.join(script_dir, "../data/input.csv")
    KAFKA_TOPIC = "csv-data"
    
    print(f"Monitorando arquivo: {os.path.abspath(CSV_FILE)}")
    
    # Criar monitor e executar
    monitor = CSVMonitor(CSV_FILE, KAFKA_TOPIC)
    monitor.run(interval=3)
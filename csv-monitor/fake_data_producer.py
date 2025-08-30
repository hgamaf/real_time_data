import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

class FakeDataProducer:
    def __init__(self, kafka_topic, bootstrap_servers='localhost:9092'):
        self.kafka_topic = kafka_topic
        self.fake = Faker('pt_BR')  # Usar dados brasileiros
        
        # Cidades brasileiras para mais realismo
        self.cidades = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 
            'Fortaleza', 'Brasília', 'Curitiba', 'Recife', 'Porto Alegre',
            'Manaus', 'Belém', 'Goiânia', 'Campinas', 'São Luís', 'Maceió',
            'Natal', 'João Pessoa', 'Teresina', 'Campo Grande', 'Cuiabá',
            'Florianópolis', 'Vitória', 'Aracaju', 'Palmas', 'Boa Vista'
        ]
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[bootstrap_servers],
                client_id='fake-data-producer',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                request_timeout_ms=10000,
                retries=3
            )
            print(f"🚀 Conectado ao Kafka em {bootstrap_servers}")
            print(f"📡 Enviando dados para o tópico: {kafka_topic}")
        except Exception as e:
            print(f"❌ Erro ao conectar com Kafka: {e}")
            print("🔧 Certifique-se de que o Kafka está rodando em localhost:9092")
            raise
    
    def generate_fake_data(self):
        """Gera dados fake no formato: id, nome, idade, cidade, valor"""
        return {
            'id': random.randint(1000, 9999),
            'nome': self.fake.name(),
            'idade': random.randint(18, 80),
            'cidade': random.choice(self.cidades),
            'valor': round(random.uniform(50.0, 2000.0), 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def send_data(self, data):
        """Envia dados para o Kafka"""
        try:
            future = self.producer.send(
                self.kafka_topic,
                key=data['id'],
                value=data
            )
            future.get(timeout=10)
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar dados: {e}")
            return False
    
    def run(self, interval=5):
        """Executa gerador continuamente"""
        print(f"🎯 Gerando dados fake a cada {interval} segundos...")
        print("📊 Schema: id, nome, idade, cidade, valor")
        print("🔄 Pressione Ctrl+C para parar")
        print("=" * 50)
        
        try:
            counter = 0
            while True:
                # Gerar dados fake
                fake_data = self.generate_fake_data()
                
                # Enviar para Kafka
                if self.send_data(fake_data):
                    counter += 1
                    print(f"✅ [{counter:3d}] ID: {fake_data['id']} | "
                          f"{fake_data['nome']:<20} | "
                          f"{fake_data['idade']:2d} anos | "
                          f"{fake_data['cidade']:<15} | "
                          f"R$ {fake_data['valor']:7.2f}")
                else:
                    print(f"❌ [{counter:3d}] Falha ao enviar dados")
                
                # Aguardar próximo envio
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompendo gerador...")
        finally:
            self.producer.close()
            print("✅ Producer fechado")

def main():
    """Função principal"""
    KAFKA_TOPIC = "csv-data"
    
    print("🎯 Gerador de Dados Fake - Dashboard Compatível")
    print("=" * 50)
    print("📊 Formato: id, nome, idade, cidade, valor")
    print("🎯 Tópico Kafka: csv-data")
    print("📱 Compatível com o dashboard existente")
    print("=" * 50)
    
    try:
        # Perguntar intervalo
        try:
            interval_input = input("⏱️  Intervalo entre dados (segundos) [5]: ").strip()
            interval = int(interval_input) if interval_input else 5
            if interval < 1:
                interval = 5
        except ValueError:
            interval = 5
        
        print(f"⚡ Configurado para gerar dados a cada {interval} segundos")
        print()
        
        # Criar e executar producer
        producer = FakeDataProducer(KAFKA_TOPIC)
        producer.run(interval)
            
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
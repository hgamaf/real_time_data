#!/usr/bin/env python3
"""
Script para executar o gerador de dados fake
Uso: python run_fake_producer.py [intervalo]
"""

import sys
import os

# Adicionar o diretório csv-monitor ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'csv-monitor'))

from fake_data_producer import FakeDataProducer

def main():
    KAFKA_TOPIC = "csv-data"
    
    # Argumento da linha de comando
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    print("🎯 Gerador de Dados Fake - Dashboard Compatível")
    print("=" * 50)
    print("📊 Formato: id, nome, idade, cidade, valor")
    print(f"⏱️  Intervalo: {interval} segundos")
    print("🎯 Tópico: csv-data")
    print("=" * 50)
    
    try:
        producer = FakeDataProducer(KAFKA_TOPIC)
        producer.run(interval)
            
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
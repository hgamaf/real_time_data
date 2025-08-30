#!/usr/bin/env python3
"""
Script para executar o gerador de dados fake
Uso: python run_fake_producer.py [tipo] [intervalo]

Tipos disponíveis:
- person: Gera dados de pessoas
- transaction: Gera dados de transações
- sales: Gera dados de vendas
"""

import sys
import os

# Adicionar o diretório csv-monitor ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'csv-monitor'))

from fake_data_producer import FakeDataProducer

def main():
    KAFKA_TOPIC = "csv-data"
    
    # Argumentos da linha de comando
    data_type = sys.argv[1] if len(sys.argv) > 1 else None
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    if data_type not in ['person', 'transaction', 'sales']:
        print("🎯 Gerador de Dados Fake - Uso Rápido")
        print("=" * 40)
        print("Uso: python run_fake_producer.py [tipo] [intervalo]")
        print()
        print("Tipos disponíveis:")
        print("  person      - 👥 Pessoas (nome, idade, cidade, valor)")
        print("  transaction - 💰 Transações (com email, telefone)")
        print("  sales       - 🛒 Vendas (com produto, quantidade)")
        print()
        print("Exemplos:")
        print("  python run_fake_producer.py person 3")
        print("  python run_fake_producer.py transaction 10")
        print("  python run_fake_producer.py sales 5")
        print()
        print("Ou execute sem argumentos para menu interativo:")
        print("  python csv-monitor/fake_data_producer.py")
        return
    
    try:
        producer = FakeDataProducer(KAFKA_TOPIC)
        
        if data_type == 'person':
            producer.run_person_generator(interval)
        elif data_type == 'transaction':
            producer.run_transaction_generator(interval)
        elif data_type == 'sales':
            producer.run_sales_generator(interval)
            
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
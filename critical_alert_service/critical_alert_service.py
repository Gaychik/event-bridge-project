# critical_alert_service.py
import pika
import json
import os
import sys
from typing import Dict, Any

# Конфигурация из переменных окружения с значениями по умолчанию
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
QUEUE_NAME = 'critical_alert_queue'
EXCHANGE_NAME = 'event_topic_exchange'
ROUTING_KEY = 'event.registered.vip'


def get_rabbitmq_connection():

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)


def print_vip_alert(event_data: Dict[str, Any]):

    # Извлекаем данные из события
    user_name = event_data.get('user_name', 'Unknown')
    user_email = event_data.get('user_email', 'unknown@example.com')
    event_name = event_data.get('event_name', 'Unknown Event')
    
    # Формируем строки сообщения согласно ТЗ
    lines = [
        "!!! NEW VIP REGISTRATION !!!",
        f"User: {user_email}",
        f"Event: {event_name}"
    ]
    
    # Находим максимальную длину строки
    max_length = max(len(line) for line in lines) + 4
    
    # Печатаем верхнюю границу
    print("\n" + "*" * max_length)
    
    # Печатаем каждую строку
    for line in lines:
        padding = max_length - len(line) - 2
        print(f"* {line}{' ' * padding}*")
    
    # Печатаем нижнюю границу
    print("*" * max_length + "\n")


def callback(ch, method, properties, body):

    try:
        # Декодируем и парсим JSON
        event_data = json.loads(body.decode('utf-8'))
        
        # Проверяем, что это VIP-событие
        if event_data.get('is_vip'):
            print_vip_alert(event_data)
            
            # Подтверждаем успешную обработку сообщения
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[✓] Обработано VIP-событие: {event_data.get('user_email')}")
        else:
            # Это не VIP - такого не должно быть, но на всякий случай
            print(f"[!] Получено non-VIP событие в critical_alert_queue")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
    except json.JSONDecodeError as e:
        print(f"[ERROR] Ошибка парсинга JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"[ERROR] Ошибка обработки: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def setup_queue(channel):

    # Объявляем exchange (существующий - pika пропустит)
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type='topic',
        durable=True
    )
    
    # Объявляем очередь
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
        exclusive=False,
        auto_delete=False
    )
    
    # Привязываем очередь к exchange с routing key для VIP
    channel.queue_bind(
        queue=QUEUE_NAME,
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY
    )
    
    print(f"[✓] Очередь '{QUEUE_NAME}' привязана к exchange '{EXCHANGE_NAME}'")
    print(f"[✓] Слушаем VIP-события с routing key: {ROUTING_KEY}")


def main():

    print("=" * 50)
    print("VIP Консьерж Сервис (Critical Alert Service)")
    print("=" * 50)
    print(f"Подключение к RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    print(f"Ожидание VIP-регистраций...")
    print("Нажмите CTRL+C для выхода")
    print("-" * 50)
    
    while True:
        try:
            # Устанавливаем соединение
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            # Настраиваем очередь
            setup_queue(channel)
            
            # Устанавливаем QoS (prefetch count = 1)
            channel.basic_qos(prefetch_count=1)
            
            # Начинаем потребление
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=callback,
                auto_ack=False
            )
            
            # Запускаем цикл обработки
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[!] Ошибка подключения: {e}")
            print("[!] Повтор через 5 секунд...")
            import time
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n[✓] Завершение работы...")
            try:
                connection.close()
            except:
                pass
            sys.exit(0)
        except Exception as e:
            print(f"[!] Ошибка: {e}")
            print("[!] Перезапуск через 5 секунд...")
            import time
            time.sleep(5)


if __name__ == '__main__':
    main()
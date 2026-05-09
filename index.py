#!/usr/bin/env python3
import pika
import json
import sys
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
import uuid
import pdfgen
import random
import pdf_server


pdf_server.run_server()

class RegistrationEvent(BaseModel):
    registration_id: str = str(uuid.uuid4())
    event_name: str
    user_email: EmailStr
    user_name: str
    is_vip: bool = False
    registration_time: str = datetime.now(timezone.utc).isoformat()

def callback(ch, method, properties, body):
    """Обработчик полученных сообщений"""
    try:
        # Декодируем и парсим JSON
        event_data = json.loads(body.decode('utf-8'))
        
        # Преобразуем в объект RegistrationEvent для удобства
        event = RegistrationEvent(**event_data)
        
        print(f"\n{'='*60}")
        print(f"📨 Получено событие:")
        print(f"   Routing Key: {method.routing_key}")
        print(f"   Exchange: {method.exchange}")
        print(f"{'='*60}")
        print(f"👤 Пользователь: {event.user_name}")
        print(f"📧 Email: {event.user_email}")
        print(f"🎯 Событие: {event.event_name}")
        print(f"👑 VIP статус: {'Да' if event.is_vip else 'Нет'}")
        
        if not event.is_vip:
            pdfgen.gen_File(event.user_name, event.user_email, event.event_name, event.registration_time, vip=False, seat=random.randint(1, 100))
        else:
            pdfgen.gen_File(event.user_name, event.user_email, event.event_name, event.registration_time, vip=True, seat="VIP Lounge")

        print(f"{'='*60}\n")
        
        # Подтверждаем обработку сообщения (acknowledge)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        # Отклоняем сообщение без повторной отправки
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"❌ Ошибка обработки события: {e}")
        # Возвращаем сообщение в очередь для повторной обработки
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    try:
        # Подключаемся к RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        channel = connection.channel()
        
        # Объявляем exchange (должен совпадать с издателем)
        channel.exchange_declare(
            exchange='event_topic_exchange',
            exchange_type='topic',
            durable=True
        )
        
        # Создаем временную очередь с уникальным именем
        # exclusive=True - очередь удалится при отключении
        # auto_delete=True - очередь удалится, когда отключатся все потребители
        result = channel.queue_declare(
            queue='',  # Пустая строка = генерируем уникальное имя
            exclusive=True,
            auto_delete=True
        )
        queue_name = result.method.queue
        
        # Привязываем очередь к exchange с нужными routing keys
        # Можно привязаться к нескольким ключам или использовать wildcard
        routing_keys = [
            'event.registered.vip',      # Только VIP регистрации
            'event.registered.regular',  # Только обычные регистрации
            # 'event.registered.*',      # Все регистрации (wildcard)
            # 'event.#',                 # Все события (включая вложенные)
        ]
        
        for routing_key in routing_keys:
            channel.queue_bind(
                exchange='event_topic_exchange',
                queue=queue_name,
                routing_key=routing_key
            )
            print(f"🔗 Привязаны к routing_key: {routing_key}")
        
        print(f"\n🎧 Ожидание сообщений в очереди: {queue_name}")
        print("📋 Нажмите CTRL+C для выхода\n")
        
        # Настраиваем обработчик сообщений
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False  # Ручное подтверждение для надежности
        )
        
        # Запускаем цикл обработки
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\n\n👋 Программа остановлена пользователем")
        sys.exit(0)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ Не удалось подключиться к RabbitMQ: {e}")
        print("Убедитесь, что RabbitMQ запущен: sudo systemctl start rabbitmq")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()

if __name__ == '__main__':
    main()

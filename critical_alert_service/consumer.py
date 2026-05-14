import json
import sys
import pika
from datetime import datetime
from config import Config

class VIPAlertConsumer:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.channel = None
        
    def connect_to_rabbitmq(self):

        try:
            credentials = pika.PlainCredentials(
                self.config.RABBITMQ_USER, 
                self.config.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=self.config.RABBITMQ_HOST,
                port=self.config.RABBITMQ_PORT,
                credentials=credentials
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Объявляем очередь (создаём, если её нет)
            self.channel.queue_declare(
                queue=self.config.QUEUE_NAME,
                durable=True  # Очередь сохранится при перезапуске RabbitMQ
            )
            
            print(f"✅ Connected to RabbitMQ, listening to queue: {self.config.QUEUE_NAME}")
            
        except Exception as e:
            print(f"❌ Failed to connect to RabbitMQ: {e}")
            sys.exit(1)
    
    def format_alert_message(self, vip_data):
        """Форматирование сообщения с рамкой для VIP-регистрации"""
        email = vip_data.get('email', 'unknown@example.com')
        event_name = vip_data.get('event_name', 'Unknown Event')
        timestamp = vip_data.get('timestamp', datetime.now().isoformat())
        
        # Создаем строки для рамки
        frame_char = self.config.FRAME_CHAR
        width = self.config.FRAME_WIDTH
        
        # Основное сообщение
        lines = [
            f"!!! NEW VIP REGISTRATION !!!",
            f"User: {email}",
            f"Event: {event_name}",
            f"Time: {timestamp}"
        ]
        
        # Находим максимальную длину строки
        max_len = max(len(line) for line in lines)
        
        # Создаем рамку
        top_bottom_frame = frame_char * (max_len + 4)
        
        formatted_message = []
        formatted_message.append(top_bottom_frame)
        
        for line in lines:
            padding = max_len - len(line)
            formatted_message.append(f"{frame_char} {line}{' ' * padding} {frame_char}")
        
        formatted_message.append(top_bottom_frame)
        
        return "\n".join(formatted_message)
    
    def process_vip_registration(self, ch, method, properties, body):

        try:
            # Парсим JSON сообщение
            vip_data = json.loads(body.decode('utf-8'))
            
            # Форматируем и выводим заметное сообщение
            alert_message = self.format_alert_message(vip_data)
            
            print("\n" + "!" * 80)
            print(alert_message)
            print("!" * 80 + "\n")
            
            # Подтверждаем обработку сообщения
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            # Логируем успешную обработку
            print(f"✅ VIP alert processed for: {vip_data.get('email')}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON message: {e}")
            print(f"Raw message: {body}")
            # В случае ошибки всё равно подтверждаем, чтобы не забивать очередь
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"❌ Error processing VIP registration: {e}")
            # В случае критической ошибки не подтверждаем (сообщение останется в очереди)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):

        try:
            # Настройка QoS (Quality of Service) - не более 1 неподтвержденного сообщения
            self.channel.basic_qos(prefetch_count=1)
            
            # Подписываемся на очередь
            self.channel.basic_consume(
                queue=self.config.QUEUE_NAME,
                on_message_callback=self.process_vip_registration
            )
            
            print(f"🚀 VIP Alert Service is running...")
            print(f"📡 Waiting for VIP registrations in queue: {self.config.QUEUE_NAME}")
            print("Press CTRL+C to stop")
            
            # Запускаем бесконечный цикл прослушивания
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            print("\n🛑 Service stopped by user")
            self.stop()
        except Exception as e:
            print(f"❌ Consumer error: {e}")
            self.stop()
    
    def stop(self):

        if self.connection and self.connection.is_open:
            self.connection.close()
            print("✅ Connection to RabbitMQ closed")

def main():
    consumer = VIPAlertConsumer()
    consumer.connect_to_rabbitmq()
    consumer.start_consuming()

if __name__ == "__main__":
    main()
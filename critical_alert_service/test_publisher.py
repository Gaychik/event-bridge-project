import json
import pika
from datetime import datetime
from config import Config

class TestVIPProducer:
    def __init__(self):
        self.config = Config()
        
    def send_test_vip(self):

        credentials = pika.PlainCredentials(
            self.config.RABBITMQ_USER, 
            self.config.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=self.config.RABBITMQ_HOST,
            port=self.config.RABBITMQ_PORT,
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Тестовые данные VIP-клиента
        test_vip_data = {
            "email": "vip.client@example.com",
            "event_name": "Premium Conference 2026",
            "timestamp": datetime.now().isoformat(),
            "vip_level": "platinum",
            "phone": "+7 (999) 123-45-67"
        }
        
        # Отправляем в очередь
        channel.basic_publish(
            exchange='',
            routing_key=self.config.QUEUE_NAME,
            body=json.dumps(test_vip_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Сохранять сообщение на диске
                content_type='application/json'
            )
        )
        
        print(f"✅ Test VIP message sent to {self.config.QUEUE_NAME}")
        print(f"📧 Data: {test_vip_data}")
        
        connection.close()

if __name__ == "__main__":
    producer = TestVIPProducer()
    producer.send_test_vip()
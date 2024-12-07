import pika
import numpy as np
import json
from sklearn.datasets import load_diabetes
import time
from datetime import datetime


# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    time.sleep(2)
    try:
        message_id = datetime.timestamp(datetime.now())
        # Загружаем датасет о диабете
        X, y = load_diabetes(return_X_y=True)
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0]-1)

        message_y_true = {
                'id': message_id,
                'body': y[random_row]
            }

        message_X = {
                'id': message_id,
                'body': list(X[random_row])
            }

        # Создаём подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаём очередь features
        channel.queue_declare(queue='features')

        # Публикуем сообщение в очередь y_true
        channel.basic_publish(exchange='',
                            routing_key='y_true',
                            body=json.dumps(message_y_true))
        print(f'Сообщение с правильным ответом отправлено в очередь: {message_y_true}')

        # Публикуем сообщение в очередь features
        channel.basic_publish(exchange='',
                            routing_key='features',
                            body=json.dumps(message_X))
        print(f'Сообщение с вектором признаков отправлено в очередь: {message_X}')

        # Закрываем подключение
        connection.close()
    except Exception as e:
        print(f'Не удалось подключиться к очереди : {e}')

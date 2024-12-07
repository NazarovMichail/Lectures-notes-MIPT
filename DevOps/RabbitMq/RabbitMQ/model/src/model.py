import pika
import pickle
import numpy as np
import json

# Читаем файл с сериализованной моделью
with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

try:
    # Создаём подключение по адресу rabbitmq:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Объявляем очередь features
    channel.queue_declare(queue='features')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')

    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        print(f'Получен вектор признаков {body}')
        message_X = json.loads(body)

        features = message_X['body']

        pred = regressor.predict(np.array(features).reshape(1, -1))
        message_pred = {
                'id': message_X['id'],
                'body': list(pred)
            }
        print(f"Словарь с предсказанием: {message_pred}")
        channel.basic_publish(exchange='',
                        routing_key='y_pred',
                        body=json.dumps(message_pred))
        print(f'Предсказание {message_pred} отправлено в очередь y_pred')

    # Извлекаем сообщение из очереди features
    # on_message_callback показывает, какую функцию вызвать при получении сообщения
    channel.basic_consume(
        queue='features',
        on_message_callback=callback,
        auto_ack=True
    )
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
except Exception:
    print('Не удалось подключиться к очереди')

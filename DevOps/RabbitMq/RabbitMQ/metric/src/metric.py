import pika
import json
import pandas as pd
from loguru import logger


FILE_PATH = './logs/metric_log.csv'

df = pd.DataFrame(columns=['id', 'y_true', 'y_pred', 'absolute_error'])
df.to_csv(FILE_PATH)

try:
    # Создаём подключение к серверу на локальном хосте
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Объявляем очередь y_true
    channel.queue_declare(queue='y_true')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')

    def calculate_absolute_error(row):
        return abs(row['y_true'] - row['y_pred'])

    # Создаём функцию callback для обработки данных из очереди
    def callback_y_true(ch, method, properties, body):

        global df
        # answer_string = f'Из очереди {method.routing_key} получено значение {json.loads(body)}'
        message_y_true = json.loads(body)
        logger.debug(f"Получено сообщение y_true: {message_y_true}")
        id_y = message_y_true['id']
        value = message_y_true['body']

        if id_y not in df['id'].values:
            new_row = {col: 0 for col in df.columns}
            new_row['id'] = id_y
            new_row['y_true'] = value
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            condition = (df['id'] == id_y)
            df.loc[condition, 'y_true'] = value

        condition = (df['id'] == id_y)
        row = df.loc[condition].iloc[0]
        if row['y_true'] != 0 and row['y_pred'] != 0:
            df.loc[condition, 'absolute_error'] = calculate_absolute_error(row)
            df.to_csv(FILE_PATH, mode='a', header=False, index=True)

    def callback_y_pred(ch, method, properties, body):

        global df
        message_y_pred = json.loads(body)
        logger.debug(f"Получено сообщение y_pred: {message_y_pred}")
        id_y = message_y_pred['id']
        value = message_y_pred['body']

        if id_y not in df['id'].values:
            new_row = {col: 0 for col in df.columns}
            new_row['id'] = id_y
            new_row['y_pred'] = value
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            condition = (df['id'] == id_y)
            df.loc[condition, 'y_pred'] = value

        condition = (df['id'] == id_y)
        row = df.loc[condition].iloc[0]
        if row['y_true'] != 0 and row['y_pred'] != 0:
            df.loc[condition, 'absolute_error'] = calculate_absolute_error(row)
            df.to_csv(FILE_PATH, mode='a', header=False, index=True)

    # Извлекаем сообщение из очереди y_true
    channel.basic_consume(
        queue='y_true',
        on_message_callback=callback_y_true,
        auto_ack=True
    )
    # Извлекаем сообщение из очереди y_pred
    channel.basic_consume(
        queue='y_pred',
        on_message_callback=callback_y_pred,
        auto_ack=True
    )

    # Запускаем режим ожидания прихода сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except Exception as e:
    logger.error(f"Ошибка при подключении: {e}")


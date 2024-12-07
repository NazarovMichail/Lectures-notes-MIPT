import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger


LOG_PATH = './logs/'
CSV_PATH = './logs/metric_log.csv'
plt.style.use('ggplot')
while True:
    try:
        df = pd.read_csv(CSV_PATH, index_col=0)
        plt.hist(df['absolute_error'], bins=50, edgecolor='black', )
        plt.title("Гистограмма абсолютных ошибок")
        plt.xlabel('Абсолютные ошибки')
        plt.ylabel('Количество')
        plt.savefig(f'{LOG_PATH}error_distribution.png')
        logger.info('Гистограмма обновлена ')
    except Exception as e:
        logger.error(f"Ошибка: {e}")

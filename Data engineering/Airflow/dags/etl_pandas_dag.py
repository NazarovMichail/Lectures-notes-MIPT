import pandas as pd
import time
import datetime
from tqdm import tqdm
from airflow.decorators import dag, task


default_args = {
    'owner': 'NMS'
}


@dag(default_args=default_args,
     dag_id='etl_pandas_dag',
     schedule="0 0 5 * *",
     start_date=datetime.datetime(2024, 3, 31),
     tags=['etl'])
def etl_task():
    
    date = time.strftime("%Y-%m-%d")
    
    extract_dir = '/home/nazarovmichail/airflow/extract data/'
    extract_filename = 'profit_table.csv'
    extract_filepath = extract_dir + extract_filename

    load_dir = '/home/nazarovmichail/airflow/load data/'
    load_filename = 'flags_activity.csv'
    load_filepath = load_dir + load_filename

    @task()
    def extract(extract_filepath):

        df_extracted = pd.read_csv(extract_filepath)
        return df_extracted

    @task()
    def transform(df: pd.DataFrame, date: str) -> pd.DataFrame:

        def transfrom_csv(profit_table, date):
            """ Собирает таблицу флагов активности по продуктам
        на основании прибыли и количеству совершёных транзакций
        
        :param profit_table: таблица с суммой и кол-вом транзакций
        :param date: дата расчёта флагоа активности
        
        :return df_tmp: pandas-датафрейм флагов за указанную дату
        """
            start_date = pd.to_datetime(date) - pd.DateOffset(months=2)
            end_date = pd.to_datetime(date) + pd.DateOffset(months=1)
            date_list = pd.date_range(
                start=start_date, end=end_date, freq='M'
            ).strftime('%Y-%m-01')
            
            df_tmp = (
                profit_table[profit_table['date'].isin(date_list)]
                .drop('date', axis=1)
                .groupby('id')
                .sum()
            )
            
            product_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
            for product in tqdm(product_list):
                df_tmp[f'flag_{product}'] = (
                    df_tmp.apply(
                        lambda x: x[f'sum_{product}'] != 0 and x[f'count_{product}'] != 0,
                        axis=1
                    ).astype(int)
                )
                
            df_tmp = df_tmp.filter(regex='flag').reset_index()
            
            return df_tmp
        df_tmp = transfrom_csv(df, date)
        print(df_tmp)
        return df_tmp

    @task()
    def load(df: pd.DataFrame, df_path):
        df.to_csv(df_path, index=False, mode='a')

    df_extracted = extract(extract_filepath)
    df_transformed = transform(df_extracted, date)
    load(df_transformed, load_filepath)


etl_dag = etl_task()
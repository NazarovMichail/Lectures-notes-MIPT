import pandas as pd
import os
import time
import datetime
from airflow.decorators import dag, task, task_group
from df_transform import transfrom_csv


default_args = {
    'owner': 'NMS'
}


@dag(default_args=default_args,
     dag_id='etl_pandas_parallel_dag',
     schedule="0 0 5 * *",
     start_date=datetime.datetime(2024, 3, 31),
     tags=['etl'])
def etl_task():

    date = time.strftime("%Y-%m-%d")

    extract_dir = '/home/nazarovmichail/airflow/extract data/'
    extract_filename = 'profit_table.csv'
    extract_filepath = extract_dir + extract_filename

    transform_dir = '/home/nazarovmichail/airflow/transform data/'

    load_dir = '/home/nazarovmichail/airflow/load data/'
    load_filename = 'flags_activity.csv'
    load_filepath = load_dir + load_filename

    @task()
    def extract(extract_filepath):

        df_extracted = pd.read_csv(extract_filepath)
        return df_extracted

    @task()
    def transform(df: pd.DataFrame,
                  date: str,
                  product: str,
                  transform_dir: str) -> pd.DataFrame:

        df_product = transfrom_csv(df, date, product)
        transform_filename = f'{product}_transform_df.csv'
        transform_filepath = transform_dir + transform_filename
        df_product.to_csv(transform_filepath, index=False)

        print(f'Done: {product}_transform_df.csv')

    @task()
    def load(transform_dir, load_filepath):

        df_products_list = list(os.walk(transform_dir))
        for ind, file in enumerate(sorted(df_products_list[0][2])):
            if ind == 0:
                df_load = pd.read_csv(transform_dir + file, index_col='id')
            else:
                df_product = pd.read_csv(transform_dir + file, index_col='id')
                df_product.index = df_load.index
                df_load = pd.concat((df_load, df_product), axis=1)

        df_load.to_csv(load_filepath, mode='a')

    @task_group()
    def group_transform():
        transform(df_extracted, date, 'a', transform_dir)
        transform(df_extracted, date, 'b', transform_dir)
        transform(df_extracted, date, 'c', transform_dir)
        transform(df_extracted, date, 'd', transform_dir)
        transform(df_extracted, date, 'e', transform_dir)
        transform(df_extracted, date, 'f', transform_dir)
        transform(df_extracted, date, 'g', transform_dir)
        transform(df_extracted, date, 'h', transform_dir)
        transform(df_extracted, date, 'i', transform_dir)
        transform(df_extracted, date, 'j', transform_dir)

    df_extracted = extract(extract_filepath)
    group_transform().set_downstream(load(transform_dir, load_filepath))


etl_dag = etl_task()

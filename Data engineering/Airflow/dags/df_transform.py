import pandas as pd


def transfrom_csv(profit_table, date, product):
    """ Собирает таблицу флагов активности по продукту
на основании прибыли и количеству совершёных транзакций

:param profit_table: таблица с суммой и кол-вом транзакций
:param date: дата расчёта флагов активности
:param product: название продукта

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

    df_tmp[f'flag_{product}'] = (
        df_tmp.apply(
            lambda x: x[f'sum_{product}'] != 0 and x[f'count_{product}'] != 0,
            axis=1
        ).astype(int)
    )
        
    df_tmp = df_tmp.filter(regex='flag').reset_index()
    
    return df_tmp

import luigi
import requests
from bs4 import BeautifulSoup
import re
import wget
import os
import io
import pandas as pd
import tarfile
import gzip
import shutil
import time


class Parsing(luigi.Task):

    dataset_name = luigi.Parameter('GSE68849')

    def run(self):
        site_url = 'https://www.ncbi.nlm.nih.gov'  # Url сайта
        datasets_url = '/geo/query/acc.cgi'        # Url поиска датасетов

        response = requests.get(
            site_url + datasets_url, params={'acc': self.dataset_name})        # GET-запрос к поиску конкретного датасета
        page = BeautifulSoup(response.text, 'html.parser')                     # Считывание html-информации

        attribute = 'acc=' + self.dataset_name                                 # Атрибут по которому фильтруются ссылки

        links = page.find_all(name='a', href=[re.compile(attribute)])          # Поиск списка ссылок с параметром - название датасета

        for link in links:
            search_link = re.compile(r'format=file$').search(link.get('href')) # Поиск ссылки из списка с форматом только файл
            if search_link is not None:
                result_search = link
        result_search = result_search.get('href')                              # Извлечение текста относительной ссылки
        download_link = site_url + result_search                               # Получение ссылки для скачивания датасета

        try:
            os.mkdir(self.dataset_name)
        except FileExistsError:
            print('_'*31, "\nThis directory already exists !\n", '_'*30)

        wget.download(download_link, out=f'{self.dataset_name}/')            #  Без "/" назначается новое название файла

    def output(self):                                                        #  Проверка на наличие скачанного файла
        if self.dataset_name in list(os.walk(os.getcwd()))[0][1]:            #  Создана ли папка data
            if len(list(os.walk(self.dataset_name))[0][2]) > 0:              #  Скачан ли файл
                self.filename = list(os.walk(self.dataset_name))[0][2][0]
                print('_'*37, '\n', self.filename, "Is already exists !\n", '_'*36)
                return luigi.LocalTarget(f'{self.dataset_name}\\' + self.filename)
            if len(list(os.walk(self.dataset_name))[0][1]) > 0:
                dirname = list(os.walk(self.dataset_name))[0][1][0]
                return luigi.LocalTarget(f'{self.dataset_name}\\' + dirname)


class Extracting(luigi.Task):

    dataset_name = luigi.Parameter('GSE68849')
    starting_dir = os.getcwd()

    def extract_file(self, filedir_path: str) -> int:

        """Распаковывает архив в текущей папке

    Args:
        filedir_path (str): Путь к папке с архивом

    Returns:
        int: Если архив распакован, возвращает 1, если не распакован - 0
    """

        os.chdir(filedir_path)
        extracted_flag = 0
        filenames_list = list(os.walk(filedir_path))[0][2]
        for filename in filenames_list:
            filename_short = os.path.splitext(filename)[0]
            file_extension = os.path.splitext(filename)[1]

            if file_extension in ['.tar', '.gzip', '.bz2', '.lzma']:
                with tarfile.open(filename) as tar:
                    tar.extractall()
                extracted_flag = 1
                os.remove(filename)

            if file_extension in ['.gz']:
                with gzip.open(filename, 'rb') as file_in:
                    with open(filename_short, 'wb') as file_out:
                        shutil.copyfileobj(file_in, file_out)
                extracted_flag = 1
                os.remove(filename)
        return extracted_flag

    def replace_files(self, filedir_path: str) -> None:
        """Перемещает файлы в созданные папки

    Args:
        filedir_path (str): Путь к папке с файлами для перемещения
    """
        os.chdir(filedir_path)
        filenames_list = list(os.walk(filedir_path))[0][2]
        for filename in filenames_list:
            filename_short = os.path.splitext(filename)[0]
            try:
                os.mkdir(filename_short)
            except FileExistsError:
                print('_'*31, "\nThis directory already exists !\n", '_'*30)
            os.replace(filename, filename_short + '\\' + filename)

    def run(self):

        os.chdir(self.dataset_name)
        self.filedir_path = os.getcwd()
        extracted_flag = 1
        while extracted_flag == 1:
            extracted_flag = self.extract_file(self.filedir_path)

        self.replace_files(self.filedir_path)
        os.chdir(self.starting_dir)

    def requires(self):
        return Parsing(dataset_name=self.dataset_name)

    def output(self):                                                        #  Проверка на наличие перемещенных файлов
        os.chdir(self.starting_dir)
        if self.dataset_name in list(os.walk(os.getcwd()))[0][1]:            #  Создана ли папка data
            if len(list(os.walk(self.dataset_name))[0][1]) > 0:              #  Есть ли папки в data
                dirname = list(os.walk(self.dataset_name))[0][1][0]
                if len(list(os.walk(f'{self.dataset_name}\\' + dirname))[0][2]) > 0:         #  Есть ли файлы в папке
                    filename = list(os.walk(f'{self.dataset_name}\\' + dirname))[0][2][0]
                return luigi.LocalTarget(f'{self.dataset_name}\\' + dirname + '\\' + filename )


class ToCsv(luigi.Task):

    dataset_name = luigi.Parameter('GSE68849')
    starting_dir = os.getcwd()

    def export_to_csv(self, filename: str) -> None:
        """Экспортирует txt-файл в csv-файл, разбивая на таблицы

        Args:
            filename (str): Название txt-файла
        """
        dfs = {}
        with open(filename) as f:
            write_key = None
            fio = io.StringIO()
            for l in f.readlines():
                if l.startswith('['):
                    if write_key:
                        fio.seek(0)
                        header = None if write_key == 'Heading' else 'infer'
                        dfs[write_key] = pd.read_csv(fio, sep='\t', header=header)
                    fio = io.StringIO()
                    write_key = l.strip('[]\n')
                    continue
                if write_key:
                    fio.write(l)
            fio.seek(0)
            dfs[write_key] = pd.read_csv(fio, sep='\t')
        for df_name in dfs:
            df = pd.DataFrame(dfs[df_name])
            df.to_csv(f'{df_name}.csv', index=False)

    def export_to_dir(self, filedir_path: str) -> None:
        """
        Помещает csv-файл в указанную папку
        Args:
            filedir_path (str): Путь к папке назначения
        """
        dirs_list = list(os.walk(filedir_path))[0][1]
        for dir in dirs_list:
            new_dir_path = filedir_path + '\\' + dir
            os.chdir(new_dir_path)
            filenames_list = list(os.walk(new_dir_path))[0][2]
            for filename in filenames_list:
                self.export_to_csv(filename)

    def run(self):
        os.chdir(self.dataset_name)
        filedir_path = os.getcwd()
        self.export_to_dir(filedir_path)

    def requires(self):
        return Extracting(dataset_name=self.dataset_name)

    def output(self):                                                        #  Проверка на наличие перемещенных файлов
        os.chdir(self.starting_dir)
        if self.dataset_name in list(os.walk(os.getcwd()))[0][1]:            #  Создана ли папка data
            if len(list(os.walk(self.dataset_name))[0][1]) > 0:              #  Есть ли папки в data
                dirname = list(os.walk(self.dataset_name))[0][1][0]
                if len(list(os.walk(f'{self.dataset_name}\\' + dirname))[0][2]) > 0:         #  Есть ли файлы в папке
                    filenames_list = list(os.walk(f'{self.dataset_name}\\'+ dirname))[0][2]
                    for filename in filenames_list:
                        file_extension = os.path.splitext(filename)[1]
                        if file_extension == '.csv':                        #  Есть ли файлы c расширением csv
                            filename = list(os.walk(f'{self.dataset_name}\\' + dirname))[0][2][0]
                            return luigi.LocalTarget(f'{self.dataset_name}\\' + dirname + '\\' + filename)


class TransformCsv(luigi.Task):
    starting_dir = os.getcwd()
    dataset_name = luigi.Parameter('GSE68849')
    filename = luigi.Parameter('Probes.csv')
    columns_drop = luigi.ListParameter(default=[
        'Definition', 'Ontology_Component', 'Ontology_Process',
        'Ontology_Function', 'Synonyms', 'Obsolete_Probe_Id', 'Probe_Sequence'])
    new_filename = luigi.Parameter('Probes_short.csv')

    def run(self):
        os.chdir(self.dataset_name)
        filedir_path = os.getcwd()
        dirnames_list = list(os.walk(filedir_path))[0][1]

        for dirname in dirnames_list:
            os.chdir(filedir_path + '\\' + dirname)
            df = pd.read_csv(self.filename)
            df_edited = df.drop(columns=list(self.columns_drop))
            df_edited.to_csv(self.new_filename, index=False)
            os.chdir(filedir_path)
            print(df_edited.info())

    def requires(self):
        return ToCsv(dataset_name = self.dataset_name)

    def output(self):                                                        #  Проверка на наличие перемещенных файлов
        os.chdir(self.starting_dir)
        if self.dataset_name in list(os.walk(os.getcwd()))[0][1]:            #  Создана ли папка data
            if len(list(os.walk(self.dataset_name))[0][1]) > 0:              #  Есть ли папки в data
                dirname = list(os.walk(self.dataset_name))[0][1][0]
                if len(list(os.walk(f'{self.dataset_name}\\'+ dirname))[0][2]) > 0:         #  Есть ли файлы в папке
                    filenames_list = list(os.walk(f'{self.dataset_name}\\'+ dirname))[0][2]
                    for filename in filenames_list:
                        if filename == self.new_filename:                                   #  Есть ли измененные файлы csv
                            filename = list(os.walk(f'{self.dataset_name}\\'+ dirname))[0][2][0]
                            return luigi.LocalTarget(f'{self.dataset_name}\\' + dirname + '\\' + filename)


class RemoveFile(luigi.Task):
    dataset_name = luigi.Parameter('GSE68849')
    starting_dir = os.getcwd()
    taskdone = luigi.Parameter('_Task_Remove_Done.txt')

    def run(self):
        os.chdir(self.dataset_name)
        filedir_path = os.getcwd()
        dirnames_list = list(os.walk(filedir_path))[0][1]
        for dirname in dirnames_list:
            os.chdir(filedir_path + '\\' + dirname)
            current_dir_path = os.getcwd()
            filenames_list = list(os.walk(current_dir_path))[0][2]
            for filename in filenames_list:
                file_extension = os.path.splitext(filename)[1]
                if file_extension == '.txt':
                    os.remove(filename)
                    print(f'File {filename} has been removed!')
        os.chdir(self.starting_dir)
        with open(self.dataset_name + self.taskdone, 'w') as f:
            f.write(f'The task was completed: {time.ctime()}')

    def requires(self):
        return TransformCsv(dataset_name=self.dataset_name)

    def output(self):
        return luigi.LocalTarget(self.taskdone)


if __name__ == '__main__':
    luigi.run()

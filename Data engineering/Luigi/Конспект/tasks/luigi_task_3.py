import luigi

class MyTask(luigi.Task):
    filename = "file_to_check.txt"

    def run(self):                          #  Записываем текст в файл
        with open(self.filename, 'w') as f:
            f.write("Some text")

    def output(self):                       #  Проверяем на наличие
        return luigi.LocalTarget(self.filename)

if __name__ == '__main__':
    luigi.run()

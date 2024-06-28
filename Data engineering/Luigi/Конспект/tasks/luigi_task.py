import luigi

class MyTask(luigi.Task):
    def run(self):
        print('Some txt')


if __name__ == '__main__':
    luigi.run()

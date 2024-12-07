FROM python:3.9
WORKDIR /usr/src/app
COPY ./src ./
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "metric.py" ]

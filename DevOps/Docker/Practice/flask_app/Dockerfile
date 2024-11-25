FROM tiangolo/uwsgi-nginx-flask:python3.9
COPY ./app ./
COPY ./requirements.txt ./
COPY ./uwsgi.ini ./
RUN pip install --no-cache-dir -r requirements.txt

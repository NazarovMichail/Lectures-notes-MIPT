FROM python:3.10

WORKDIR /usr/src

COPY ./src/ ./

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "plot.py"]

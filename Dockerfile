FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY grdf_exporter/ ./grdf_exporter/
COPY s7_exporter ./

CMD [ "python", "main.py" ]

FROM docker.io/python:3 AS builder
WORKDIR /usr/src
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install --user pipenv
ADD Pipfile.lock Pipfile /usr/src/
RUN /root/.local/bin/pipenv sync

FROM docker.io/python:3
WORKDIR /usr/src/app

COPY --from=builder /usr/src/.venv /usr/src/app/.venv
COPY . .

CMD [".fly/start.sh"]

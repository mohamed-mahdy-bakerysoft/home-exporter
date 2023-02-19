#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import date,timedelta,datetime

from schedule import every, repeat
from lowatt_grdf.api import API
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# https://github.com/lowatt/lowatt-grdf/pull/17
# grdf = API(os.environ.get("CLIENT_ID"), os.environ.get("CLIENT_SECRET"))
db = influxdb_client.InfluxDBClient(
   url=os.environ.get("INFLUXDB_URL"),
   token=os.environ.get("INFLUXDB_TOKEN"),
   org=os.environ.get("INFLUXDB_ORG")
)
write_api = db.write_api(write_options=SYNCHRONOUS)

def fetch():
    grdf = API(os.environ.get("CLIENT_ID"), os.environ.get("CLIENT_SECRET"))
    today = date.today() - timedelta(days=2)
    delta = timedelta(days=5)

    points = []

    for year in range(3):
        start = today.replace(year=today.year - year)
        for releve in grdf.donnees_consos_informatives(
            os.environ.get("PCE"),
            from_date=(start - delta).isoformat(),
            to_date=(start).isoformat()
        ):
            conso = releve["consommation"]
            points.append(influxdb_client.Point("grdf")
                .field("energy", conso["energie"])
                .tag("year", start.year)
                .time(datetime.fromisoformat(conso["date_fin_consommation"]).replace(year=today.year))
            )

    return points

def push(points):
    write_api.write(
        bucket=os.environ.get("INFLUXDB_BUCKET"),
        org=os.environ.get("INFLUXDB_ORG"),
        record=points
    )

@repeat(every(12).hours)
def grdf_exporter():
    push(fetch())

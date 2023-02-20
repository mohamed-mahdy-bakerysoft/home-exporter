#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

db = influxdb_client.InfluxDBClient(
   url=os.environ.get("INFLUXDB_URL"),
   token=os.environ.get("INFLUXDB_TOKEN"),
   org=os.environ.get("INFLUXDB_ORG")
)
write_api = db.write_api(write_options=SYNCHRONOUS)

def push(points):
    write_api.write(
        bucket=os.environ.get("INFLUXDB_BUCKET"),
        org=os.environ.get("INFLUXDB_ORG"),
        record=points
    )

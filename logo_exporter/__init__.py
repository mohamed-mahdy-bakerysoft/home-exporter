#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from schedule import every, repeat
import re
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import snap7
import multi_read
import ctypes
plc = multi_read.LogoMulti()

db = influxdb_client.InfluxDBClient(
   url=os.environ.get("INFLUXDB_URL"),
   token=os.environ.get("INFLUXDB_TOKEN"),
   org=os.environ.get("INFLUXDB_ORG")
)
write_api = db.write_api(write_options=SYNCHRONOUS)

def fetch():
    plc.connect(os.environ.get("PLC_IP_ADDR"), 0x0100, 0x2000)
    if plc.get_connected():
        plc.read_multi([
            "V923.0",
            "V942"
        ])
    else:
        print("Conncetion failed")

def push(points):
    write_api.write(
        bucket=os.environ.get("INFLUXDB_BUCKET"),
        org=os.environ.get("INFLUXDB_ORG"),
        record=points
    )

@repeat(every(1).second)
def logo_exporter():
    push(fetch())

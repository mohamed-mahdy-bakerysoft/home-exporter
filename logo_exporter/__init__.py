#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from schedule import every, repeat
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import logo_exporter.multi_read
plc = logo_exporter.multi_read.LogoMulti()
plc.connect(os.environ.get("PLC_IP_ADDR"), 0x0100, 0x2000)

db = influxdb_client.InfluxDBClient(
   url=os.environ.get("INFLUXDB_URL"),
   token=os.environ.get("INFLUXDB_TOKEN"),
   org=os.environ.get("INFLUXDB_ORG")
)
write_api = db.write_api(write_options=SYNCHRONOUS)

def fetch():
    if plc.get_connected():
        results = plc.read_multi([
            "V923", # I01 => I08
            "V924", # I09 => I12

            "V942", # Q01 => Q08

            "V948", # M01 => M08
            "V949", # M09 => M12

            "VW952", # AM01
            "VW954", # AM02
            "VW956", # AM03
        ])
        results["923"] = plc.byte_to_bool(results["923"], 8)
        results["924"] = plc.byte_to_bool(results["924"], 4)
        results["942"] = plc.byte_to_bool(results["942"], 8)
        results["948"] = plc.byte_to_bool(results["948"], 8)
        results["949"] = plc.byte_to_bool(results["949"], 4)

        point = (influxdb_client.Point("logo")
            .field("I01", results["923"][0])
            .field("I02", results["923"][1])
            .field("I03", results["923"][2])
            .field("I04", results["923"][3])
            .field("I05", results["923"][4])
            .field("I06", results["923"][5])
            .field("I07", results["923"][6])
            .field("I08", results["923"][7])
            .field("I09", results["924"][0])
            .field("I10", results["924"][1])
            .field("I11", results["924"][2])
            .field("I12", results["924"][3])
            .field("Q01", results["942"][0])
            .field("Q02", results["942"][1])
            .field("Q03", results["942"][2])
            .field("Q04", results["942"][3])
            .field("Q05", results["942"][4])
            .field("Q06", results["942"][5])
            .field("Q07", results["942"][6])
            .field("Q08", results["942"][7])
            .field("M01", results["948"][0])
            .field("M02", results["948"][1])
            .field("M03", results["948"][2])
            .field("M04", results["948"][3])
            .field("M05", results["948"][4])
            .field("M06", results["948"][5])
            .field("M07", results["948"][6])
            .field("M08", results["948"][7])
            .field("M09", results["948"][0])
            .field("M10", results["949"][1])
            .field("M11", results["949"][2])
            .field("M12", results["949"][3])
        )

        return point
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

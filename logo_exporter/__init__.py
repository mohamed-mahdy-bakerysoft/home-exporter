#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import atexit
from datetime import datetime

from schedule import every, repeat
from sentry_sdk import capture_exception
from influxdb_client import Point
import influxdb_exporter

import logo_exporter.multi_read
plc = logo_exporter.multi_read.LogoMulti()
last_result = {}

def on_exit(plc: logo_exporter.multi_read.LogoMulti):
    """Close clients after terminate a script.

    :param db_client: InfluxDB client
    :param write_api: WriteApi
    :return: nothing
    """
    plc.disconnect()
    plc.destroy()
atexit.register(on_exit, plc)

def fetch():
    try:
        if not plc.get_connected():
            plc.connect(os.environ.get("PLC_IP_ADDR"), 0x0100, 0x2000)

        results = plc.read_multi([
            "V923", # I01 => I08
            "V924", # I09 => I12

            "V942", # Q01 => Q08

            "V948", # M01 => M08
            "V949", # M09 => M12

            # "VW952", # AM01
            # "VW954", # AM02
            # "VW956", # AM03
        ])
        results["923"] = plc.byte_to_bool(results["923"])
        results["924"] = plc.byte_to_bool(results["924"])
        results["942"] = plc.byte_to_bool(results["942"])
        results["948"] = plc.byte_to_bool(results["948"])
        results["949"] = plc.byte_to_bool(results["949"])

        dict_results = {
            "I01": results["923"][0],
            "I02": results["923"][1],
            "I03": results["923"][2],
            "I04": results["923"][3],
            "I05": results["923"][4],
            "I06": results["923"][5],
            "I07": results["923"][6],
            "I08": results["923"][7],
            "I09": results["924"][0],
            "I10": results["924"][1],
            "I11": results["924"][2],
            "I12": results["924"][3],
            "Q01": results["942"][0],
            "Q02": results["942"][1],
            "Q03": results["942"][2],
            "Q04": results["942"][3],
            "Q05": results["942"][4],
            "Q06": results["942"][5],
            "Q07": results["942"][6],
            "Q08": results["942"][7],
            "M01": results["948"][0],
            "M02": results["948"][1],
            "M03": results["948"][2],
            "M04": results["948"][3],
            "M05": results["948"][4],
            "M06": results["948"][5],
            "M07": results["948"][6],
            "M08": results["948"][7],
            "M09": results["948"][0],
            "M10": results["949"][1],
            "M11": results["949"][2],
            "M12": results["949"][3],
        }

        global last_result
        if dict_results == last_result:
            return

        point = Point.from_dict({
            "measurement": "logo",
            "fields": dict_results,
            "time": datetime.now()
        })

        last_result = dict_results

        return point
    except Exception as e:
        capture_exception(e)

@repeat(every(1).second)
def logo_exporter():
    point = fetch()
    if point:
        influxdb_exporter.InfluxDB().push(point)

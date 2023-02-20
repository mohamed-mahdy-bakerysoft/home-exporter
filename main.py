#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from time import sleep

import sentry_sdk
from dotenv import load_dotenv
from schedule import run_pending

load_dotenv()

import grdf_exporter # noqa: E402,F401
import logo_exporter # noqa: E402,F401

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
)

while True:
    run_pending()
    sleep(1)

#!/usr/bin/env python3


"""Importing"""
from os import environ


class Config(object):
    API_ID = int(environ.get("API_ID", 0))
    API_HASH = environ.get("API_HASH", "")
    BOT_TOKEN = environ.get("BOT_TOKEN", "6206599982:AAGMtdPmgw7wRF5EsdREiJT3Qb9Yy8ALIVE")
    MONGO_STR = environ.get("MONGO_STR", "")


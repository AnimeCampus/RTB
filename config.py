#!/usr/bin/env python3


"""Importing"""
from os import environ


class Config(object):
    API_ID = int(environ.get("API_ID", 16743442))
    API_HASH = environ.get("API_HASH", "12bbd720f4097ba7713c5e40a11dfd2a")
    BOT_TOKEN = environ.get("BOT_TOKEN", "6206599982:AAGqJ84tpTzhdKYzNRMp2kPdcpN0_1zz5K4")
    MONGO_STR = environ.get("MONGO_STR", "mongodb+srv://jarvis:op@cluster0.7tisvwv.mongodb.net/?retryWrites=true&w=majority")


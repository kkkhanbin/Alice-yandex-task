import os


class Config:
    SECRET_KEY = os.urandom(24)
    JSON_AS_ASCII = False

from threading import Thread
from functools import wraps
import datetime
import smtplib

from html.parser import HTMLParser
import ipaddress

from classes.shared import db
from classes import settings
from classes import logs

def asynch(func):

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl

    return async_func

def check_existing_settings():
    settingsQuery = settings.settings.query.all()
    if settingsQuery != []:
        db.session.close()
        return True
    else:
        db.session.close()
        return False

# Class Required for HTML Stripping in strip_html
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_html(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def formatSiteAddress(systemAddress):
    try:
        ipaddress.ip_address(systemAddress)
        return systemAddress
    except ValueError:
        try:
            ipaddress.ip_address(systemAddress.split(':')[0])
            return systemAddress.split(':')[0]
        except ValueError:
            return systemAddress

def table2Dict(table):
    exportedTableList = table.query.all()
    dataList = []
    for tbl in exportedTableList:
        dataList.append(dict((column.name, str(getattr(tbl, column.name))) for column in tbl.__table__.columns))
    return dataList

def newLog(logType, message):
    newLogItem = logs.logs(datetime.datetime.now(), str(message), logType)
    db.session.add(newLogItem)
    db.session.commit()
    return True
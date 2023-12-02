import sqlite3
from StockTracker.website_info import Website_info
import time
from multiprocessing import Process
from dotenv import load_dotenv
import os
from mailersend import emails
import boto3
import json
import psycopg2

load_dotenv()

NOTIFICATION_EMAIL_ID = "neqvygmjzzzg0p7w"

FETCH_ALL_INFO_SQL_QUERY = """select "StockTracker_watching".id, url, sku, email, name from "StockTracker_watching" inner join "StockTracker_user" 
    on "StockTracker_watching".user_id = "StockTracker_user".id
    inner join "StockTracker_toy" 
    on watched_toy_id = "StockTracker_toy".id
    where get_result = false;"""

UPDATE_WATCHING_STATUS_TO_ONE_TEMPLATE = """update "StockTracker_watching" 
    set get_result = {id}
    where id = 1;"""


class Watching_dto:
    def __init__(self, id, url, sku, email, name):
        self.id = id
        self.url = url
        self.sku = sku
        self.email = email
        self.name = name

def long_polling_helper():
    with open("db_config.json") as file:
        db_data = json.load(file)
    while True:
        con = psycopg2.connect(database = db_data["NAME"], host = db_data["HOST"], user = db_data["USER"], password = db_data["PASSWORD"])
        cur = con.cursor()
        inStockSkuSet = set()
        outOfStockSkuSet = set()
        shouldSendEmailWatching = []
        cur.execute(FETCH_ALL_INFO_SQL_QUERY)
        all_watching = cur.fetchall()
        # id url sku email, name
        for row in all_watching:
            id, url, sku, email, name = row
            watching_dto = Watching_dto(id, url, sku, email, name)
            if sku in inStockSkuSet:
                shouldSendEmailWatching.append(watching_dto)
            elif sku in outOfStockSkuSet:
                continue
            else:
                website_info = Website_info(watching_dto.url, watching_dto.sku)
                website_info.get_info_from_url()
                if website_info.check_stock():
                    inStockSkuSet.add(watching_dto.sku)
                    shouldSendEmailWatching.append(watching_dto)
                else:
                    outOfStockSkuSet.add(watching_dto.sku)
            time.sleep(0.7)
        # send email here and change get_result property in db

        changeDbProcess = Process(target=ChangeDbStatus, args=(shouldSendEmailWatching, ))
        changeDbProcess.start()
        changeDbProcess.join()
        sendNotificationEmailProcess = Process(target=SendNotificationEmail, args=(shouldSendEmailWatching, ))
        sendNotificationEmailProcess.start()
        sendNotificationEmailProcess.join()
        time.sleep(600)

def SendConfirmationEmail(email, name, sku):
    session = boto3.Session(region_name="us-west-1", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    sesClient = session.client("ses")
    sendArgs = {
        "Source" : "no-reply-jellycatstocktracker@incentwang.com",
        "Destination" : {
            "ToAddresses" : [email],
            "CcAddresses" : [],
            "BccAddresses" : []
        },
        "Template" : "WatchConfirmationTemplate",
        "TemplateData" : json.dumps({
            "name" : name,
            "sku" : sku,
        })
    }
    sesClient.send_templated_email(**sendArgs)

def SendNotificationEmail(watchingDtos):
    session = boto3.Session(region_name="us-west-1", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    sesClient = session.client("ses")
    for watchingDto in watchingDtos:
        sendArgs = {
            "Source" : "no-reply-jellycatstocktracker@incentwang.com",
            "Destination" : {
                "ToAddresses" : [watchingDto.email],
                "CcAddresses" : [],
                "BccAddresses" : []
            },
            "Template" : "RestockNotificationTemplate",
            "TemplateData" : json.dumps({
                "name" : watchingDto.name,
                "sku" : watchingDto.sku,
                "url" : watchingDto.url,
            })
        }

        sesClient.send_templated_email(**sendArgs)
    

def TestSendEmail(watchingDtos):
    session = boto3.Session(region_name="us-west-1", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    sesClient = session.client("ses")
    for watchingDto in watchingDtos:
        sendArgs = {
            "Source" : "no-reply-jellycatstocktracker@incentwang.com",
            "Destination" : {
                "ToAddresses" : [watchingDto.email],
                "CcAddresses" : [],
                "BccAddresses" : []
            },
            "Template" : "WatchConfirmationTemplate",
            "TemplateData" : json.dumps({
                "name" : watchingDto.name,
                "sku" : watchingDto.sku,
            })
        }

        sesClient.send_templated_email(**sendArgs)

def ChangeDbStatus(watchingDtos):
    with open("db_config.json") as file:
        db_data = json.load(file)
    con = psycopg2.connect(database = db_data["NAME"], host = db_data["HOST"], user = db_data["USER"], password = db_data["PASSWORD"])
    cur = con.cursor()
    for watchingDto in watchingDtos:
        cur.execute(UPDATE_WATCHING_STATUS_TO_ONE_TEMPLATE.format(id=watchingDto.id))

if __name__ == '__main__':
    long_polling_helper()
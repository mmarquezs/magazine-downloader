#!/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import argparse
import os
# import time
import datetime
from datetime import date, timedelta
#import requests
#from bs4 import BeautifulSoup
import subprocess
import grab
# import magnet2torrent
HOME = os.path.expanduser("~")
DB_PATH = HOME+"/.dbmagazines"
TPBURL = "https://pirateproxy.pw"
TODAY = date.today()
YESTERDAY = date.today() - timedelta(days=1)
TORRENTS_PATH = "/mnt/sda1/downloads/deluge/watch/publications"
#TORRENTS_PATH = "."
def main():
    """
    Command-line interface to subscribe,unsubscribe from newspapers,magazines and
    update/download them.
    """
    parser = argparse.ArgumentParser(
        description='Search,Download,Subscribe to Magazines,Newspapers,..')
    parser.add_argument('--u',
                        '--update',
                        action="store_true",
                        help='Search and downloads releases')
    parser.add_argument('--S',
                        '--subscribe',
                        type=str,
                        help='Subscribe')
    parser.add_argument('--U',
                        '--unsubscribe',
                        type=str,
                        help='Unsubscribe')
    # parser.add_argument('magazine',
    #                     help='Magazine to subscribe/unsubscribe')
    args = parser.parse_args()
    if args.u:
        search_download()
    elif args.S is not None:
        subscribe(args.S)
    elif args.U is not None:
        unsubscribe(args.U)
    else:
        file = open(DB_PATH)
        database = json.loads(file.read().strip())
        file.close()
        print(json.dumps(database))

def subscribe(name):
    """
    Change subscriptions status to subscribed of a magazine,newspaper.
    """
    file = open(DB_PATH)
    database = json.loads(file.read().strip())
    file.close()
    database[name]["subscribed"] = True
    file = open(DB_PATH, 'w')
    file.write(json.dumps(database, sort_keys=True, indent=4, separators=(',', ': ')))
    file.close()

def unsubscribe(name):
    """
    Change subscriptions status to unsubscribed of a magazine,newspaper.
    """
    file = open(DB_PATH)
    database = json.loads(file.read().strip())
    file.close()
    database[name]["subscribed"] = False
    file = open(DB_PATH, 'w')
    file.write(json.dumps(database, sort_keys=True, indent=4, separators=(',', ': ')))
    file.close()

def add(name, value):
    """
    Add a magazine,newspaper.
    """
    file = open(DB_PATH)
    database = json.loads(file.read().strip())
    file.close()
    database[name] = {"date":value, "subscribed":False}
    file = open(DB_PATH, 'w')
    file.write(json.dumps(database, sort_keys=True, indent=4, separators=(',', ': ')))
    file.close()
def update(name, value):
    file = open(DB_PATH)
    database = json.loads(file.read().strip())
    file.close()
    database[name]["date"] = value
    file = open(DB_PATH, 'w')
    file.write(json.dumps(database, sort_keys=True, indent=4, separators=(',', ': ')))
    file.close()
def search_download():
    file = open(DB_PATH)
    database = json.loads(file.read().strip())
    database[" ".join(sys.argv[2:-1])] = {"date":sys.argv[-1], "subscribed":False}
    file.close()
    request = requests.get(TPBURL+"/user/virana/0/3", verify=False).content
    soup = BeautifulSoup(request, "lxml")
    g_data = soup.find_all("td", {"class":None})
    db = {}
    months = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    for item in g_data:
        try:
            type_torrent = item.contents[1].text.split(" ")[1]
            if type_torrent.lower() == "revista" or type_torrent.lower() == "diario":
                name = item.contents[1].text.rstrip().split(" ")[2:]
                list_remove = []
                for word in name:
                    if word in months:
                        list_remove += [word]
                        break
                    for letter in word:
                        if letter.isdigit():
                            list_remove += [word]
                            break
                for element in list_remove:
                    name.remove(element)
                name = " ".join(name)
                date_torrent = item.contents[7].text.replace(u'\xa0', ' ').split(" ")[1]
                if date_torrent == "today":
                    date_torrent = TODAY.strftime("%d-%m")
                elif date_torrent == "y-day":
                    date_torrent = YESTERDAY.strftime("%d-%m")
                else:
                    date_torrent = "-".join(date_torrent.split("-")[::-1])
                magnet = item.contents[3].get("href")
                db[name] = {"date":date_torrent, "magnet":magnet}
        except:
            pass
        # except Exception as e:
        #     print(e)
        #     pass
    for element in list(db.items()):
        if element[0] in database:
            if datetime.datetime.strptime(element[1]["date"], "%d-%m") > datetime.datetime.strptime(database[element[0]]["date"], "%d-%m"):
                magnet2torrent.magnet2torrent(element[1]["magnet"], TORRENTS_PATH+"/"+element[0]+"-"+element[1]["date"]+".torrent")
                # if database[element[0]]["subscribed"]:
                #     print(subprocess.check_output("bash "+MAGNET2TORRENT_PATH+" \""+element[1]["magnet"]+"\" "+TORRENTS_PATH+"/"+element[0]+".torrent"))
                update(element[0], element[1]["date"])
            else:
                pass
                # print("Element antic o ja descarregat")
        else:
            add(element[0], element[1]["date"])
if __name__ == '__main__':
    main()

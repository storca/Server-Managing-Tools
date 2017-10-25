#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import time
import mysql.connector
from mysql.connector import errorcode


gamenames = {
"tf2server":"Team Fortress 2",
"csgoserver":"Counter Strike Global Offensive",
"gmodserver":"Garry's Mod",
"ts3server":"TeamSpeak 3",
"sinusbot":"Sinusbot"
}

serversPorts = {
"tf2server":27015,
"csgoserver":27016,
"gmodserver":27017,
"ts3server":9987,
"sinusbot":8087
}

serversUrls = {
"tf2server":"steam://connect/teamiskog.ddns.net:27015",
"csgoserver":"steam://connect/teamiskog.ddns.net:27016",
"gmodserver":"steam://connect/teamiskog.ddns.net:27017",
"ts3server":"ts3server://teamiskog.ddns.net?port=9987",
"sinusbot":"None"
}

class mysqlConn:
    def __init__(self, login="root", password="", db=None):
        self.login = login
        self.password = password
        self.db = db
    def begin(self):
        try:
            global cnx
            cnx = mysql.connector.connect(user=self.login,password=self.password,database=self.db, buffered=True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                return False
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                return False
            else:
                print(err)
                return False
        else:
            global mysqlCursor
            mysqlCursor = cnx.cursor()
            return True
    def createTables(self):
        sql="CREATE TABLE IF NOT EXISTS gameservers (id INT NOT NULL AUTO_INCREMENT, serverName VARCHAR(30),gameName VARCHAR(50), status TINYINT, inRepair TINYINT, lastChecked DATETIME, url VARCHAR(100), PRIMARY KEY(id));"
        try:
            mysqlCursor.execute(sql)
        except mysql.connector.Error as err:
            print("Failed to create tables : {}".format(err))
            return False
        return True
    def registerServer(self, serverName):
        addServer = ("INSERT INTO gameservers (serverName, gameName, url) VALUES (%(serverName)s, %(gameName)s, %(url)s)")
        dataServer = {'serverName':serverName, 'gameName':gamenames[serverName], 'url':serversUrls[serverName]}
	try:
            mysqlCursor.execute(addServer, dataServer)
            cnx.commit()
        except:
            print("Cannot register server "+serverName)
    def updateServer(self, serverName, status, inRepair):
        query = "UPDATE gameservers SET status=\'{}\', inRepair=\'{}\', lastChecked=\'{}\', url=\'{}\' WHERE serverName=\'{}\'".format(status, inRepair, time.strftime('%Y-%m-%d %H:%M:%S'), serversUrls[serverName], serverName)
        print(query)
        mysqlCursor.execute(query)
        #cnx.commit()
    def close(self):
        mysqlCursor.close()
        cnx.close()
def exists(name):
    query = "SELECT id, serverName FROM gameservers"
    try:
        mysqlCursor.execute(query)
    except mysql.connector.Error as err:
        print(err)
    except:
        print("Error")
    for (id,serverName) in mysqlCursor:
        if serverName == name:
            return True
    return False

def run():
    print("Monitoring is running...")
    if mysqlObj.createTables():
        print("Table created")
        for t in serversPorts:
            if not exists(t):
                mysqlObj.registerServer(t)
        for i in serversPorts:
            result = os.system("netstat -an | grep \""+str(serversPorts[i])+"\"")
            if result == "256" or result == 256:
                mysqlObj.updateServer(i, 0, 0)
            else:
                mysqlObj.updateServer(i, 1, 0)
    cnx.commit()
    mysqlObj.close()

mysqlObj = mysqlConn("login", "pass", "db")
if mysqlObj.begin():
    run()
else:
    print("Cannot connect to database")
    exit()

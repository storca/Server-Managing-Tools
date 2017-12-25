#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from ConfigParser import *
from logging import *
import mysql.connector
from mysql.connector import errorcode
import os
import time

#Those filenames could also be paths
configFileName = "mon.conf"
logFileName = "mon.log"

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
                logging.error("Something is wrong with your user name or password")
                return False
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
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
    def updateServer(self, serverName, status=None, inRepair=None):
        if inRepair == None:
            query = "UPDATE gameservers set status=\'{}\', lastChecked=\'{}\' where serverName=\'{}\'".format(status, time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            query = "UPDATE gameservers SET status=\'{}\', inRepair=\'{}\', lastChecked=\'{}\', url=\'{}\' WHERE serverName=\'{}\'".format(status, inRepair, time.strftime('%Y-%m-%d %H:%M:%S'), serversUrls[serverName], serverName)
        query = "UPDATE gameservers SET "
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

def init(configFileName, logFileName):
    try:
        config = ConfigParser()
        try:
            config.read(path)
        except ConfigParser.ParsingError as err:
            logging.warning("Invalid syntax in config file \"{}\"".format(path))
            logging.warning(err)
            return None
        except ConfigParser.MissingSectionHeaderError as err:
            logging.warning("Missing section header in config file \"{}\"".format(path))
            logging.warning(err)
            return None
        except Exception as err:
            logging.warning("Unknown error : {}".format(err))
            return None
        except IOError:
            print("Cannot find config file {}".format(configFileName))
            return None
        else
            return config


    sections = config.sections()

    #Checking the config file
    for section in sections:
        options = config.options(section)
        needed_options = ['name', 'port', 'url']
        for option in needed_options:
            if option not in options:
                log.warning("Missing option \'{}\' in section \'{}\'".format(option, section))
            elif config.get(section, option) == '':
                log.warning("Missing value in option \'{}\' in section \'{}\'".format(option, section))

    return config

def run(config):
    gamenames = config.sections()
    print("Monitoring is running...")
    if mysqlObj.createTables():
        print("Table created")
        for gamesv in gamenames:
            if not exists(gamesv):
                mysqlObj.registerServer(gamesv)
            if config.has_option(gamesv, "port"):
                result = os.system("netstat -an | grep \""+str(serversPorts[i])+"\"")
                if result == "256" or result == 256:
                    mysqlObj.updateServer(gamesv, status=0)
                else:
                    mysqlObj.updateServer(gamesv, status=1)
            elif config.has_option(gamesv, "in_maintain"):
                try:
                    val = config.getboolean(gamesv, "in_maintain")
                except ValueError:
                    logging.warning("Invalid boolean value in section \'{}\' with option \'{}\'".format(gamesv, "in_maintain"))
                else:
                    mysqlObj.updateServer(gamesv, inRepair=val)

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
    config = init(configFileName, logFileName)
    if config != None:
        run(config)
else:
    print("Cannot connect to database")
    exit()

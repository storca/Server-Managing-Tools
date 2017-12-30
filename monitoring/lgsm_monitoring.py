#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#from ConfigParser import *
import configparser
import logging
import mysql.connector
from mysql.connector import errorcode
import os
import time

#Those filenames could also be paths
configFileName = "sampleConfigFile.conf"
logFileName = None

loglevel = logging.DEBUG

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
        addServer = ("INSERT INTO gameservers (serverName) VALUES (%(serverName)s)")
        logging.debug(addServer)
        #dataServer = {'serverName':serverName, 'gameName':gamenames[serverName], 'url':serversUrls[serverName]}
        dataServer = {'serverName':serverName}
        logging.debug(dataServer)
        try:
            mysqlCursor.execute(addServer, dataServer)
            cnx.commit()
        except:
            logging.error("Cannot register server "+serverName)
    def updateServer(self, serverName, status=None, inRepair=None, name=None, url=None):
        '''
        Only one set at the time
        '''
        
        query = "UPDATE gameservers set "
        
        if status != None:
            query += "status=\'{}\'".format(status)
        elif inRepair != None:
            query += "inRepair=\'{}\'".format(inRepair)
        elif name != None:
            query += "gameName=\'{}\'".format(name)
        elif url != None:
            query += "url=\'{}\'".format(url)
        
        query += " WHERE serverName=\'{}\'".format(serverName)
        
        mysqlCursor.execute(query)
        
        logging.debug("--------MYSQL Query--------")
        logging.debug(query)
        logging.debug("---------------------------")
        
    def close(self):
        mysqlCursor.close()
        cnx.close()

def exists(name):
    query = "SELECT id, serverName FROM gameservers"
    try:
        mysqlCursor.execute(query)
    except mysql.connector.Error as err:
        logging.error(err)
    except:
        logging.error("Error")
    for (id,serverName) in mysqlCursor:
        if serverName == name:
            return True
    return False

def init(configFileName, logFileName):
    config = configparser.ConfigParser()
    try:
        config.read(configFileName)
    except configparser.ParsingError as err:
        logging.warning("Invalid syntax in config file \"{}\"".format(path))
        logging.warning(err)
        return None
    except configparser.MissingSectionHeaderError as err:
        logging.warning("Missing section header in config file \"{}\"".format(path))
        logging.warning(err)
        return None
    except Exception as err:
        logging.warning("Unknown error : {}".format(err))
        return None
    except IOError:
        print("Cannot find config file {}".format(configFileName))
        return None
    else:
        return config


def check(config):
    sections = config.sections()
    #Checking the config file
    for section in sections:
        options = config.options(section)
        needed_options = ['name', 'port', 'url']
        for option in needed_options:
            if option not in options:
                logging.warning("Missing option \'{}\' in section \'{}\'".format(option, section))
            elif config.get(section, option) == '':
                logging.warning("Missing value in option \'{}\' in section \'{}\'".format(option, section))

    return config

def run(config):

    gamenames = config.sections()
    logging.debug("Sections found :")
    logging.debug(gamenames)
    if mysqlObj.createTables():
        logging.debug("Table created")
        for gamesv in gamenames:
            if not exists(gamesv):
                mysqlObj.registerServer(gamesv)
            if config.has_option(gamesv, "port"):
                try:
                    result = os.system("netstat -an | grep \""+str(config.getint(gamesv, "port"))+"\"")
                    if result == "256" or result == 256:
                        mysqlObj.updateServer(gamesv, status=0)
                    else:
                        mysqlObj.updateServer(gamesv, status=1)
                except ValueError:
                    logging.warning("Invalid integer value in section \'{}\' with option \'{}\'".format(gamesv, "port"))
            if config.has_option(gamesv, "in_maintain"):
                try:
                    val = config.getboolean(gamesv, "in_maintain")
                except ValueError:
                    logging.warning("Invalid boolean value in section \'{}\' with option \'{}\'".format(gamesv, "in_maintain"))
                else:
                    mysqlObj.updateServer(gamesv, inRepair=val)
            if config.has_option(gamesv, "name"):
                try:
                    val = config.get(gamesv, "name")
                except:
                    logging.warning("Cannot get value in section \'{}\' with option \'{}\'".format(gamesv, "name"))
                else:
                    mysqlObj.updateServer(gamesv, name=val)
            if config.has_option(gamesv, "url"):
                try:
                    val = config.get(gamesv, "url")
                except:
                    logging.warning("Cannot get value in section \'{}\' with option \'{}\'".format(gamesv, "url"))
                else:
                    mysqlObj.updateServer(gamesv, url=val)
                    val = config.get(gamesv, "url")
        cnx.commit()
        mysqlObj.close()
'''
        for t in serversPorts:
            if not exists(t):
                mysqlObj.registerServer(t)
        for i in serversPorts:
            result = os.system("netstat -an | grep \""+str(serversPorts[i])+"\"")
            if result == "256" or result == 256:
                mysqlObj.updateServer(i, 0, 0)
            else:
                mysqlObj.updateServer(i, 1, 0)
'''



mysqlObj = mysqlConn("root", "", "myDatabase")

if logFileName == None:
    logging.basicConfig(level=loglevel)
else:
    logging.basicConfig(filename=logFileName, level=logging.DEBUG)

if mysqlObj.begin():
    config = init(configFileName, logFileName)
    if config != None:
        check(config)
        run(config)
else:
    logging.error("Cannot connect to database")
    exit()

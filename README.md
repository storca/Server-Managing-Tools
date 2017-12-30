# Server-Managing-Tools
<a href="https://travis-ci.org/storca/Server-Managing-Tools"><img src="https://travis-ci.org/storca/Server-Managing-Tools.svg?branch=master" alt="Travis Ci"/></a>  
Some tools that I've created to monitor / manage my server  

## LGSM-Manager

LGSM-Manager is a Python script that update a mysql table with servers status (checked by the Python script).  
There is a PHP script that creates a table with all the servers and their respective status.  

### Config file setup  
You can add as many servers as you want in the configuration file, just follow this syntax :  

I'll take apache for example

```
[apache1]
name=Apache HTTP
port=80
url=http://localhost
in_maintain=0

[apache2]
name=Apache HTTPs
port=443
url=https://localhost
in_maintain=0
```

### Options Available  

* 'name'        : An option to set the nice name of a server  
* 'port'        : The port (TCP) used by the server  
* 'url'         : Option to specify an url to connect to the server (is usefull to srcds servers eg: steam://connect/<yourserverport> )  
* 'in_maintain' : If the server is in maintain then, set it to '1'
  
### PHP script setup

Don't forget to change your options for the database in the 'monitoring.php' file.

Two ways to set it up :  
  - Create a symbolic link to your web folder (ln -s /path/to/source /path/to/destination)  
  - Just copy the script in your web folder :p  

### Crontab setup  
You need to run the Python script every time you want to check the servers status, uh too boring.  
On a linux terminal run :
```
apt update
apt install cron
```
Cron is now installed, let's configure it :p  
Avoid editing the crontab of root  
```
crontab -e #-> Edit the crontab for the current user
```
Add this line to your crontab file  
```
* * * * * /path/to/lgsm_monitoring.py
```
It will run the script every minute  

Start your webserver (if not started) and go to the path of 'monitoring.php'  
It should work ^^  

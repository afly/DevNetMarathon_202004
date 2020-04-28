# DevNetMarathon_202004
Cisco DevNet Marathon 04/2020

Задание с Cisco DevNet Marathon

Лаба собрана в GNS3
Адреса устройств в виде списка в скрипте. 
Username, password, enable pass запрашиваются при запуске скрипта. Предполагается, что они одинаковые на всех устройствах.

Результат выполнения скрипта:
./task_1.py 
Username:test
Password: 
Enable password:
Connecting to device 192.168.200.1 ...
Backing up device TEST-ROUTER-1 configuration...
Configuration device TEST-ROUTER-1 saved as backup_conf/TEST-ROUTER-1-20200428_20-52-21.cfg
Getting device TEST-ROUTER-1 information...
Setting ntp on device TEST-ROUTER-1 ...
Configuring command: clock timezone UTC 0
Connecting to device 192.168.200.2 ...
Backing up device R2 configuration...
Configuration device R2 saved as backup_conf/R2-20200428_20-52-42.cfg
Getting device R2 information...
Setting ntp on device R2 ...
Configuring command: clock timezone UTC 0
Connecting to device 192.168.200.20 ...
Timeout error
Connecting to device 192.168.200.3 ...
Backing up device R3 configuration...
Configuration device R3 saved as backup_conf/R3-20200428_20-53-06.cfg
Getting device R3 information...
Setting ntp on device R3 ...
Configuring command: ['clock timezone UTC 0', 'ntp server 192.168.200.2']


Devices status: 
hostname       cdp_status    image    image_ver    platform    ntp_status
-------------  ------------  -------  -----------  ----------  ---------------
TEST-ROUTER-1  enabled / 2   unknown  PE           7206VXR     Clock in UnSync
R2             enabled / 2   unknown  PE           7206VXR     Clock in UnSync
R3             enabled / 2   unknown  PE           7206VXR     Clock in UnSync


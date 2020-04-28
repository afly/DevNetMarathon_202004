#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Учебное задание: DevNetМарафон. День 1.

Дано: сеть из нескольких коммутаторов и маршрутизаторов, все они доступны по своим IP-адресам. Все IP-адреса устройств известны.Все коммутатор и маршрутизаторы работают под управлением ОС IOS или IOS XE.
Необходимо:
1.Собрать со всех устройств файлы конфигураций, сохранить их на диск, используя имя устройства и текущую дату в составеимени файла.
2. Проверить на всех коммутаторах-включен ли протокол CDP и есть ли упроцесса CDPна каждом из устройств данные о соседях.
3. Проверить, какой типпрограммного обеспечения(NPEили PE)* используется на устройствах исобрать со всех устройств данные о версиииспользуемог ПО.
4. Настроить на всех устройствах timezone GMT+0, получение данных для синхронизациивремени от источника во внутренней сети, предварительно проверив его доступность.
5. Вывести отчет в виде нескольких строк, каждая изкоторых имеет следующийформат, близкий к такому:Имя устройства -тип устройства -версия ПО -NPE/PE -CDP on/off, Xpeers-NTP in sync/not sync.
Пример:
ms-gw-01|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |PE|CDP is ON,5peers|Clock in Sync
ms-gw-02|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |NPE|CDP is ON,0 peers|Clock in Sync
'''
import getpass
import netmiko
import re
import datetime
import os
import time
from tabulate import tabulate

BACKUP_DIR = 'backup_conf'
NTP_IP = '192.168.200.2'

def connect_cisco_ios_device(device, username, passwordi, enable):
    device_params = { 'device_type': 'cisco_ios',
                      'ip': device,
                      'username': username,
                      'password': password,
                      'secret': enable
                      }
    try:
        connect = netmiko.ConnectHandler(**device_params)
    except netmiko.ssh_exception.NetmikoAuthenticationException:
        print('Authentication error')
        return 'error'
    except netmiko.ssh_exception.NetmikoTimeoutException:
        print('Timeout error')
        return 'error'
    except Exception as err:
        print('Error: ', err)
        return 'error'
    return connect

def disconnect_device(connect):
    connect.disconnect()

def send_show_command(connect, command):
    #ssh = connect_cisco_ios_device(device)
    result = connect.send_command(command)
    return result

def send_config_command(connect, command):
    #ssh = connect_cisco_ios_device(device)
    result = connect.send_config_set(command)
    return result

def get_hostname(connect):
    prompt = connect.find_prompt()
    match = re.search(r'(\S+)#$', prompt)
    result = match.group(1)
    return result

def get_current_date_time():
    current = datetime.datetime.now()
    result = current.strftime('%Y%m%d_%H-%M-%S')
    return result

def make_backup_confg(name, config):
    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    file_name = '{}-{}.cfg'.format(name, get_current_date_time())
    backup_path = os.path.join(BACKUP_DIR, file_name)
    with open(backup_path, 'w') as f:
        f.write(config)
    print('Configuration device {} saved as {}'.format(name, backup_path))

def get_cdp_status(cdp_status):
    if '% CDP is not enabled' in cdp_status:
        result = 'not enabled /'
        return result
    else:
        regexp = (r'Device ID: (\S+)')
        match = re.finditer(regexp, cdp_status)
        neighbor_list = []
        for neighbor in match:
            neighbor_list.append(neighbor.group(1))
        result = 'enabled / {}'.format(len(neighbor_list))
        return result

def get_image(sh_version):
    result = {}
    regexp_image = (r'System image file is (\S+)')
    match_image = re.search(regexp_image, sh_version)
    image = re.split(r'[:/"]', match_image.group(1))[-2]
    result['image'] = image
    if 'npe' in image:
        result['image_ver'] = 'NPE'
    else:
        result['image_ver'] = 'PE'
    regexp_platform = (r'[Cc]isco +(\S+) +\S+ +processor')
    match_platform = re.search(regexp_platform, sh_version)
    result['platform'] = match_platform.group(1)
    return result

def config_ntp(connect, ntp_ip):
    command_ping = 'ping {}'.format(ntp_ip)
    ping = send_show_command(connect, command_ping)
    regexp_ping = (r'Success rate is (\d+) percent')
    match_ping = re.search(regexp_ping, ping)
    if int(match_ping.group(1)) == 0:
        send_config_command(connect, 'clock timezone UTC 0')
        return 'ntp is unreachable'
    else:
        ntp_associations = send_show_command(connect, 'show ntp associations')
        if ntp_ip not in ntp_associations:
            commands = ['clock timezone UTC 0','ntp server {}'.format(ntp_ip)]
        else:
            commands = 'clock timezone UTC 0'
        print('Configuring command: {}'.format(commands))
        send_config_command(connect, commands)
        time.sleep(5)
        ntp_status = send_show_command(connect, 'show ntp status')
        if 'Clock is synchronized' in ntp_status:
            return 'Clock in Sync'
        else:
            return 'Clock in UnSync'


def main(list_ip, username, password, enable):
    result = []
    for ip in list_ip:
        status_dict = {}
        print('Connecting to device {} ...'.format(ip))
        connect = connect_cisco_ios_device(ip, username, password, enable)
        if connect == 'error':
            continue
        connect.enable()
        
        hostname = get_hostname(connect)
        status_dict['hostname'] = hostname
        print('Backing up device {} configuration...'.format(hostname))
        running_config = send_show_command(connect, 'show running-config')
        make_backup_confg(hostname, running_config)
        
        print('Getting device {} information...'.format(hostname))
        cdp = send_show_command(connect, 'show cdp neighbors detail')
        cdp_status = get_cdp_status(cdp)
        status_dict['cdp_status'] = cdp_status
        
        version = send_show_command(connect, 'show version')
        device_info = get_image(version)
        status_dict['image'] = device_info['image']
        status_dict['image_ver'] = device_info['image_ver']
        status_dict['platform'] = device_info['platform']
        
        print('Setting ntp on device {} ...'.format(hostname))
        ntp_status = config_ntp(connect, NTP_IP)
        status_dict['ntp_status'] = ntp_status
        
        result.append(status_dict)
        disconnect_device(connect)
    print('\n')
    print('Devices status: ')
    print(tabulate(result, headers='keys'))


if __name__ == "__main__":
    list_ip = ['192.168.200.1', '192.168.200.2', '192.168.200.20', '192.168.200.3']
    username = input('Username:')
    password = getpass.getpass()
    enable = getpass.getpass('Enable password:')
    #username = 'test'
    #password = 'test1'
    main(list_ip, username, password, enable)


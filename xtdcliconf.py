#!/usr/bin/env python
'''
  xtdcliconf.py

  Eases login on HP Switches with Comware firmware, switching to the extended cli
  mode and dropping into ssh session directly. Can also be used to execute predefined
  command sequences on the switch

  ugly code should be reworked :-)

 ----------------------------------------------------------------------------
 "THE BEER-WARE LICENSE" (Revision 42):
 <abi@grinser.de> wrote this file. As long as you retain this notice you
 can do whatever you want with this stuff. If we meet some day, and you think
 this stuff is worth it, you can buy me a beer in return Michael Ablassmeier
 ----------------------------------------------------------------------------

'''
import re
import logging
import paramiko
import sys
import json
import os
import argparse
from paramiko_expect import SSHClientInteraction

CONFIG_DIR='config'

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="hostname for switch", required=True)
parser.add_argument("--user", help="username for switch", required=True)
parser.add_argument("--password", help="password for switch", required=True)
parser.add_argument("--execute", help="exec commands from file", required=False, type=str)
parser.add_argument("--save", help="save config on swith",required=False,action="store_true")
parser.add_argument("--shell", help="drop to shell",required=False,action="store_true")
parser.add_argument("--verbose", help="echo interact output shell",required=False,action="store_true")
args = parser.parse_args()

host = args.host
username = args.user
password = args.password

if args.execute:
    cmds = args.execute
else:
    cmds = False


FORMAT="%(module)s:%(funcName)s(): %(msg)s"
logging.basicConfig(level=logging.INFO,format=FORMAT)

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect (host,
                username=username,
                password=password,
                pkey=None,
                allow_agent=None,
                look_for_keys=False,
                timeout=5
    )
except Exception as e:
    logging.error('Unable to connect switch via SSH: "%s"' % e)
    sys.exit(1)

interact = SSHClientInteraction(client, timeout=2, display=args.verbose)

class MatchNotFound(Exception):
    pass

class HostnameNotFound(Exception):
    pass

def search_match(regex, string):
    ''' paramiko_expect does not return a regex object so we need
        to parse the name of the switch from the prompt or any other
        value we want to work with
    '''
    grp = re.search(regex, string)
    if grp:
        return grp
    else:
        raise MatchNotFound('Unable to find match')

def get_switch_hostname():
    reg = '.*<(.*)>$'
    interact.send('\n')
    interact.expect(reg)
    try:
        match = search_match(reg, interact.current_output)
        return match.group(1)
    except MatchNotFound as e:
        raise HostnameNotFound('Unable to find switch hostname')

def read_switch_config(hostname):
    config = '%s/%s' % (CONFIG_DIR, hostname)
    logging.info('Search for config file: "%s"' % config)
    if os.path.exists(config):
        logging.info('Found config')
        with open(config) as json_conf:
            data = json.load(json_conf)
        return data
    else:
        return False

try:
    hostname = get_switch_hostname()
    logging.info('Detected Switch Hostname: "%s"' % hostname)
except HostnameNotFound as e:
    logging.warning('Unable to find hostname')

config = read_switch_config(hostname)

def execute_xtd_cli():
    '''
        use specified cli mode cmd from existing config file,
        if config file is not existant, use default passwords
        found from the web
    '''
    if config:
        logging.info('Use cli mode cmd from config: "%s"' % config['cli-mode-cmd'])
        cli_str = '.*%s.*'  % str(config['cli-mode-cmd'])
    else:
        cli_str = '.*xtd-cli-mode.*'

    try:
        interact.send('?')
        interact.expect(cli_str)
        if config:
            password = config['password']
            logging.info('Use password from config: "%s"' % config['password'])
        else:
            password = 'foes-bent-pile-atom-ship'
        xtd_cmd = 'xtd-cli-mode'
    except Exception as e:
        logging.info('CLI Mode "%s" not found in switch output, fallback to _cmdline-mode on' % cli_str)
        xtd_cmd = '_cmdline-mode on'
        if config:
            password = config['password']
        else:
            password = 'Jinhua1920unauthorized'
    finally:
        try:
            logging.info('Configured switch supports XTD CLI Cmd, switch to extended cli mode with cmd: "%s"' % xtd_cmd)
            interact.send(xtd_cmd)
            interact.expect('.*All commands can be displayed and executed.*')
        except Exception as e:
            logging.error('Unable to switch to extended cli mode')
            sys.exit(1)

        interact.send('Y')
        try:
            interact.expect('.*assword:.*')
            interact.send(password)
            interact.expect('.*Warning.*')
        except Exception as e:
            logging.error('Unable to switch to system view using specified password')
            sys.exit(1)
        interact.send('system-view')
        interact.expect('.*System.*[.*].*')
        interact.send('\n')

execute_xtd_cli()

if cmds:
    logging.info('executing commands from file: %s' % cmds)
    with open(cmds) as cmdfile:
        for cmd in cmdfile.readlines():
            interact.send(cmd)

if args.save:
	interact.send('save')
	interact.expect('.*The current configuration will be written to the device.*')
	interact.send('Y')
	interact.expect('.*press the enter key.*')
	interact.send('\n')
	interact.expect('.*overwrite.*')
	interact.send('Y')
	interact.expect('.*Saved.*')
else:
    interact.take_control()

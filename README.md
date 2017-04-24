xtdcliconf
=========

Drop into HP Comare Extended CLI mode directly.


Description
-----------

HP Switches and derivates using HP comware are not directly manageable using
ssh, customers are forced to administrate those switches via web frontend,
which is a pain in the ass.

There is however a so called "Extended CLI mode" for developers and/or advanced
system engineers, based on the installed firmware secured with a differend
password which gives full access to the switch configuration on the command
line. 

Some of the passwords revealed can be found using google or looking at the
tools source.

Entering the XTD mode requires manual user input and this tools eases the login
by automatically dropping the user to a system-view capable shell using
paramiko and paramiko_expect.

As different switches run on different firmware and require different passwords
or commands to get into extended cli mode / system view one can also define a
password for each switch in a config file.

It can also execute a sequence of commands read from a config file, for example
if one has to define a vlan on 10 different switches, this comes in handy.

Prerequisites
------------

Configure your HP Comware based switch to allow ssh login

Usage
------------

        usage: xtdcliconf.py [-h] --host HOST --user USER --password PASSWORD
                     [--execute EXECUTE] [--save] [--shell] [--verbose]

Example connect
------------

Connect to a HP comware switch via SSH and go into extended cli mode:

```
 (switch)abi@x:~/switchconf/xtdcliconf$ python xtdcliconf.py --host 192.168.250.100 --user sshuser --password sshpass
 transport:_log(): Connected (version 2.0, client Comware-7.1.070)
 transport:_log(): Authentication (password) successful!
 xtdcliconf:<module>(): Detected Switch Hostname: "rz1-l2-sw100"
 xtdcliconf:read_switch_config(): Search for config file: "config/rz1-l2-sw100"
 xtdcliconf:execute_xtd_cli(): Configured switch supports XTD CLI Cmd, switch to extended cli mode with cmd: "xtd-cli-mode"
 [rz1-l2-sw100]
 [rz1-l2-sw100]
 [rz1-l2-sw100]
 System view commands:
   aaa                      AAA configuration
   access-list              Alias for 'acl'
   acl                      Specify ACL configuration information
   alias                    Configure an alias for a command
   apply                    Apply a PoE profile
```

Config files
------------

Based on the configured switch name one can create a config file which sets the xtd cli mode command
and password to be used. Some switches use "xtd-cli-mode" cmd to switch to extended mode, others with
older firmware use "_cmdline-mode on"

If you have to manage multiple switches with different firmware and as such commands or passwords you
can define them in the config file like:

```
{
        "cli-mode-cmd": "xtd-cli-mode",
        "password": "foes-bent-pile-atom-ship"
}
```

Executing commands
------------

To execute multiple commands create a simple text file with system-view commands like:

 vlan 100
 name foo
 description bar

and execute them on switch via:


 ```
 xtdcliconf.py --host 192.168.250.100 --user sshuser --password sshpassword --execute cmd
 transport:_log(): Connected (version 2.0, client Comware-7.1.070)
 transport:_log(): Authentication (password) successful!
 xtdcliconf:<module>(): Detected Switch Hostname: "rz1-l2-sw100"
 xtdcliconf:read_switch_config(): Search for config file: "config/rz1-l2-sw100"
 xtdcliconf:execute_xtd_cli(): Configured switch supports XTD CLI Cmd, switch to extended cli mode with cmd: "xtd-cli-mode"
 xtdcliconf:<module>(): executing commands from file: cmd
 [rz1-l2-sw100]
 [rz1-l2-sw100]
 [rz1-l2-sw100]vlan 100
 [rz1-l2-sw100-vlan100]name foo
 [rz1-l2-sw100-vlan100]description bar
 [rz1-l2-sw100-vlan100]
 ``` 

if option ```--save``` is specified it makes sure all changes are saved before exiting the session:

 [rz1-l2-sw100]save
 The current configuration will be written to the device. Are you sure? [Y/N]:Y
 Please input the file name(*.cfg)[flash:/startup.cfg]
 (To leave the existing filename unchanged, press the enter key):
 flash:/startup.cfg exists, overwrite? [Y/N]:
 Before pressing ENTER you must choose 'YES' or 'NO'[Y/N]:Y
 Validating file. Please wait...
 Saved the current configuration to mainboard device successfully.
``` 


Debugging
------------

If you want t osee the full switch communication or something goes wrong use
```--verbose``` option to see full traffic sent the switch.
 


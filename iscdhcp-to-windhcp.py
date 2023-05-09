#!/usr/bin/python3

# 
# Copyright (c) 2023 Stephen Loeckle
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import re
import traceback
import json

version = '0.1'

iscfilename='dhcpd.conf'
# xmlfilename='ms-dhcp-export.xml'
dhcpfailoverserver='dhcp-b.abc.edu'
dhcpfailovername='AB-Failover'

def comparexml(datain,debug=None):
    compno = 0
    compareresults = {}
    with open(xmlfilename, 'r') as file:
        xmldata = file.read().replace('\n', '')
    for key,val in datain.items():
        if val['network'] not in xmldata:
            compno += 1
            if debug:
                print('*** {} NOT found in dhcp xmldata ***'.format(val['network']))
                j = json.dumps(val, indent = 4)   
                print(j)
            compareresults[compno] = val
    return(compareresults)

def createscript(scriptdata1,scriptdata2=None,debug=None):
    for key, val in scriptdata1.items():
        try:
            startrange, endrange = val['range'].rsplit(',',1)
            print('add-dhcpserverv4scope -name "{}" -startrange {} -endrange {} -subnetmask {}'.format(val['name'],startrange,endrange,val['netmask']))
        except:
            pass
            print('*** Error in subnet scriptdata1: {}'.format(val))
            err = traceback.format_exc()
            print(err)
            prefix = val['network'].rsplit('.',1)
            print('*** Try this line: {}'.format('add-dhcpserverv4scope -name "{}" -startrange {}{} -endrange {}{} -subnetmask {}'.format(val['name'],prefix[0],'.1',prefix[0],'.254',val['netmask'])))
        try:
            if val['routers']:
                print('set-dhcpserverv4optionvalue -scopeid {} -router {}'.format(val['network'],val['routers']))
        except:
            print('Subnet {} has no routers option'.format(val['network']))
            pass
            
        try:
            if val['domain-name-servers']:
                print('set-dhcpserverv4optionvalue -scopeid {} -dnsserver {}'.format(val['network'],val['domain-name-servers']))
        except:
            print('Subnet {} has no domain-name-servers option'.format(val['network']))
            pass
            
        try:
            if val['netbios-name-servers']:
                print('set-dhcpserverv4optionvalue -scopeid {} -winsserver {}'.format(val['network'],val['domain-name-servers']))
        except:
            print('Subnet {} has no domain-name-servers option'.format(val['network']))
            pass
            
        try:
            if dhcpfailoverserver:
                print('add-dhcpserverv4failoverscope -name "{}" -scopeid {}'.format(dhcpfailovername,val['network']))
        except:
            pass
    if scriptdata2:
        for key, val in scriptdata2.items():
            try:
                mac = val['mac'].replace(':','-')
            except:
                pass
            else:
                try:
                    print('add-dhcpserverv4reservation -description "{}" -clientid "{}" -ipaddress {} -scopeid {}'.format(val['name'],mac,val['ip'],val['scopeid']))
                except:
                    pass
                    print('*** Error in host scriptdata2: {}'.format(val))
                    err = traceback.format_exc()
                    print(err)
        print()
            
def parseconfig(debug=None):
    lineno = 0
    subnetno = 0
    hostno = 0
    subnets = {}
    hosts = {}
    file = open(iscfilename, 'r')
    while True:
        line = file.readline()
        lineno += 1
        if debug:
            print('Parsing main line #{}'.format(lineno))
        if line.startswith('#'):
            lastline = line
            continue
        elif 'subnet ' in line:
            if debug:
                print('Found subnet line')
            subnetoptionno = 0
            miscoptionno = 0
            line = line.rstrip()
            line = line.lstrip()
            subnetheader = line.split(' ')
            try:
                if subnetheader[2] == 'netmask':
                    subnetno += 1
                    subnets[subnetno] = {}
                    lastline = lastline.rstrip()
                    lastline = lastline.lstrip()
                    if lastline.startswith('#'):
                        lastline = lastline.strip('# ')
                        lastline = lastline.strip('#')
                        subnets[subnetno]['name'] = lastline
                    else:
                        subnets[subnetno]['name'] = subnetheader[1]
                    subnets[subnetno]['network'] = subnetheader[1]
                    subnets[subnetno]['netmask'] = subnetheader[3]
                    # subnets[subnetno]['options'] = {}
                    while True:
                        if '}' in line:
                            if debug:
                                print('Found } in line')
                            break
                        elif '{' in line:
                            if debug:
                                print('Found { in line')
                        else:
                            if 'routers ' in line:
                                line = line.rstrip()
                                line = line.lstrip()
                                # line = line.strip('"')
                                line = line.strip(';')
                                options = line.split(' ')
                                subnets[subnetno]['routers'] = options[2]
                            if 'option ' in line and 'routers ' not in line:
                                subnetoptionno += 1
                                line = line.rstrip()
                                line = line.lstrip()
                                # line = line.strip('"')
                                line = line.strip(';')
                                options = line.split(' ')
                                
                                if len(options) > 3:
                                    subnets[subnetno]['{}'.format(options[1])] = ''.join(options[2:])
                                    subnets[subnetno]['{}'.format(options[1])] = subnets[subnetno]['{}'.format(options[1])].strip('"')
                                else:
                                    subnets[subnetno]['{}'.format(options[1])] = options[2]
                                    subnets[subnetno]['{}'.format(options[1])] = subnets[subnetno]['{}'.format(options[1])].strip('"')
                            elif 'option ' not in line and 'routers ' not in line and len(line) > 1:
                                subnetoptionno += 1
                                line = line.rstrip()
                                line = line.lstrip()
                                line = line.strip(';')
                                options = line.split(' ')
                                if len(options) > 2:
                                    subnets[subnetno]['{}'.format(options[0])] = ','.join(options[1:])
                                    subnets[subnetno]['{}'.format(options[0])] = subnets[subnetno]['{}'.format(options[0])].strip('"')
                                else:
                                    subnets[subnetno]['{}'.format(options[0])] = options[1]
                                    subnets[subnetno]['{}'.format(options[0])] = subnets[subnetno]['{}'.format(options[0])].strip('"')
                        line = file.readline()
                        if not line:
                            break
                        else:
                            lineno += 1
                        if debug:
                            print('Parsing subnet line #{}'.format(lineno))
            except:
    #            print('ERROR: "{}" does not match subnet section header format'.format(line))
                err = traceback.format_exc()
                if debug:
                    print(err)
                    print(line)
                pass
            subnetno += 1
        elif 'host ' in line:
            hostno += 1
            
            hosts[hostno] = {}
            line = line.rstrip()
            line = line.lstrip()
            hostheader = line.split(' ')      
            hosts[hostno]['name'] = hostheader[1]
            if debug:
                print('Found host line')
            while True:
                print(line)
                if '}' in line:
                    if debug:
                        print('Parsing host line #{}'.format(lineno))
                        print('Found } in line')
                    break
                elif '{' in line:
                    if debug:
                        print('Parsing host line #{}'.format(lineno))
                        print('Found { in line')
                else:
                    if 'hardware ' in line:
                        if debug:
                            print('Parsing host line #{}'.format(lineno))
                            print('Found hardware in line')
                        line = line.rstrip()
                        line = line.lstrip()
                        line = line.strip(';')
                        options = line.split(' ')
                        hosts[hostno]['mac'] = options[2]
                    elif 'fixed-address ' in line:
                        if debug:
                            print('Parsing host line #{}'.format(lineno))
                            print('Found fixed-address in line')
                        line = line.rstrip()
                        line = line.lstrip()
                        line = line.strip(';')
                        options = line.split(' ')
                        hosts[hostno]['ip'] = options[1] 
                line = file.readline()
                if not line:
                    break
                else:
                    lineno += 1
                if debug:
                    print('Parsing host line #{}'.format(lineno))
        else:
            continue
        if not line:
            break
    if debug:
        print(subnets)
        print(hosts)
        s = json.dumps(subnets, indent = 4) 
        h = json.dumps(hosts, indent = 4) 
        print(s)
        print(h)
        
    return(subnets,hosts)
    
def processhosts(subnets,hosts):
    subnetlist = []
    hostlist = {}
    hostno = 0
    for a,b in subnets.items():
        prefix = b['network'].rsplit('.',1)
        subnetlist.append(prefix[0])
    print(subnetlist)
    for c,d in hosts.items():
        # print(d)
        try:
            hostprefix = d['ip'].rsplit('.',1)
            # print(hostprefix[0])
            try:
                location = subnetlist.index(hostprefix[0])
            except:
                pass
                location = None
            else:
                print(location)
                scopeid = subnetlist[location]+'.0'
                hostno += 1
                hostlist[hostno] = {}
                hostlist[hostno] = d
                hostlist[hostno]['scopeid'] = scopeid
        except:
            pass
    print(hostlist) 
    return(hostlist)

def main():
    #parseddata = parseconfig(debug=True)
    subnetdata,hostdata = parseconfig()
    # createscript(parseddata)
    try:
        if xmlfilename:
            print('Found xml file name. Comparing data from isc dhcp server and microsoft dhcp export first.')
            subnetresults = comparexml(subnetdata, debug=True)
            if hostdata:
                hostresults = processhosts(subnetresults,hostdata)
                cmds = createscript(subnetresults,hostresults)
            else:
                cmds = createscript(subnetresults)
        else:
            print('Processing data from isc dhcp server')
            hostresults = processhosts(subnetdata,hostdata)
            cmds = createscript(subnetdata,hostresults)        
    except:
        pass
        print('Processing data from isc dhcp server')
        hostresults = processhosts(subnetdata,hostdata)
        cmds = createscript(subnetdata,hostresults)        
    else:
        print(cmds)
    
if __name__ == '__main__':
    main()
#!/usr/bin/python
import sys
import re
import os
import argparse
from tabulate import tabulate

parser=argparse.ArgumentParser()
parser.add_argument("-l","--lldp",nargs="?",help="Check LLDP status")
parser.add_argument("-m","--mlag",nargs="?",help="Check MLAG status")
parser.add_argument("-mi","--mlagint",nargs="?",help="Check MLAG Interface status")
parser.add_argument("-b","--bgp",nargs="?",help="Check BGP status")
parser.add_argument("-o","--ospf",nargs="?",help="Check OSPF status")
parser.add_argument("-v","--version",nargs="?",help="Check Version")
args=parser.parse_args()

def read_file(file_name):
 #print(file_name)    
 with open(file_name) as f:
  data=f.readlines()
 return data

#regexp = re.compile('^Port.*Flags$')
#for i in data:
# a=data.index(i)  if regexp.search(i) and a==0 else 0
# print a

#THIS IS NOT USED NOW!#
#def phy_int_list():
# phy_int_list=os.popen('cat 137753-show-tech-AU-SYD-SY3-7280-CORE01-02_01.1343  | egrep Et.*LLDP | cut -d " "  -f2 ').readlines()
#return phy_int_list

def file_finder(file_name):
 if ' ' in file_name:
  file_name="'"+file_name+"'"   
 check='ls | grep -v gz | grep -i '+file_name
 file_list=os.popen(check).readlines()
 if len(file_list) > 1:
  print('\nMore than one match found for filename, please be more specific!\n')
  for i in file_list:
   print i
  sys.exit(-2)
 else:
  file_name=file_list[0].strip('\n')
  if ' ' in file_name:
   file_name="'"+file_name+"'"
  return file_name

def check_mlagint(file_name):
 data=read_file(file_name)
 mi=[]
 regexp = re.compile('mlag.*state.*oper.*changes')
 for i in data:
  if regexp.search(i):
    index=data.index(i)+2
 for i in range(index,index+200):
  if data[i].isspace():
   break
  else:
   mi.append(data[i].split('       '))
 print('\n')
 print tabulate(mi, headers=['MLAG', 'State','Local','Remote','Oper[Local/Remote]','Config[Local/Remote]','Last Change','Changes'],tablefmt='fancy_grid')
 print('\n')  


def check_bgp(file_name):
 data=read_file(file_name)
 bgp=[]
 temp=[]
 index_val=0
 rid=asnum=''
 ######COME UP WITH A BETTER REGEX;figure out why \b(\d+\.)+\d+\b not working########
 re_rid='\d+\.\d+\.\d+\.\d'
 re_as='\d+$'
 regexp = re.compile('------------- show ip bgp summary vrf all -------------')
 for i in data:
  if regexp.search(i):
    index=data.index(i)+2
 for i in range(index,index+200):
  if data[i].isspace():
   break
  else:
   if 'VRF' in data[i]:
    vrf= data[i].split()[-1]
   if 'identifier' in data[i]:
    rid=re.findall(re_rid,data[i])[0]
    asnum=re.findall(re_as,data[i])
   regexp = re.compile('Neighbor.*AS.*State.*PfxAcc')
   if regexp.search(data[i]):
    index_val=i+1
 #print data[index_val]
    for j in range(index_val,index_val+200):
     if 'VRF' in data[j]:
      if len(bgp)>0:
       for i in bgp:
        temp.append(filter(None,i))
      else:
        print('\nNO BGP NEI for the VRF '+ vrf+'with RID' + rid) 
          
      print tabulate(temp, headers=['Neighbor', 'V','AS','MsgRcvd','MsgSent','InQ','OutQ','Up/Down','State' ,'PfxRcd','PfxAcc','VRF','RID'],tablefmt='fancy_grid')
      bgp=[] 
      temp=[]
      break
     if data[j].isspace():
      if len(bgp)>0:
       for i in bgp:
        temp.append(filter(None,i))
      else:    
       print('NO BGP NEI for the VRF '+ vrf+'with RID' + rid) 
      print tabulate(temp, headers=['Neighbor', 'V','AS','MsgRcvd','MsgSent','InQ','OutQ','Up/Down','State' ,'PfxRcd','PfxAcc','VRF','RID'],tablefmt='fancy_grid')
      bgp=[] 
      temp=[]
      bgp=[] 
      break
     else:
      data[j]=data[j]+' '+vrf
      data[j]=data[j]+' '+rid
      bgp.append(data[j].split(' '))
def check_ver(file_name):
 ver=temp=[]   
 data=read_file(file_name)
 regexp = re.compile('------------- show version detail -------------')
 for i in data:
  if regexp.search(i):
    index=data.index(i)+1
 for i in range(index,index+100):
  if 'Installed software packages' in data[i]:
   ver.append(temp)
   break
  else:
   temp.append(data[i])
   print data[i]   
########TABULATE IS NOT WORKING;FIX IT TO GET THE OUTPUT FORMATTING!!#####
 #header=['Show Version']
 #print("\n")
 #print tabulate(ver,headers=header,tablefmt='fancy_grid')
 #print('\n')
 
def check_ospf(file_name):
 ospf=[]
 data=read_file(file_name)
 regexp = re.compile('------------- show ip ospf neighbor -------------')
 for i in data:
  if regexp.search(i):
    index=data.index(i)+3
 for i in range(index,index+200):
  if data[i].isspace():
   break
  else:
    ospf.append(filter(None,data[i].split(' ')))
 header=['Neighbor ID','VRF','Pri','State','Dead Time','Address','Interface']    
 print("\n")
 print tabulate(ospf,headers=header,tablefmt='fancy_grid')
 print('\n')
def check_mlag(file_name):
 mlag=[]
 lif=''
 change=''
 did=''
 check='cat '+file_name+'  | grep -e \'MLAG Configuration:\' -A 30'
 data=os.popen(check).readlines()
 #######EDIT THE CODE BELOW;COME UP WITH SOMETHING BETTER##########
 for i in data:
  if 'domain-id' in i:
   did=i.split(':')[1].strip(' ').strip('\n')
  if 'local-interface' in i:
   lif=i.split(':')[1].strip(' ').strip('\n')
  if 'peer-address' in i:
   pad=i.split(':')[1].strip(' ').strip('\n')
  if 'state   ' in i:
   state=i.split(':')[1].strip(' ').strip('\n')
  if 'State  ' in i and 'Peer' not in i:
   state=state+'-'+i.split(':')[1].strip(' ').strip('\n')
  if 'tate change' in i:
   change=change+' - '+i.split(':')[1].strip(' ').strip('\n')
  if 'Configured  ' in i:
   cpo=i.split(':')[1].strip(' ').strip('\n')
  if 'Inactive   ' in i:
   ipo=i.split(':')[1].strip(' ').strip('\n')
  if 'Active-partial  ' in i:
   appo=i.split(':')[1].strip(' ').strip('\n')
  if 'Active-full  ' in i:
   afpo=i.split(':')[1].strip(' ').strip('\n')

 mlag.append([did,lif,pad,state,change[3:],cpo,ipo,appo,afpo])
 print('\n')
 print tabulate(mlag, headers=['Domain-ID', 'Local Interface','Peer-Address','State','Change(s)','Configured Po','Inactive Po','Active-Partial Po','Active-Full Po'],tablefmt='fancy_grid')
 print('\n')
def check_lldp(file_name):
 lldp=[]
 temp=[]
 sname=''
 pid=''
 pdesc=''
 check='cat '+file_name+'  | egrep Et.*LLDP | egrep -v 0.L | cut -d " "  -f2 '
 lldp_int_list=os.popen(check).readlines()
#####Need to fix this######
 lldp_int_list.append('Management1')
 for i in lldp_int_list:
  check='cat '+file_name+'  | grep -e "'+i.strip('\n')+'\s.*LLDP" -A 20'
  data=os.popen(check).readlines()
  for j in data:
   if 'System Name' in j:
    sname=j.split("\"")[1]
   if 'Port ID    ' in j:
       pid=j.split(":")[1].strip("\"")
   if 'Port Description' in j:
    pdesc=j.split("\"")[1]
   if sname and pid !='':
    lldp.append([sname,i,pid,pdesc])
    sname=''
    pid=''
 print('\n')
 print tabulate(lldp, headers=['Neighbor', 'Local port','Remote Port','Remote Description'],tablefmt='fancy_grid')
 print('\n')

def main():
 #file=file_finder(args.lldp)   
 if args.lldp:
  file=file_finder(args.lldp)   
  check_lldp(file)
 if args.mlag:
  file=file_finder(args.mlag)
  check_mlag(file)
 if args.mlagint:
  file=file_finder(args.mlagint)
  check_mlagint(file)
 if args.bgp:
  file=file_finder(args.bgp)
  check_bgp(file)
 if args.ospf:
  file=file_finder(args.ospf)
  check_ospf(file)  
 if args.version:
  file=file_finder(args.version)
  check_ver(file)
if __name__=='__main__':
 main()


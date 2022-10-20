import argparse
import sys
import os
import configparser
import json

from gvm.connections import TLSConnection
from gvm.errors import GvmError
from gvm.protocols.latest import Gmp
from gvm.transforms import EtreeCheckCommandTransform
from gvm.xml import pretty_print

from colorama import Fore
from datetime import datetime, date
from pymongo import MongoClient
from bson import ObjectId

import firebase_admin
from firebase_admin import credentials, firestore

os.chdir("/opt/scanone/vuln-management/")
config_file = configparser.ConfigParser()
config_file.read("config.ini")

hostname = config_file["OpenVAS"].get("hostname")
port = config_file["OpenVAS"].get("port")
username = config_file["OpenVAS"].get("username")
password = config_file["OpenVAS"].get("password")
config_id = config_file["OpenVAS"].get("config_id")
scanner_id = config_file["OpenVAS"].get("scanner_id")
port_list_id = config_file["OpenVAS"].get("port_list_id")

gvmConnection = TLSConnection(hostname=hostname, port=int(port))
transform = EtreeCheckCommandTransform()

class GvmScan:
    def __init__(self, reportId, status, progress, data):
        self.reportId = reportId
        self.status = status
        self.progress = progress
        self.data = data

def recursive_dict(element):
    """Takes an lxml element and returns a corresponding nested python dictionary.
       If there's multiple child elements with same tag, it will have a list of them.
       Improvement on https://lxml.de/FAQ.html#how-can-i-map-an-xml-tree-into-a-dict-of-dicts"""
    
    # Trivial case returns only the element text.
    if len(element) == 0:
        return element.text
    
    # Nested case returns a proper dictionary.
    else:
        retval = {}
        
        for child in element:
            # Recursive call computed, but not placed yet.
            recurse = recursive_dict(child)
            
            # No previous entry means it's now a single entry.
            if child.tag not in (retval):
                retval[child.tag] = recurse
                
            # Previous singe entry means it's now a list.
            elif type(retval[child.tag]) is not list:
                oldval = retval[child.tag]
                retval[child.tag] = [oldval, recurse]
                
            # Previous list entry means the list gets appended.
            else:
                oldlist = retval[child.tag]
                retval[child.tag] = oldlist + [recurse]
                
        return retval

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # ARGUMENTS FROM API CALL
    parser.add_argument("-e", "--env", help = "environment", required = "true")
    parser.add_argument("-uid", "--userid", help = "user id", required = "true")
    parser.add_argument("-tid", "--testid", help = "test id", required = "true")
    args = parser.parse_args()
    

    with Gmp(connection=gvmConnection, transform=transform) as gmp:
        try: 

            test_id = str(args.testid)
            user_id = str(args.userid)

            print(f"{Fore.GREEN}Running OpenVAS Scan Check for Test {test_id}")

            gmp.authenticate(username, password)

            version = gmp.get_version()
            print(f"Greenbone OS | OpenVAS v{ version.find('version').text }")

            # GET CURRENT REPORT JSON
            for file in os.listdir(f"/opt/scanone/vuln-management/reports/openvas/{user_id}"):
                if test_id in file:
                    os.chdir(f"/opt/scanone/vuln-management/reports/openvas/{user_id}")
                    open_file = open(file)

                    json_content = json.load(open_file)
                    report_data = gmp.get_report(json_content['reportId'], details=True, filter_string='apply_overrides=0 levels=hmlg min_qod=0 rows=1000 first=1 sort-reverse=severity')
                    report_dict = recursive_dict(report_data)['report']['report']
                    print(f"{Fore.LIGHTBLUE_EX}Report: {json_content['reportId']} - {report_dict['scan_run_status']} - {report_dict['task']['progress']} %")

                    scan_data = GvmScan(
                        json_content['reportId'], 
                        report_dict['scan_run_status'],
                        report_dict['task']['progress'],
                        report_dict
                    )

                    with open(f"/opt/scanone/vuln-management/reports/openvas/{user_id}/{file}", "w") as outfile:
                        json.dump(scan_data.__dict__, outfile)

        except BaseException as error:
            print(f'{Fore.RED}Error occurred on OpenVAS Scan Check\n{str(error)}', file=sys.stderr)


      


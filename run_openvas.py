import configparser
import os
import json
import subprocess

from gvm.connections import TLSConnection
from gvm.errors import GvmError
from gvm.protocols.latest import Gmp
from gvm.transforms import EtreeCheckCommandTransform

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

def execute_gvm_scan(target: str, userId: str, testId: str):
    try:

        gmp = Gmp(connection=gvmConnection, transform=transform)
        gmp.authenticate(username, password)

        version = gmp.get_version()
        print(f"Greenbone OS | Openvas v{ version.find('version').text }")

        # CREATE TARGET IF NOT EXIST
        targetId = create_target(gmp, target)

        # CREATE TASK AND START SCAN
        task = create_task(gmp, testId, targetId)
        queued_task = gmp.start_task(task.attrib['id'])

        # GET CURRENT REPORT FROM THE TASK
        report = gmp.get_report(queued_task.find('report_id').text)
        result = recursive_dict(report)

        # INSERT REQUESTED REPORT ON MONGO
        scan_data = GvmScan(
            queued_task.find('report_id').text, 
            result['report']['report']['scan_run_status'],
            result['report']['report']['task']['progress'],
            result['report']['report']
        )

        # format target for filename, check if its an url or an ip
        format_target = target.split('://')[1].replace("/", "-") if "://" in target else target.replace("/", "-")
        filename = f"report-{format_target}-{testId}.json"

        check_dir = os.path.isdir(f"/opt/scanone/vuln-management/reports/openvas/{userId}")
        if not check_dir:
            print("User directory doesn't exist, creating")

            md_cmd = f"mkdir -p /opt/scanone/vuln-management/reports/openvas/{userId}"
            md_p = subprocess.Popen(md_cmd, stdout=subprocess.PIPE, shell=True)
            md_p.communicate()
        
        with open(f"/opt/scanone/vuln-management/reports/openvas/{userId}/{filename}", "w") as outfile:
            json.dump(scan_data.__dict__, outfile)


        return scan_data.__dict__
        

    except GvmError as error:
        raise error


def create_target(gmp: Gmp, target: str):

    targets = []
    targets = gmp.get_targets()
    targetExist = False
    targetId = None

    for item in targets.xpath('target'):
        if item.find('name').text == target:
            targetExist = True
            targetId = item.attrib['id']
            print(f"target { target } exists: { targetExist }")
            break

    if not targetExist:
        # CREATE TARGET WITH PORT LIST DEFAULT SETTINGS
        new_target = gmp.create_target(
            name=f'{target}', 
            hosts=[target], 
            port_list_id=port_list_id
        )

        targetId = new_target.attrib['id']
        print("target created")
    
    return targetId

def create_task(gmp: Gmp, testId: str, targetId: str):
    # pretty_print(gmp.get_scan_configs())
    # pretty_print(gmp.get_scanners())

    # CREATE TASK WITH DEFAULT SETTINGS ( Full and fast | OpenVAS Default )
    new_task = gmp.create_task(
        name=f'StrikeOne Test {testId} for Target {targetId}',
        config_id=config_id,
        target_id=targetId,
        scanner_id=scanner_id
    )
    return new_task


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
                
            # Previous single entry means it's now a list.
            elif type(retval[child.tag]) is not list:
                oldval = retval[child.tag]
                retval[child.tag] = [oldval, recurse]
                
            # Previous list entry means the list gets appended.
            else:
                oldlist = retval[child.tag]
                retval[child.tag] = oldlist + [recurse]
                
        return retval
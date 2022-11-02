from bson import ObjectId
import subprocess
import json
import copy
import os
import shutil

# CLASSES

def execute_owasp_scan(target: str, userId: str, testId: str):

    try: 

        # format target for filename, check if its an url or an ip
        format_target = target.split('://')[1].replace("/", "-") if "://" in target else target.replace("/", "-")

        # run docker scan as sudo
        filename = f"report-{format_target}-{testId}.json"

        print("Running Docker command...")

        command = f"sudo docker run --rm -v $PWD:/zap/wrk owasp/zap2docker-stable:latest zap-baseline.py -t {target} -J {filename}"    
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, cwd="/home/ubuntu")
        res = p.communicate()
        print (res)

        # json result is saved, new pending scan is created in database
        print("Copying results")

        result = open(f"/home/ubuntu/{filename}")
        owasp_result = copy.deepcopy(json.load(result))

        # check if user has scans directory and move json result there
        check_dir = os.path.isdir(f"/opt/scanone/vuln-management/reports/owasp_zap/{userId}")
        if not check_dir:
            print("User directory doesn't exist, creating")

            md_cmd = f"sudo mkdir -p /opt/scanone/vuln-management/reports/owasp_zap/{userId}"
            md_p = subprocess.Popen(md_cmd, stdout=subprocess.PIPE, shell=True)
            md_p.communicate()

        shutil.move(f"/home/ubuntu/{filename}", f"/opt/scanone/vuln-management/reports/owasp_zap/{userId}/{filename}")

        # update vulnerabilities with _id field
        for site in owasp_result['site']:
            for alert in site['alerts']:
                if '_id' not in alert:
                    alert['_id'] = ObjectId()

        return owasp_result

    except BaseException as err:
        print(f"Unexpected oops during scan! {err}, {type(err)}")
        raise err
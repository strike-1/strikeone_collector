from bson import ObjectId
import subprocess
import json
import copy
import os
import shutil

# CLASSES

def execute_owasp_scan(target: str, userId: str, testId: str):

    try: 

        print("[OWASP ZAP] Beginning OWASP ZAP scan...")

        # format target for filename, check if its an url or an ip
        format_target = target.split('://')[1].replace("/", "-") if "://" in target else target.replace("/", "-")

        # run docker scan as sudo
        filename = f"report-{format_target}-{testId}.json"

        print("[OWASP ZAP] Running Docker image...")

        command = f"sudo docker run --rm -u root -v $PWD:/zap/wrk owasp/zap2docker-stable:latest zap-baseline.py -t {target} -J {filename}"    
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, cwd="/opt/scanone/vuln-management")
        p.communicate()

        # json result is saved, new pending scan is created in database
        print("[OWASP ZAP] Copying results to .json file...")

        result = open(f"/opt/scanone/vuln-management/{filename}")
        owasp_result = copy.deepcopy(json.load(result))

        # check if user has scans directory and move json result there
        print("[OWASP ZAP] Checking if user reports directory exists...")
        check_dir = os.path.isdir(f"/opt/scanone/vuln-management/reports/owasp_zap/{userId}")

        if not check_dir:
            print("[OWASP ZAP] User directory doesn't exist, creating...")

            md_cmd = f"sudo mkdir -p /opt/scanone/vuln-management/reports/owasp_zap/{userId}"
            md_p = subprocess.Popen(md_cmd, stdout=subprocess.PIPE, shell=True)
            md_p.communicate()

        print("[OWASP ZAP] Moving scan results to reports directory...")
        shutil.move(f"/opt/scanone/vuln-management/{filename}", f"/opt/scanone/vuln-management/reports/owasp_zap/{userId}/{filename}")

        # update vulnerabilities with _id field
        for site in owasp_result['site']:
            for alert in site['alerts']:
                if '_id' not in alert:
                    alert['_id'] = ObjectId()

        print("[OWASP ZAP] Scan finished.")

        return owasp_result

    except BaseException as err:
        print(f"[OWASP ZAP] An error has occurred.")
        raise err
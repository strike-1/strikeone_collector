import argparse
from typing import List, Optional
import subprocess

from run_openvas import execute_gvm_scan
from run_owasp_zap import execute_owasp_scan

def main(userId: str, tool: str, testId: str, urls: List[str], dep_check_data: Optional[dict]):

    try:

        print("Beginning test process...\n")

        if tool == 'openvas':
            gvmResults = list()

            for url in urls:
                targetToScan = url

                if url.find("http://") != -1:
                    targetToScan = targetToScan.split("http://")[1]

                if url.find("https://") != -1:
                    targetToScan = targetToScan.split("https://")[1]

                if targetToScan.endswith("/"):
                    targetToScan = targetToScan[:-1]


                result = execute_gvm_scan(str(targetToScan), userId, testId)
                gvmResults.append(result)

            return gvmResults

        if tool == 'owasp_zap':
            owaspResults = list()

            for url in urls:
                result = execute_owasp_scan(str(url), userId, testId)
                owaspResults.append(result)

            return owaspResults
        
        if tool == 'dep_check':
            if 'project_repo' not in dep_check_data or dep_check_data['project_repo'] is None:
                raise ValueError("project_repo field doesn't exist.")
            
            if 'platform' not in dep_check_data or dep_check_data['platform'] is None:
                raise ValueError("platform field doesn't exist.")

            if 'user_repo' not in dep_check_data or dep_check_data['user_repo'] is None:
                raise ValueError("user_repo field doesn't exist.")

            if 'token' not in dep_check_data or dep_check_data['token'] is None:
                raise ValueError("token field doesn't exist.")

            command = f"sudo sh run_dep_check.sh {dep_check_data['project_repo']} {dep_check_data['platform']} {dep_check_data['user_repo']} {dep_check_data['token']} {userId} {testId}"    
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            res = p.communicate()
            print (res)

            return res

    except BaseException as err:
        print('Error occurred during test!\n', err)
        raise err

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # ARGUMENTS FROM API CALL
    parser.add_argument("-uid", "--userid", help = "user mongo id", required = "true")
    parser.add_argument("-t", "--tool", help = "tool to use", required = "true")
    parser.add_argument("-d", "-tid", "--testid", help = "testid for report filename", required = "true")
    parser.add_argument("-u", "--urls", help = "urls to scan", nargs='+')

    # DEPENDENCY CHECK 
    parser.add_argument("-dcpr", "--dcprojectrepo", help = "project repo for dependency check scan")
    parser.add_argument("-dcpl", "--dcplatform", help = "platform for dependency check scan")
    parser.add_argument("-dcur", "--dcuserrepo", help = "user repo for dependency check scan")
    parser.add_argument("-dctk", "--dctoken", help = "token for dependency check scan")

    args = parser.parse_args()

    dep_check_data = {
        "project_repo": args.dcprojectrepo,
        "platform": args.dcplatform,
        "user_repo": args.dcuserrepo,
        "token": args.dctoken,
    }
    # EXECUTE SCRIPT
    main(args.userid, args.tool, args.testid, args.urls, dep_check_data)
import argparse
from typing import List, Optional
import subprocess

from run_openvas import execute_gvm_scan
from run_owasp_zap import execute_owasp_scan
from run_nuclei import execute_nuclei

def main(userId: str, tool: str, testId: str, urls: List[str], dep_check_data: Optional[dict], nuclei_data: Optional[dict]):

    try:

        print("Beginning test process...\n")

        if tool == 'openvas':
            gvmResults = list()

            for url in urls:

                result = execute_gvm_scan(str(url), userId, testId)
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

        if tool == 'nuclei':

            for url in urls:
                list_scan = open("nuclei_scan_list.txt", 'a')
                list_scan.write(f"{url}\n")
                list_scan.close()

            result = execute_nuclei(userId, testId, nuclei_data['templates'])
            return result

    except BaseException as err:
        print('Error occurred during test!\n', err)
        raise err

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # ARGUMENTS FROM API CALL
    parser.add_argument("-uid", "--userid", help = "user mongo id", required = "true")
    parser.add_argument("-t", "--tool", help = "tool to use", required = "true")
    parser.add_argument("-d", "-tid", "--testid", help = "testid for report filename", required = "true")
    parser.add_argument("-u", "--urls", help = "urls to scan", nargs='+', required = "true")

    # DEPENDENCY CHECK 
    parser.add_argument("-dcpr", "--dcprojectrepo", help = "project repo for dependency check scan")
    parser.add_argument("-dcpl", "--dcplatform", help = "platform for dependency check scan")
    parser.add_argument("-dcur", "--dcuserrepo", help = "user repo for dependency check scan")
    parser.add_argument("-dctk", "--dctoken", help = "token for dependency check scan")

    # NUCLEI
    parser.add_argument("-nts", "--nucleitemplates", help = "nuclei templates to use", nargs='+')

    args = parser.parse_args()

    dep_check_data = {
        "project_repo": args.dcprojectrepo,
        "platform": args.dcplatform,
        "user_repo": args.dcuserrepo,
        "token": args.dctoken,
    }

    nuclei_data = {
        "templates": args.nucleitemplates
    }
    # EXECUTE SCRIPT
    main(args.userid, args.tool, args.testid, args.urls, dep_check_data, nuclei_data)
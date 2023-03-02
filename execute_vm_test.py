import argparse
from typing import List, Optional
import subprocess

from run_openvas import execute_gvm_scan
from run_owasp_zap import execute_owasp_scan
from run_nuclei import execute_nuclei

def main(userId: str, tool: str, testId: str, urls: List[str], tool_data: Optional[dict]):

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
            if 'project_url' not in tool_data or tool_data['project_url'] is None:
                raise ValueError("project_url field doesn't exist.")
            
            if 'project_name' not in tool_data or tool_data['project_name'] is None:
                raise ValueError("project_name field doesn't exist.")
            

            command = f"sudo sh run_dep_check.sh {tool_data['project_url']} {tool_data['project_name']} {userId} {testId}"    
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            res = p.communicate()
            print (res)

            return res
    
        if tool == 'nuclei':

            for url in urls:
                list_scan = open("nuclei_scan_list.txt", 'a')
                list_scan.write(f"{url}\n")
                list_scan.close()

            result = execute_nuclei(userId, testId, tool_data['templates'])
            return result

        if tool == 'gitleaks':
            if 'project_url' not in tool_data or tool_data['project_url'] is None:
                raise ValueError("project_url field doesn't exist.")
            
            if 'project_name' not in tool_data or tool_data['project_name'] is None:
                raise ValueError("project_name field doesn't exist.")
            

            command = f"sudo sh run_gitleaks.sh {tool_data['project_url']} {tool_data['project_name']} {userId} {testId}"    
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            res = p.communicate()
            return res

        if tool == 'horusec':
            if 'project_url' not in tool_data or tool_data['project_url'] is None:
                raise ValueError("project_url field doesn't exist.")
            
            if 'project_name' not in tool_data or tool_data['project_name'] is None:
                raise ValueError("project_name field doesn't exist.")
            

            command = f"sudo sh run_horusec.sh {tool_data['project_url']} {tool_data['project_name']} {userId} {testId}"    
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            res = p.communicate()
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
    parser.add_argument("-u", "--urls", help = "urls to scan", nargs='+', required = "true")

    # DEPENDENCY CHECK, GIT LEAKS
    parser.add_argument("-pu", "--projecturl", help = "project/repo url to clone")
    parser.add_argument("-pn", "--projectname", help = "project/repo name, needed to read repo contents")

    # NUCLEI
    parser.add_argument("-nts", "--nucleitemplates", help = "nuclei templates to use")

    args = parser.parse_args()

    tool_data = {
        "project_url": args.projecturl,
        "project_name": args.projectname,
        "templates": args.nucleitemplates
    }

    # EXECUTE SCRIPT
    main(args.userid, args.tool, args.testid, args.urls, tool_data)
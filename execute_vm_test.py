import argparse
import configparser
import os
from typing import List

from run_openvas import execute_gvm_scan
from run_owasp_zap import execute_owasp_scan

def main(env: str, userId: str, tool: str, date: str, urls: List[str]):

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

                result = execute_gvm_scan(str(targetToScan), userId, date)
                gvmResults.append(result)

            return gvmResults

        if tool == 'owasp_zap':
            owaspResults = list()

            for url in urls:
                result = execute_owasp_scan(str(url), userId, date)
                owaspResults.append(result)

            return owaspResults

    except BaseException as err:
        print('Error occurred during test!\n', err)
        raise err

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # ARGUMENTS FROM API CALL
    parser.add_argument("-e", "--env", help = "environment", required = "true")
    parser.add_argument("-uid", "--userid", help = "user mongo id", required = "true")
    parser.add_argument("-t", "--tool", help = "tool to use", required = "true")
    parser.add_argument("-d", "--date", help = "date for report filename", required = "true")
    parser.add_argument("-u", "--urls", help = "urls to scan", nargs='+')
    args = parser.parse_args()
    # EXECUTE SCRIPT
    main(args.env, args.userid, args.tool, args.date, args.urls)
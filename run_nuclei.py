import subprocess
import os
import json
from typing import Union

def execute_nuclei(userId: str, testId: str, templates: Union[str, None]):
    print('Running Nuclei...')

    check_dir = os.path.isdir(f"/opt/scanone/vuln-management/reports/nuclei/{userId}")
    if not check_dir:
        print("User directory doesn't exist, creating")

        md_cmd = f"mkdir -p /opt/scanone/vuln-management/reports/nuclei/{userId}"
        md_p = subprocess.Popen(md_cmd, stdout=subprocess.PIPE, shell=True)
        md_p.communicate()

    nuclei_file = f"/opt/scanone/vuln-management/reports/nuclei/{userId}/nuclei-report-{testId}.json"
    check_nuclei_file = os.path.isfile(nuclei_file)
    if not check_nuclei_file:
        with open(nuclei_file, "w") as outfile:
            pass  
   
    cwd = os.getcwd()

    cmd  = f"sudo -E nuclei -l {cwd}/nuclei_scan_list.txt -t {templates if templates is not None else 'nuclei-templates'} -json -silent -o {nuclei_file}"
    p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, cwd=f"/opt/scanone/vuln-management/reports/nuclei/{userId}" )
    results = p.communicate()[0].decode().split('\n')


    # Open url list and search for results
    with open(f'{cwd}/nuclei_scan_list.txt', 'r') as scanned_urls:
        url_list = list(scanned_urls)
        for url in url_list:
            parsed_url = url.replace("\n", "").replace("https://", "").replace("http://", "")
            url_results = []

            for result in results:
                if result is not None and len(result) > 10:
                    result_dict = json.loads(result)
                    result_host = result_dict['host']
                    if 'https://' in result_host:
                        result_host = result_host.replace('https://', '')
                    elif 'http://' in result_host:
                        result_host = result_host.replace('http://', '')
                    
                    if parsed_url == result_host: 
                        url_results.append(result_dict)

            filename_url = url.replace("\n", "").split('://')[1].replace("/", "-") if "://" in url else url.replace("/", "-")
            filename = f"report-{filename_url}-{testId}.json"            

            with open(f"/opt/scanone/vuln-management/reports/nuclei/{userId}/{filename}", "w") as outfile:
                json.dump(url_results, outfile)   

        
        os.remove("nuclei_scan_list.txt")

    return results
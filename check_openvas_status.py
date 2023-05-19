import argparse
import sys
import os
import configparser

from gvm.connections import TLSConnection
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    try:
    
        with Gmp(connection=gvmConnection, transform=transform) as gmp:
            try: 

                print(f"[OPENVAS] Attempting OpenVAS authentication...")

                gmp.authenticate(username, password)

                version = gmp.get_version()
                print(f"[OPENVAS] Greenbone OS | OpenVAS v{ version.find('version').text }")
                print(f"[OPENVAS]  Authenticated successfully.")

            except BaseException as error:
                print(f'[OPENVAS] Failed to authenticate.\n{str(error)}', file=sys.stderr)

    except BaseException as connError:
        print(f'[OPENVAS] Failed to establish connection to OpenVAS.\n{str(connError)}', file=sys.stderr)
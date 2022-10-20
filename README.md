# StrikeOne Collector
StrikeOne Collector helps users integrate third party tools to [StrikeOne Admin](https://admin.strikeone.io/login), such a OpenVAS or OWASP ZAP. The scripts are remotely executed 
through an SSH connection and are mainly used to execute tools themselves, and/or to process whatever output they might give. A configuration file (config.ini)
is also present in order to allow to further configure the tools to integrate.

You can read the documentation [here.](https://docs.strikeone.io/scan-one/vuln-management/#strikeone-collector-tool-configuration)

# Installation
Currently, **only Linux based systems are supported*. Simply create a new directory on **/opt/scanone/vuln-management** and clone the repository there. Make sure all
required modules are installed as well.

# Python edgegrid module - CONFIG for ETP CLI module
"""
Copyright 2022 Akamai Technologies, Inc. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import os
import argparse
import logging
from configparser import ConfigParser
import http.client as http_client

# 2022, new name for ETP is SIA
product_name = "Secure Internet Access Enterprise"
product_acronym = "SIA"
epilog = '''Copyright (C) Akamai Technologies, Inc\n''' \
         '''Visit http://github.com/akamai/cli-etp for detailed documentation'''
logger = logging.getLogger(__name__)


class EdgeGridConfig():

    parser = argparse.ArgumentParser(prog="akamai etp",
                                     description='Interact with ETP configuration and logs/events',
                                     epilog=epilog,
                                     formatter_class=argparse.RawTextHelpFormatter)

    def __init__(self, config_values, configuration, flags=None):
        parser = self.parser
        subparsers = parser.add_subparsers(dest="command", help='ETP object to manipulate')

        # Security Events
        event_parser = subparsers.add_parser("event", help="Fetch last events (from 30 min ago to 3 min ago)",
                                             epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        event_parser.add_argument('event_type', nargs='?', default="threat",
                                  choices=['threat', 'aup', 'dns', 'proxy', 'netcon'],
                                  help="Event type: Threat, Acceptable User "
                                       "Policy (AUP), DNS, Proxy or "
                                       "Network traffic connections details")
        event_parser.add_argument('--start', '-s', type=int, help="Start datetime (EPOCH),\nDefault is 30 min ago")
        event_parser.add_argument('--end', '-e', type=int, help="End datetime (EPOCH),\nDefault is now - 3 min")
        event_parser.add_argument('--output', '-o', help="Output file, default is stdout. Encoding is utf-8.")
        event_parser.add_argument('--tail', '-f', action='store_true', default=False,
                                  help="""Do not stop when most recent log is reached,\n"""
                                       """rather to wait for additional data to be appended\n"""
                                       """to the input. --start and --end are ignored when used.""")
        event_parser.add_argument('--poll', type=int, default=60,
                                  help="Poll frequency in seconds with --tail mode. Default is 60s")
        event_parser.add_argument('--limit', type=int, default=3*60,
                                  help="Stop the most recent fetch to now minus specified seconds, default is 3 min. "
                                       "Applicable to --tail")
        event_parser.add_argument('--concurrent', type=int, default=os.environ.get('CLIETP_FETCH_CONCURRENT', 1),
                                  help="Number of concurrent API call")

        # ETP Lists
        list_parser = subparsers.add_parser("list", help="Manage ETP security list",
                                            epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        subsub = list_parser.add_subparsers(dest="list_action", help='List action')

        listcreate = subsub.add_parser("create", help="Create a new security list")
        listcreate.add_argument('name', type=str, help='List name')
        listcreate.add_argument('description', type=str, help='List description')
        # TODO: offer choice based on ETPListCategory enum
        listcreate.add_argument('category', type=int, default=4, help='List category ID')

        listdelete = subsub.add_parser("delete", help="Delete a security list")
        listdelete.add_argument('listid', type=int, help='List ID')

        listget = subsub.add_parser("get", help="List of ETP security lists")
        listget.add_argument('listid', type=int, nargs='?', metavar='listid', help='ETP list ID')

        listadd = subsub.add_parser("add_item", help="Add one or multiple IP or host to a list",
                                    epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        listadd.add_argument('listid', type=int, metavar='listid', help='ETP list ID')
        listadd.add_argument('iporhost', metavar='IP/host', nargs='+', help='IP or FQDN to add/remove to the list')
        listadd.add_argument('--suspect', dest='suspect', default=False, action="store_true",
                             help='Item will be added as suspect confidence instead of known')

        listremove = subsub.add_parser("remove_item", help="Remove one or multiple IP or host from a list",
                                       epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        listremove.add_argument('listid', type=int, metavar='listid', help='ETP list ID')
        listremove.add_argument('iporhost', metavar='IP/host', nargs='+', help='IP or FQDN to add/remove to the list')

        listdeploy = subsub.add_parser("deploy", help="Deploy changes made to a list",
                                       epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        listdeploy.add_argument('listid', type=int, metavar='listid', help='ETP list ID')

        # IOC
        ioc_parser = subparsers.add_parser("ioc", help="Manage Indicator of Compromise (IOC) feed intelligence",
                                           epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        iocsubsub = ioc_parser.add_subparsers(dest="ioc_action", help='List action')
        ioc_info = iocsubsub.add_parser("info", help="Information on a particular internet domain")
        ioc_info.add_argument('domain', type=str, metavar='domain', help='Internet domain (eg. example.com)')
        ioc_timeseries = iocsubsub.add_parser("timeseries", help="Time Series intelligence")
        ioc_timeseries.add_argument('domain', type=str, metavar='domain', help='Internet domain (eg. example.com)')
        ioc_changes = iocsubsub.add_parser("changes", help="Information on a particular internet domain")
        ioc_changes.add_argument('domain', type=str, metavar='domain', help='Internet domain (eg. example.com)')

        # Sub-tenants
        tenant_parser = subparsers.add_parser("tenant", help="Manage ETP Account sub-tenants",
                                              epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        tenant_operation = tenant_parser.add_subparsers(dest="operation", help='Sub-tenant operation')
        tenant_operation.add_parser(
            "list", help="List all tenants in the account",
            epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        tenant_reportclient = tenant_operation.add_parser(
            "clients", help="Active ETP Client for the last 30 days per tenant",
            epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
        tenant_reportclient.add_argument('--start', '-s', type=int, help="Start datetime (EPOCH),\nDefault is 1h ago")
        tenant_reportclient.add_argument('--end', '-e', type=int, help="End datetime (EPOCH),\nDefault is now")

        # General options
        subparsers.add_parser("version", help="Display CLI ETP module version",
                              epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('--verbose', '-v', default=False, action='count', help=' Verbose mode')
        parser.add_argument('--debug', '-d', default=False, action='count', help=' Debug mode (prints HTTP headers)')
        parser.add_argument('--logfile', '-l', default=None, help='Log file, stdout if not set')

        parser.add_argument('--edgerc', '-e', default='~/.edgerc', metavar='credentials_file',
                            help=' Location of the credentials file (default is ~/.edgerc)')
        parser.add_argument('--proxy', '-p', default='', help=''' HTTP/S Proxy Host/IP and port number,'''
                                                              ''' do not use prefix (e.g. 10.0.0.1:8888)''')
        parser.add_argument('--section', '-c', default='default', metavar='credentials_file_section', action='store',
                            help=' Credentials file Section\'s name to use')
        parser.add_argument('--user-agent-prefix', dest='ua_prefix', default='Akamai-CLI', help=argparse.SUPPRESS)

        if flags:
            for argument in flags.keys():
                parser.add_argument('--' + argument, action=flags[argument])

        arguments = {}
        for argument in config_values:
            if config_values[argument]:
                if config_values[argument] == "False" or config_values[argument] == "True":
                    parser.add_argument('--' + argument, action='count')
                parser.add_argument('--' + argument)
                arguments[argument] = config_values[argument]

        try:
            args = parser.parse_args()
        except Exception:
            sys.exit()

        arguments = vars(args)

        if arguments['debug']:
            http_client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

        if "section" in arguments and arguments["section"]:
            configuration = arguments["section"]

        arguments["edgerc"] = os.path.expanduser(arguments["edgerc"])

        if os.path.isfile(arguments["edgerc"]):
            config = ConfigParser()
            config.readfp(open(arguments["edgerc"]))
            if not config.has_section(configuration):
                err_msg = "ERROR: No section named %s was found in your %s file\n" % \
                           (configuration, arguments["edgerc"])
                err_msg += "ERROR: Please generate credentials for the script functionality\n"
                err_msg += "ERROR: and run 'python gen_edgerc.py %s' to generate the credential file\n" % configuration
                sys.exit(err_msg)
            for key, value in config.items(configuration):
                # ConfigParser lowercases magically
                if key not in arguments or arguments[key] is None:
                    arguments[key] = value
                else:
                    print("Missing configuration file.  Run python gen_edgerc.py to get your credentials file "
                          "set up once you've provisioned credentials in LUNA.")
                    return None

        for option in arguments:
            setattr(self, option, arguments[option])

        self.create_base_url()

    def create_base_url(self):
        if hasattr(self, 'host'):
            self.base_url = "https://%s" % self.host

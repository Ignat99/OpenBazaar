#!./env/bin/python
# OpenBazaar's launcher script.
# Authors: Angel Leon (@gubatron)

import os
import argparse
import multiprocessing
from openbazaar_daemon import node_starter
from setup_db import setup_db
from network_util import init_aditional_STUN_servers, check_NAT_status


def is_osx():
    return os.uname()[0].startswith('Darwin')


def getDefaults():
    return {'SERVER_PORT': 12345,
            'LOG_DIR': 'logs',
            'LOG_FILE': 'production.log',
            'DB_DIR': 'db',
            'DB_FILE': 'ob.db',
            'DEV_DB_FILE': 'ob-dev-{0}.db',
            'DEVELOPMENT': False,
            'DEV_NODES': 3,
            'SEED_MODE': False,
            'SEED_HOSTNAMES': 'seed.openbazaar.org seed2.openbazaar.org seed.openlabs.co us.seed.bizarre.company eu.seed.bizarre.company'.split(),
            'DISABLE_UPNP': False,
            'DISABLE_STUN_CHECK': False,
            'DISABLE_OPEN_DEFAULT_WEBBROWSER': False,
            'DISABLE_SQLITE_CRYPT': False,
            'LOG_LEVEL': 10,  # CRITICAL=50, ERROR=40, WARNING=30, DEBUG=10, NOTSET=0
            'NODES': 3,
            'HTTP_IP': '127.0.0.1',
            'HTTP_PORT': -1,
            'BITMESSAGE_USER': None,
            'BITMESSAGE_PASS': None,
            'BITMESSAGE_PORT': -1,
            'ENABLE_IP_CHECKER': False,
            'CONFIG_FILE': None
            }


def initArgumentParser(defaults):

    parser = argparse.ArgumentParser(usage=usage(),
                                     add_help=False)

    parser.add_argument('-i', '--server-public-ip', help='Server Public IP')

    parser.add_argument('-p', '--server-public-port', '--my-market-port',
                        default=defaults['SERVER_PORT'],
                        type=int,
                        help='Server Public Port (default 12345)')

    parser.add_argument('-k', '--http-ip', '--web-ip',
                        default=defaults['HTTP_IP'],
                        help='Web Interface IP (default 127.0.0.1;' +
                        ' use 0.0.0.0 for any)')

    parser.add_argument('-q', '--web-port', '--http-port',
                        type=int, default=defaults['HTTP_PORT'],
                        help='Web Interface Port (default random)')

    parser.add_argument('-l', '--log',
                        default=defaults['LOG_DIR'] + os.sep + defaults['LOG_FILE'],
                        help='Log File Path')

    parser.add_argument('--log-level',
                        default=defaults['LOG_LEVEL'],
                        help='Log Level (Default: 10 - DEBUG')

    parser.add_argument('-d', '--development-mode',
                        action='store_true',
                        help='Development mode')

    parser.add_argument("--db-path", "--database",
                        default=defaults['DB_DIR'] + os.sep + defaults['DB_FILE'],
                        help="Database filename")

    parser.add_argument('-n', '--dev-nodes',
                        type=int,
                        default=-1,
                        help='Number of Dev nodes to start up')

    parser.add_argument('--bitmessage-user', '--bmuser',
                        default=defaults['BITMESSAGE_USER'],
                        help='Bitmessage API username')

    parser.add_argument('--bitmessage-pass', '--bmpass',
                        default=defaults['BITMESSAGE_PASS'],
                        help='Bitmessage API password')

    parser.add_argument('--bitmessage-port', '--bmport',
                        type=int,
                        default=defaults['BITMESSAGE_PORT'],
                        help='Bitmessage API port (eg: 8444)')

    parser.add_argument('-u', '--market-id',
                        help='Market ID')

    parser.add_argument('-j', '--disable-upnp',
                        action='store_true',
                        default=defaults['DISABLE_UPNP'],
                        help='Disable automatic UPnP port mappings')

    parser.add_argument('--disable-stun-check',
                        action='store_true',
                        default=defaults['DISABLE_STUN_CHECK'],
                        help='Disable automatic port setting via STUN servers (NAT Punching attempt)')

    parser.add_argument('-S', '--seed-mode',
                        action='store_true',
                        default=defaults['SEED_MODE'],
                        help='Enable Seed Mode')

    parser.add_argument('-s', '--seeds',
                        nargs='*',
                        default=[])

    parser.add_argument('--disable-open-browser',
                        action='store_true',
                        default=defaults['DISABLE_OPEN_DEFAULT_WEBBROWSER'],
                        help='Don\'t open preferred web browser ' +
                        'automatically on start')

    parser.add_argument("--disable-sqlite-crypt",
                        action="store_true",
                        help="Disable encryption on sqlite database")

    parser.add_argument('--config-file',
                        default=defaults['CONFIG_FILE'],
                        help='Disk path to an OpenBazaar configuration file')

    parser.add_argument('--enable-ip-checker',
                        default=defaults['ENABLE_IP_CHECKER'])

    parser.add_argument('command')
    return parser


def usage():
    return """
openbazaar [options] <command>

    COMMANDS
        start            Start OpenBazaar
        stop             Stop OpenBazaar

    OPTIONS
    -i, --server-public-ip <ip address>
        Server public IP

    -p, --server-public-port, --my-market-port <port number>
        Server public (P2P) port (default 12345)

    -k, --http-ip, --web-ip <ip address>
        Web interface IP (default 127.0.0.1; use 0.0.0.0 for any)

    -q, --web-port, --http-port <port number>
        Web interface port (-1 = random by default)

    -l, --log <file path>
        Log file path (default 'logs/production.log')

    --log-level <level>
        Log verbosity level (default: 10 - DEBUG)
        Expected <level> values are:
           0 - NOT SET
          10 - DEBUG
          20 - INFO
          30 - WARNING
          40 - ERROR
          50 - CRITICAL

    -d, --development-mode
        Enable development mode

    -n, --dev-nodes
        Number of dev nodes to start up

    --database
        Database filename. (default 'db/od.db')

    --disable-sqlite-crypt
        Disable encryption on sqlite database

    --bitmessage-user, --bmuser
        Bitmessage API username

    --bitmessage-pass, --bmpass
        Bitmessage API password

    --bitmessage-port, --bmport
        Bitmessage API port

    -u, --market-id
        Market ID

    -j, --disable-upnp
        Disable automatic UPnP port mappings

    --disable-stun-check
        Disable automatic port setting via STUN servers (NAT Punching attempt)

    -S, --seed-mode
        Enable seed mode

    --disable-open-browser
        Don't open preferred web browser automatically on start

    --config-file
        Disk path to an OpenBazaar configuration file

    --enable-ip-checker
        Enable periodic IP address checking. In case you expect your IP to change rapidly.

"""


def create_openbazaar_contexts(arguments, defaults, nat_status):
    """
    This method will return a list of OpenBazaarContext objects.
    If we are on production mode, the list will contain a
    single OpenBazaarContext object based on the arguments passed.

    If a configuration file is passed, settings from the configuration
    file will be read first, and whatever other parameters have been
    passed via the command line will override the settings on the
    configuration file.
    """
    # TODO: if a --config file has been specified
    # first load config values from it
    # then override the rest that has been passed
    # through the command line.

    my_market_ip = ''
    if arguments.server_public_ip is not None:
        my_market_ip = arguments.server_public_ip
    elif nat_status is not None:
        print nat_status
        my_market_ip = nat_status['external_ip']

    # market port
    my_market_port = defaults['SERVER_PORT']
    if arguments.server_public_port is not None and arguments.server_public_port != my_market_port:
        my_market_port = arguments.server_public_port
    elif nat_status is not None:
        # override the port for p2p communications with the one
        # obtained from the STUN server.
        my_market_port = nat_status['external_port']

    # http ip
    http_ip = defaults['HTTP_IP']
    if arguments.http_ip is not None:
        http_ip = arguments.http_ip

    # http port
    http_port = defaults['HTTP_PORT']
    if arguments.web_port is not None and arguments.web_port != http_port:
        http_port = arguments.web_port

    # create default LOG_DIR if not present
    if not os.path.exists(defaults['LOG_DIR']):
        os.makedirs(defaults['LOG_DIR'], 0755)

    # log path
    log_path = defaults['LOG_DIR'] + os.sep + defaults['LOG_FILE']
    if arguments.log is not None and arguments.log != log_path:
        log_path = arguments.log

    # log level
    log_level = defaults['LOG_LEVEL']
    if arguments.log_level is not None and arguments.log_level != log_level:
        log_level = arguments.log_level

    # market id
    market_id = None
    if arguments.market_id is not None:
        market_id = arguments.market_id

    # bm user
    bm_user = defaults['BITMESSAGE_USER']
    if arguments.bitmessage_user is not None and arguments.bitmessage_user != bm_user:
        bm_user = arguments.bitmessage_user

    # bm pass
    bm_pass = defaults['BITMESSAGE_PASS']
    if arguments.bitmessage_pass is not None and arguments.bitmessage_pass != bm_pass:
        bm_pass = arguments.bitmessage_pass

    # bm port
    bm_port = defaults['BITMESSAGE_PORT']
    if arguments.bitmessage_port is not None and arguments.bitmessage_port != bm_port:
        bm_port = arguments.bitmessage_port

    # seed_peers
    seed_peers = defaults['SEED_HOSTNAMES']
    if len(arguments.seeds) > 0:
        seed_peers = seed_peers + arguments.seeds

    # seed_mode
    seed_mode = False
    if arguments.seed_mode:
        seed_mode = True

    # dev_mode
    dev_mode = defaults['DEVELOPMENT']
    if arguments.development_mode != dev_mode:
        dev_mode = arguments.development_mode

    # dev nodes
    dev_nodes = -1
    if arguments.development_mode:
        dev_nodes = defaults['DEV_NODES']
        if arguments.dev_nodes != dev_nodes:
            dev_nodes = arguments.dev_nodes

    # database
    if not os.path.exists(defaults['DB_DIR']):
        os.makedirs(defaults['DB_DIR'], 0755)

    db_path = defaults['DB_DIR'] + os.sep + defaults['DB_FILE']
    if arguments.db_path != db_path:
        db_path = arguments.db_path

    # disable upnp
    disable_upnp = defaults['DISABLE_UPNP']
    if arguments.disable_upnp:
        disable_upnp = True

    disable_stun_check = defaults['DISABLE_STUN_CHECK']
    if arguments.disable_stun_check:
        disable_stun_check = True

    # disable open browser
    disable_open_browser = defaults['DISABLE_OPEN_DEFAULT_WEBBROWSER']
    if arguments.disable_open_browser:
        disable_open_browser = True

    # disable sqlite crypt
    disable_sqlite_crypt = defaults['DISABLE_SQLITE_CRYPT']
    if arguments.disable_sqlite_crypt != disable_sqlite_crypt:
        disable_sqlite_crypt = True

    # enable ip checker
    enable_ip_checker = defaults['ENABLE_IP_CHECKER']
    if arguments.enable_ip_checker:
        enable_ip_checker = True

    from openbazaar_daemon import OpenBazaarContext   # yes, please don't move this import from here.
    ob_ctxs = []

    if not dev_mode:
        # we return a list of a single element, a production node.
        ob_ctxs.append(OpenBazaarContext(nat_status,
                                         my_market_ip,
                                         my_market_port,
                                         http_ip,
                                         http_port,
                                         db_path,
                                         log_path,
                                         log_level,
                                         market_id,
                                         bm_user,
                                         bm_pass,
                                         bm_port,
                                         seed_peers,
                                         seed_mode,
                                         dev_mode,
                                         dev_nodes,
                                         disable_upnp,
                                         disable_stun_check,
                                         disable_open_browser,
                                         disable_sqlite_crypt,
                                         enable_ip_checker))
    elif dev_nodes > 0:
        # we create a different OpenBazaarContext object for each development node.
        i = 1
        db_path = defaults['DB_DIR'] + os.sep + defaults['DEV_DB_FILE']
        db_dirname = os.path.dirname(db_path)
        while i <= dev_nodes:
            db_path = db_dirname + os.path.sep + defaults['DEV_DB_FILE'].format(i)
            ob_ctxs.append(OpenBazaarContext(nat_status,
                                             my_market_ip,
                                             my_market_port,
                                             http_ip,
                                             http_port,
                                             db_path,
                                             log_path,
                                             log_level,
                                             market_id,
                                             bm_user,
                                             bm_pass,
                                             bm_port,
                                             seed_peers,
                                             seed_mode,
                                             dev_mode,
                                             dev_nodes,
                                             disable_upnp,
                                             disable_stun_check,
                                             disable_open_browser,
                                             disable_sqlite_crypt,
                                             enable_ip_checker))
            i = i + 1

    return ob_ctxs


def ensure_database_setup(ob_ctx, defaults):
    db_path = ob_ctx.db_path
    default_db_path = defaults['DB_DIR'] + os.sep + defaults['DB_FILE']
    default_dev_db_path = defaults['DB_DIR'] + os.sep + defaults['DEV_DB_FILE']

    if ob_ctx.dev_mode and db_path == default_db_path:
        # override default db_path to developer database path.
        db_path = default_dev_db_path

    # make sure the folder exists wherever it is
    db_dirname = os.path.dirname(db_path)
    if not os.path.exists(db_dirname):
        os.makedirs(db_dirname, 0755)

    if not os.path.exists(db_path):
        # setup the database if file not there.
        print "[openbazaar] bootstrapping database ", os.path.basename(db_path)
        setup_db(db_path)
        print "[openbazaar] database setup completed\n"


def start(arguments, defaults):
    init_aditional_STUN_servers()

    # Turn off checks that don't make sense in development mode
    if arguments.development_mode:
        print "DEVELOPMENT MODE! (Disable STUN check and UPnP mappings)"
        arguments.disable_stun_check = True
        arguments.disable_upnp = True

    # Try to get NAT escape UDP port
    nat_status = None
    if not arguments.development_mode or not arguments.disable_stun_check:
        print "Checking NAT Status..."
        nat_status = check_NAT_status()

    ob_ctxs = create_openbazaar_contexts(arguments, defaults, nat_status)
    for ob_ctx in ob_ctxs:
        ensure_database_setup(ob_ctx, defaults)

    print "About to start father process"
    p = multiprocessing.Process(target=node_starter, args=(ob_ctxs,))
    # p.daemon = True
    p.start()


def main():
    defaults = getDefaults()
    parser = initArgumentParser(defaults)
    arguments = parser.parse_args()

    print "Command: '" + arguments.command + "'"

    if arguments.command == 'start':
        start(arguments, defaults)
    elif arguments.command == 'stop':
        pass
    elif arguments.command == 'status':
        pass
    else:
        print "\n[openbazaar] Invalid command '" + arguments.command + "'"
        print "[openbazaar] Valid commands are 'start', 'stop', 'status'."
        print "\n[openbazaar] Please try again.\n"

if __name__ == '__main__':
    main()

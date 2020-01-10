import os
import sys
import getopt
import datetime
import logging
import pysftp
from ftplib import FTP

def arguments(argv=sys.argv):
    argIn = {}
    try:
        opts, args = getopt.getopt(argv[1:], "h:i:o:u:s:M:m:O:p:P:U:H:C:", ["checkin=", "checkout=", "suburb=", "state=", "maxprice=", "minprice=", "outfile=", "pages=", "path=", "host=", "username=", "password="])
        for opt, arg in opts:
            if opt == "-h":
                print(" ".join(str(val) for val in argv[:1]) + " -i <checkin date> -o <checkout date> -u <suburb> -s <state> -M <max price> -m <min price> -O <out file> -p <pages> -P <path> -H <host> -C <password> -U <username>,")
                sys.exit()
            elif opt in ("-i", "--checkin"):
                argIn['checkin'] = arg
            elif opt in ("-o", "--checkout"):
                argIn['checkout'] = arg
            elif opt in ("-u", "--suburb"):
                argIn['suburb'] = arg
            elif opt in ("-s", "--state"):
                argIn['state'] = arg
            elif opt in ("-M", "--maxprice"):
                argIn['maxprice'] = arg.strip().lower()
            elif opt in ("-m", "--minprice"):
                argIn['minprice'] = arg.strip().lower()
            elif opt in ("-O", "--outfile"):
                argIn['outfile'] = arg
            elif opt in ("-p", "--pages"):
                argIn['pages'] = int(arg)
            elif opt in ("-P", "--path"):
                argIn['path'] = arg
            elif opt in ("-H", "--host"):
                argIn['host'] = arg
            elif opt in ("-U", "--username"):
                argIn['username'] = arg
            elif opt in ("-C", "--password"):
                argIn['password'] = arg

        if 'checkin' not in argIn:
            argIn['checkin'] = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if 'checkout' not in argIn:
            argIn['checkout'] = (datetime.datetime.strptime(argIn['checkin'], "%Y-%m-%d") + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if 'state' not in argIn:
            argIn['state'] = "Guanajuato"
        if 'suburb' not in argIn:
            argIn['suburb'] = "Guanajuato"
        if 'minprice' not in argIn:
            argIn['minprice'] = None
        if 'maxprice' not in argIn:
            argIn['maxprice'] = None
        if 'pages' not in argIn:
            argIn['pages'] = None
        if 'path' not in argIn:
            argIn['path'] = os.getcwd()
        if 'host' not in argIn:
            argIn['host'] = "www.ia-ugto.mx"
        if 'username' not in argIn:
            argIn['username'] = "iaugtomx"
        if 'password' not in argIn:
            argIn['password'] = "74g1k7GicM"

    except getopt.GetoptError:
        print(" ".join(str(val)
                       for val in argv[
                                  :1]) + " -i <checkin date> -o <checkout date> -u <suburb> -s <state> -M <max price> -m <min price> -O <out file> -p <pages> -P <path> -H <host> -C <password> -U <username>,")
        sys.exit(2)
    except:
        logging.error("Exception occurred", exc_info=True)
        sys.exit(2)

    return argIn

def save_file_ftp(host, username, password, file, src_path, dest_path):
    try:
        with FTP(host=host) as ftp:
            login_status = ftp.login(user=username, passwd=password)
            if "OK" not in login_status:
                sys.exit(2)

            ftp.cwd(dest_path)
            fp = open(os.path.join(src_path, file), 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(file), fp, 1024)
            ftp.close()
    except:
        logging.error("Exception occurred", exc_info=True)

def save_file_sftp(host, username, password, file, src_path, dest_path):
    try:
        with pysftp.Connection(host, username=username, password=password) as sftp:
            with sftp.cd(dest_path):
                sftp.put(os.path.join(src_path, file))
    except:
        logging.error("Exception occurred", exc_info=True)
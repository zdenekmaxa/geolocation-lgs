"""
Process logs from lgping (nginx files).
Get and store unique IP addresses.
Query ipinfo.io service to get matching geo-locations for IP addresses.
Generate output JSON/js file to used in a page to display on maps.

"""

import fnmatch
import os
import re
import pycurl
import json
from StringIO import StringIO


INPUT_FILES_MASK = "access-lgping.log*"
OUTPUT_FILE_IPS = "unique_ip_addresses.txt"
OUTPUT_FINAL = "info.js"


def get_files():
    r = []
    for f in os.listdir('.'):
        if fnmatch.fnmatch(f, INPUT_FILES_MASK):
            print "Matching: '%s'" % f
            r.append(f)
    return r


def get_unique_ip_addresses(files_list):
    """
    Assumes format:
        aaa.bbb.ccc.ddd - - [02/Jan/2017:03:57:04 +0100] "HEAD /lgping HTTP/1.1" 200 0 "-" "curl/7.35.0"

    """
    ips = set()
    # IP address at the beginning of a line
    rc = re.compile("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}")
    counter = 0
    for f in files_list:
        print "Processing '%s' ..." % f
        with open(f, 'r') as ff:
            for line in ff:
                m = rc.match(line)
                if m:
                    ip = m.group()
                    print "Adding IP address: %s ..." % ip
                    ips.add(ip)
                counter += 1
    print "Processed %s log lines." % counter
    return ips


def get_locations_for_ip_addresses(ip_addresses):
    r = []
    for ip in ip_addresses:
        # returns 51.4000,0.0500
        url = "ipinfo.io/%s/loc" % ip
        print "Querrying %s ..." % url
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        body = buffer.getvalue().strip().split(',')
        lat, lon = buffer.getvalue().strip().split(',')
        d = dict(ip=ip, lat=float(lat), lon=float(lon))
        r.append(d)
    return r


def get_ip_addresses_from_log_files():
    files_list = get_files()
    ips = get_unique_ip_addresses(files_list)
    print "Found %s unique IP address." % len(ips)
    output = file(OUTPUT_FILE_IPS, 'w')
    for ip in ips:
        output.write("%s\n" % ip)
    output.close()
    print "IP addresses written in %s" % OUTPUT_FILE_IPS
    return ips


def read_ip_addresses_from_output_file():
    ips = set()
    with open(OUTPUT_FILE_IPS, 'r') as ip_file:
        for ip in ip_file:
            ip = ip.strip()
            print ip
            ips.add(ip)
    print "Read %s IP addresses." % len(ips)
    return ips


def main():
    # ips = get_ip_addresses_from_log_files()
    ips = read_ip_addresses_from_output_file()
    all_data = get_locations_for_ip_addresses(ips)
    final = open(OUTPUT_FINAL, 'w')
    final.write("var data = \n");
    final.write(str(all_data))
    final.write("\n;\n")
    final.close()


if __name__ == "__main__":
    main()


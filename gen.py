#!/usr/bin/env python3
''' A python script, made to simplify the process of generating a CloudFlare DDNS update script.
By pcchou, Released under the MIT License. '''

import json
import os
from time import time, sleep
from urllib import request, parse


def subdomain_selector(def_a_records):
    """ A function for the users to select A record. """
    filtered_a_records = []
    for (index, item) in enumerate([
            record["name"] for record in def_a_records]):
        filtered_a_records.append([index, item])
    print("")
    print("Please select your desired A record:")
    print("#   Name          \n"
          "------------------")
    for host in filtered_a_records:
        print(str(host[0]) + " "*(3 - len(str(host[0]))) + " " + host[1])
    print("")
    answer = int(input("Number (#): "))
    if answer in [filtered_a_records[number][0] for number, _ in enumerate(filtered_a_records)]:
        return A_RECORDS[answer]["name"], A_RECORDS[answer]["rec_id"], A_RECORDS[answer]["ttl"]
    else:
        raise ValueError("Not a vaild answer.")


CF_TOKEN = str(input("Please input your CloudFlare API Token. \n"
                     "You can get yours from your CloudFlare account settings page: "
                     "https://www.cloudflare.com/a/account/my-account. \n"
                     "CloudFlare API Token: ").strip().lower())
CF_EMAIL = str(input("Please input your CloudFlare account e-mail: ").strip().lower())
CF_DOMAIN = str(input(
    "Please input your CloudFlare target domain (not the subdomain): ").strip().lower())
print("\n"
      "Retrieving informations...")

try:
    PARSED_LIST_REQ = json.loads(request.urlopen(
        request.Request("https://www.cloudflare.com/api_json.html", parse.urlencode({
            "a": "rec_load_all",
            "z": CF_DOMAIN,
            "tkn": CF_TOKEN,
            "email": CF_EMAIL}).encode('utf-8'))).read().decode())
except ConnectionError:
    raise ConnectionError("You need a internet connection.")

if not PARSED_LIST_REQ["result"] == "success":
    raise ValueError("You're credentials are incorrect.")


A_RECORDS = []
for record in PARSED_LIST_REQ["response"]["recs"]["objs"]:
    if record["type"] == "A":
        A_RECORDS.append(record)

CF_ID = ""
while not CF_ID:
    try:
        CF_NAME, CF_ID, CF_TTL = subdomain_selector(A_RECORDS)
    except ValueError:
        print("Not a vaild answer.\n")

SCRIPT_PATH = "/tmp/cf-ddns-" + CF_NAME + "-" + str(int(time())) + ".sh"
SCRIPT = open(SCRIPT_PATH, "w")

SCRIPT_LIST = [
    "#!/bin/bash",
    "ip=`curl -s http://icanhazip.com`",
    "if [ -f /tmp/.cf-oldip ]; then",
    "    oldip=`cat /tmp/.cf-oldip`",
    "else",
    "    echo 'Old IP file not found, creating one.'",
    "    oldip =''",
    "fi",
    "if [[ \"$ip\" == \"$oldip\" ]]; then",
    "    echo 'IP unchanged, do nothing.'",
    "else",
    "    echo 'Updated IP to '\"$ip\"'.'",
    "    echo $ip > /tmp/.cf-oldip",
    ("    curl -s https://www.cloudflare.com/api_json.html"
     " -d 'a=rec_edit' -d 'type=A'"
     " -d \"content=$ip\""
     " -d 'tkn=" + CF_TOKEN + "'"
     " -d 'email=" + CF_EMAIL + "'"
     " -d 'z=" + CF_DOMAIN + "'"
     " -d 'name=" + CF_NAME + "'"
     " -d 'id=" + CF_ID + "'"
     " -d 'ttl=" + CF_TTL + "'"
     "|perl -pe 's/.*\"result\":\"(.*?)\".*/$1/'"),
    "fi"]

for line in SCRIPT_LIST:
    SCRIPT.write("%s\n" % line)
os.chmod(SCRIPT_PATH, 0o0755)
sleep(2)

print("\n")
print("Done!\n"
      "Script file written to \"" + SCRIPT_PATH + "\".\n")

print("You will need to move it to a persistent PATH directory (eg. /usr/local/bin/),\n"
      "Execute this command with the root user: \n"
      "\"mv \"" + SCRIPT_PATH + "\" /usr/local/bin/cf-ddns.sh\n\"")

print("You will also need to set it to be run automatically, by setting it in your crontab.\n"
      "Run \"crontab -e\" and add this line to the end:\n"
      "'*/5 * * * /usr/local/bin/cf-ddns.sh'\n"
      "This can make your system run the script every five minutes.\n")

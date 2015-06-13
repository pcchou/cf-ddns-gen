#!/usr/bin/env python3
''' A python script, made to simplify the process of generating a CloudFlare DDNS update script.
By pcchou, Released under the MIT License. '''

import json
import os
from time import time, sleep

import requests
from tabulate import tabulate


def subdomain_selector(filtered_a_records):
    double_filtered_a_records = []
    for (index, item) in enumerate(
           [record["name"] for record in filtered_a_records]):
        double_filtered_a_records.append([index, item])
    print("")
    print("Please select your desired A record:")
    print(tabulate(double_filtered_a_records, headers=["#", "Name"]))
    print("")
    answer = int(input("Number (#): "))
    if answer in [double_filtered_a_records[number][0] for number,_ in enumerate(double_filtered_a_records)]:
        return filtered_a_records[answer]["name"], filtered_a_records[answer]["rec_id"], filtered_a_records[answer]["ttl"]
    else:
        raise ValueError("Not a vaild answer.")


CF_TOKEN = str(input("Please input your CloudFlare API Token. \n"
                     "You can get yours from your CloudFlare account settings page: "
                     "https://www.cloudflare.com/a/account/my-account. \n"
                     "CloudFlare API Token: ").strip().lower())
CF_EMAIL = str(input("Please input your CloudFlare account e-mail: ").strip().lower())
CF_DOMAIN = str(input("Please input your CloudFlare target domain (not the subdomain): ").strip().lower())
print("\n"
      "Retrieving informations...")

try:
    parsed_list_req = json.loads(
            requests.get("https://www.cloudflare.com/api_json.html", params={
                    "a": "rec_load_all",
                    "z": CF_DOMAIN,
                    "tkn": CF_TOKEN,
                    "email": CF_EMAIL}).text)
except ConnectionError:
    raise ConnectionError("You need a internet connection.")

if not parsed_list_req["result"] == "success":
    raise ValueError("You're credentials are incorrect.")


a_records = []
for record in parsed_list_req["response"]["recs"]["objs"]:
    if record["type"] == "A":
        a_records.append(record)

filtered_a_records = []
for item in (
        [{key: record[key] for key in ["name", "rec_id", "ttl"]} for record in a_records]):
    filtered_a_records.append(item)

cf_id = ""
while not cf_id:
    try:
        cf_name, cf_id, cf_ttl = subdomain_selector(filtered_a_records)
    except ValueError:
        print("Not a vaild answer.\n")

script_path = "/tmp/cf-ddns-" + cf_name + "-" + str(int(time())) + ".sh"
script = open(script_path, "w")

script_list = [
        "#!/bin/bash",
        "ip=`curl -s http://icanhazip.com`",
        "if [ -f /tmp/.cf-oldip ]; then",
        "    oldip=`cat /tmp/.cf-oldip`",
        "else",
        "    echo 'Old IP file not found, creating one.'",
        "    oldip=''",
        "fi",
        "if [ \"$ip\" == \"$oldip\"]; then",
        "    echo 'IP unchanged, do nothing.'",
        "else",
        "    echo 'Updated IP to '\"$ip\"'.'",
        "    echo $ip > /tmp/.cf-oldip",
        ("    curl https://www.cloudflare.com/api_json.html"
         " -d 'a=rec_edit' -d 'type=A'"
         " -d \"content=$ip\""
         " -d 'tkn=" + CF_TOKEN + "'"
         " -d 'email=" + CF_EMAIL + "'"
         " -d 'z=" + CF_DOMAIN + "'"
         " -d 'name=" + cf_name + "'"
         " -d 'id=" + cf_id + "'"
         " -d 'ttl=" + cf_ttl + "'"),
        "fi"]

for line in script_list:
    script.write("%s\n" % line)
os.chmod(script_path, 0o0755)
sleep(2)

print("\n")
print("Done!\n"
      "Script file written to \"" + script_path + "\".\n")

print("You will need to move it to a persistent PATH directory (eg. /usr/local/bin/),\n"
      "Execute this command with the root user: \n"
      "mv \"" + script_path + "\" /usr/local/bin/cf-ddns.sh\n")

print("You will also need to set it to be run automatically, by setting it in your crontab.\n"
      "Run \"crontab -e\" and add this line to the end:\n"
      "*/5 * * * /usr/local/bin/cf-ddns.sh\n"
      "This can make your system run the script every five minutes.\n")

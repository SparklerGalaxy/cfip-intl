import random
import time
import json
import requests
import os
import traceback
from dns.qCloud import QcloudApiv3
from dns.aliyun import AliApi
from dns.huawei import HuaWeiApi
import sys

try:
    DOMAINS = json.loads(os.environ["DOMAINS"])
    SECRETID = os.environ["SECRETID"]
    SECRETKEY = os.environ["SECRETKEY"]
except KeyError as e:
    print(f"Missing required environment variable: {e}")
    sys.exit(1)

AFFECT_NUM = 2
DNS_SERVER = 2
REGION_HW = 'cn-east-3'
TTL = 600
RECORD_TYPE = sys.argv[1] if len(sys.argv) >= 2 else "A"

class CloudFlareIPManager:
    @staticmethod
    def get_optimized_ips():
        try:
            response = requests.get('https://api.vvhan.com/tool/cf_ip', headers={'Content-Type': 'application/json'})
            print(response.json())
            if response.status_code != 200 or not response.json().get("success"):
                return None
            
            ip_type = "v4" if RECORD_TYPE == "A" else "v6"
            data = response.json()["data"][ip_type]
            
            ips = {}
            for carrier in ["CM", "CU", "CT"]:
                if carrier in data:
                    sorted_ips = sorted(data[carrier], key=lambda x: (-x["speed"], x["latency"]))
                    ips[carrier] = [{"ip": ip["ip"]} for ip in sorted_ips[:3]]
            return {"info": ips}
        except Exception:
            return None

class DNSUpdater:
    def __init__(self, cloud):
        self.cloud = cloud
        self.lines_map = {"CM": "移动", "CU": "联通", "CT": "电信", "AB": "境外", "DEF": "默认"}

    def _process_records(self, records):
        categorized = {"CM": [], "CU": [], "CT": [], "AB": [], "DEF": []}
        for record in records:
            line = record["line"]
            if line in self.lines_map.values():
                line_key = next(k for k, v in self.lines_map.items() if v == line)
                categorized[line_key].append({
                    "recordId": record["id"],
                    "value": record["value"]
                })
        return categorized

    def _handle_dns_change(self, domain, sub_domain, line_key, current_records, candidate_ips):
        line_name = self.lines_map[line_key]
        create_num = AFFECT_NUM - len(current_records)

        for _ in range(abs(create_num)):
            if not candidate_ips:
                break
            cf_ip = candidate_ips.pop(random.randint(0, len(candidate_ips)-1))["ip"]
            if any(cf_ip == r["value"] for r in current_records):
                continue

            if create_num > 0:
                ret = self.cloud.create_record(domain, sub_domain, cf_ip, RECORD_TYPE, line_name, TTL)
            else:
                record = current_records.pop(0)
                ret = self.cloud.change_record(domain, record["recordId"], sub_domain, cf_ip, RECORD_TYPE, line_name, TTL)

            self._log_result(ret, domain, sub_domain, line_name, cf_ip, "CREATE" if create_num > 0 else "CHANGE")

    def _log_result(self, ret, domain, sub_domain, line, value, action):
        status = "SUCCESS" if DNS_SERVER != 1 or ret.get("code", 1) == 0 else "ERROR"
        message = ret.get("message", "") if status == "ERROR" else ""
        print(f"{action} DNS {status}: ----Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}----DOMAIN: {domain}----SUBDOMAIN: {sub_domain}----RECORDLINE: {line}----VALUE: {value}{f'----MESSAGE: {message}' if message else ''}")

    def update_dns_records(self):
        try:
            cf_ips = CloudFlareIPManager.get_optimized_ips()
            if not cf_ips:
                return
            for domain, sub_domains in DOMAINS.items():
                for sub_domain, lines in sub_domains.items():
                    ret = self.cloud.get_record(domain, 100, sub_domain, RECORD_TYPE)

                    print(f"Retrieved records: {ret}")
                    print(f"Retrieved records: {ret.get('data', {})}")
                    print(f"Retrieved records: {ret.get('data', {}).get('records', [])}")


                    if DNS_SERVER == 1 and "Free" in ret["data"]["domain"]["grade"]:
                        global AFFECT_NUM
                        AFFECT_NUM = min(AFFECT_NUM, 2)

                    categorized = self._process_records(ret["data"]["records"])
                    for line in lines:
                        self._handle_dns_change(
                            domain, sub_domain, line,
                            categorized.get(line, []),
                            cf_ips["info"].get(line, []).copy()
                        )
        except Exception:
            print(f"CHANGE DNS ERROR: ----Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}----MESSAGE: {traceback.format_exc()}")

def main():
    cloud = None
    if DNS_SERVER == 1:
        cloud = QcloudApiv3(SECRETID, SECRETKEY)
    elif DNS_SERVER == 2:
        cloud = AliApi(SECRETID, SECRETKEY)
    elif DNS_SERVER == 3:
        cloud = HuaWeiApi(SECRETID, SECRETKEY, REGION_HW)
    if cloud:
        updater = DNSUpdater(cloud)
        updater.update_dns_records()

if __name__ == '__main__':
    main()

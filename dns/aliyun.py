#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
# Reference: https://help.aliyun.com/document_detail/29776.html?spm=a2c4g.11186623.2.38.3fc33efexrOFkT
# REGION: https://help.aliyun.com/document_detail/198326.html
import json
import logging
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CreConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


rc_format = 'json'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AliApi():
    def __init__(self, ACCESSID, SECRETKEY):
        self.access_key_id = ACCESSID
        self.access_key_secret = SECRETKEY

    def create_client(self) -> Alidns20150109Client:
        try:
            credentialsConfig = CreConfig(
                # 凭证类型。
                type='access_key',
                # 设置为AccessKey ID值。
                access_key_id=self.access_key_id,
                # 设置为AccessKey Secret值。
                access_key_secret=self.access_key_secret,
            )
            credentialClient = CredClient(credentialsConfig)
            
            dnsConfig = open_api_models.Config(
                credential=credentialClient
            )
            dnsConfig.endpoint = f'alidns.cn-hongkong.aliyuncs.com'
            logging.info("Client created successfully")
            return Alidns20150109Client(dnsConfig)
        except Exception as e:
            logging.error(f"Failed to create client: {str(e)}")
            raise

    def del_record(self, domain, record):
        try:
            client = self.create_client()
            delete_domain_record_request = alidns_20150109_models.DeleteDomainRecordRequest(
                record_id=record
            )
            logging.info(f"Deleting record {record} for domain {domain}")
            result = client.delete_domain_record(delete_domain_record_request)
            logging.info(f"Record {record} deleted successfully")
            return result.to_map()
        except Exception as e:
            logging.error(f"Failed to delete record {record}: {str(e)}")
            raise

    def get_record(self, domain, length, sub_domain, record_type):
        try:
            client = self.create_client()
            describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
                domain_name=domain,
                page_size=length,
                rrkey_word=sub_domain,
                type=record_type
            )
            logging.info(f"Getting records for domain {domain}, subdomain {sub_domain}, type {record_type}")
            result = client.describe_domain_records(describe_domain_records_request)
            result = result.to_map()
            result['data'] = result.pop('body')['DomainRecords']
            result['data']['records'] = result['data'].pop('Record')
            for record in result['data']['records']:
                record['id'] = record.pop('RecordId')
                record['line'] = record['Line'].replace('telecom', '电信').replace('unicom', '联通').replace(
                    'mobile', '移动').replace('oversea', '境外').replace('default', '默认')
            logging.info(f"Successfully retrieved {len(result['data']['records'])} records")
            return result
        except Exception as e:
            logging.error(f"Failed to get records: {str(e)}")
            raise

    def create_record(self, domain, sub_domain, value, record_type, line, ttl):
        try:
            client = self.create_client()
            if line == "电信":
                line = "telecom"
            elif line == "联通":
                line = "unicom"
            elif line == "移动":
                line = "mobile"
            elif line == "境外":
                line = "oversea"
            elif line == "默认":
                line = "default"
            add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
                domain_name=domain,
                rr=sub_domain,
                type=record_type,
                value=value,
                line=line,
                ttl=ttl
            )
            logging.info(f"Creating record for domain {domain}, subdomain {sub_domain}, type {record_type}")
            result = client.add_domain_record(add_domain_record_request)
            logging.info(f"Record created successfully with ID {result.body.record_id}")
            return result.to_map()
        except Exception as e:
            logging.error(f"Failed to create record: {str(e)}")
            raise

    def change_record(self, domain, record_id, sub_domain, value, record_type, line, ttl):
        try:
            client = self.create_client()
            if line == "电信":
                line = "telecom"
            elif line == "联通":
                line = "unicom"
            elif line == "移动":
                line = "mobile"
            elif line == "境外":
                line = "oversea"
            elif line == "默认":
                line = "default"
            update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
                record_id=record_id,
                rr=sub_domain,
                type=record_type,
                value=value,
                line=line,
                ttl=ttl
            )
            logging.info(f"Updating record {record_id} for domain {domain}")
            result = client.update_domain_record(update_domain_record_request)
            logging.info(f"Record {record_id} updated successfully")
            return result.to_map()
        except Exception as e:
            logging.error(f"Failed to update record {record_id}: {str(e)}")
            raise
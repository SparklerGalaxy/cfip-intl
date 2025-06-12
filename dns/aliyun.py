#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
# Reference: https://help.aliyun.com/document_detail/29776.html?spm=a2c4g.11186623.2.38.3fc33efexrOFkT
# REGION: https://help.aliyun.com/document_detail/198326.html
import json
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
rc_format = 'json'
class AliApi():
    def __init__(self, ACCESSID, SECRETKEY, REGION='cn-hongkong'):
        self.access_key_id = ACCESSID
        self.access_key_secret = SECRETKEY
        self.region = REGION

    def create_client(self) -> Alidns20150109Client:
        credential = CredentialClient(self.access_key_id, self.access_key_secret)
        config = open_api_models.Config(
            credential=credential,
            region_id=self.region
        )
        config.endpoint = f'alidns.cn-hangzhou.aliyuncs.com'
        return Alidns20150109Client(config)
        
    def del_record(self, domain, record):
        client = self.create_client()
        delete_domain_record_request = alidns_20150109_models.DeleteDomainRecordRequest(
            record_id=record
        )
        result = client.delete_domain_record(delete_domain_record_request)
        return result.to_map()
    def get_record(self, domain, length, sub_domain, record_type):
        client = self.create_client()
        describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
            domain_name=domain,
            page_size=length,
            rrkey_word=sub_domain,
            type=record_type
        )
        result = client.describe_domain_records(describe_domain_records_request)
        result = result.to_map()
        result['data'] = result.pop('DomainRecords')
        result['data']['records'] = result['data'].pop('Record')
        for record in result['data']['records']:
            record['id'] = record.pop('RecordId')
            record['line'] = record['Line'].replace('telecom', '电信').replace('unicom', '联通').replace('mobile', '移动').replace('oversea', '境外').replace('default', '默认')
        return result

    def create_record(self, domain, sub_domain, value, record_type, line, ttl):
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
        result = client.add_domain_record(add_domain_record_request)
        return result.to_map()
    def change_record(self, domain, record_id, sub_domain, value, record_type, line, ttl):
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
        result = client.update_domain_record(update_domain_record_request)
        return result.to_map()

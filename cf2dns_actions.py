#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from alibabacloud_alidns20150109.client import Client as AlidnsClient
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CreConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as dns_models
from alibabacloud_tea_util.client import Client as UtilClient

# 配置日志和常量
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LINE_MAPPING = {"电信": "telecom", "联通": "unicom", "移动": "mobile", "境外": "oversea", "默认": "default"}

class AliDNSManager:
    def __init__(self, access_id, secret_key):
        self.access_id = access_id
        self.secret_key = secret_key
        self.client = self._create_client()
    
    def _create_client(self) -> AlidnsClient:
        """创建阿里云DNS客户端[2](@ref)"""
        try:
            cred_config = CreConfig(
                type='access_key',
                access_key_id=self.access_id,
                access_key_secret=self.secret_key
            )
            dns_config = open_api_models.Config(
                credential=CredClient(cred_config),
                endpoint='alidns.cn-hongkong.aliyuncs.com'
            )
            return AlidnsClient(dns_config)
        except Exception as e:
            logging.error(f"客户端创建失败: {str(e)}")
            raise

    def _map_line(self, line):
        """线路名称中英文映射[3](@ref)"""
        return LINE_MAPPING.get(line, line)

    def delete_record(self, record_id):
        """删除DNS记录[6](@ref)"""
        request = dns_models.DeleteDomainRecordRequest(record_id=record_id)
        try:
            response = self.client.delete_domain_record(request)
            logging.info(f"记录 {record_id} 删除成功")
            return response.to_map()
        except Exception as e:
            logging.error(f"记录删除失败: {str(e)}")
            raise

    def get_records(self, domain, sub_domain, record_type, page_size=100):
        """获取DNS记录列表[4](@ref)"""
        request = dns_models.DescribeDomainRecordsRequest(
            domain_name=domain,
            page_size=page_size,
            rrkey_word=sub_domain,
            type=record_type
        )
        try:
            response = self.client.describe_domain_records(request)
            data = response.to_map()['body']['DomainRecords']
            records = data['Record']
            
            # 转换记录格式
            return [{
                'id': record['RecordId'],
                'line': record['Line'].replace('telecom', '电信')
                                      .replace('unicom', '联通')
                                      .replace('mobile', '移动')
                                      .replace('oversea', '境外')
                                      .replace('default', '默认'),
                'value': record['Value']
            } for record in records]
        except Exception as e:
            logging.error(f"记录获取失败: {str(e)}")
            raise

    def create_record(self, domain, sub_domain, value, record_type, line, ttl=600):
        """创建DNS记录[5](@ref)"""
        request = dns_models.AddDomainRecordRequest(
            domain_name=domain,
            rr=sub_domain,
            type=record_type,
            value=value,
            line=self._map_line(line),
            ttl=ttl
        )
        try:
            response = self.client.add_domain_record(request)
            record_id = response.body.record_id
            logging.info(f"记录创建成功: ID={record_id}")
            return response.to_map()
        except Exception as e:
            logging.error(f"记录创建失败: {str(e)}")
            raise

    def update_record(self, record_id, sub_domain, value, record_type, line, ttl=600):
        """更新DNS记录[8](@ref)"""
        request = dns_models.UpdateDomainRecordRequest(
            record_id=record_id,
            rr=sub_domain,
            type=record_type,
            value=value,
            line=self._map_line(line),
            ttl=ttl
        )
        try:
            response = self.client.update_domain_record(request)
            logging.info(f"记录 {record_id} 更新成功")
            return response.to_map()
        except Exception as e:
            logging.error(f"记录更新失败: {str(e)}")
            raise
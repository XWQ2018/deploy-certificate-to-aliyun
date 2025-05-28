import datetime
import os
from aliyunsdkcore.client import AcsClient
from aliyunsdkcdn.request.v20180510 import SetCdnDomainSSLCertificateRequest
# from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest

def get_env_var(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Environment variable {key} not set")
    return value

def file_exists_and_not_empty(file_path):
    expanded_path = os.path.expanduser(file_path)
    return os.path.isfile(expanded_path) and os.path.getsize(expanded_path) > 0

def upload_certificate(client, domain_name, cert_path, key_path):
    expanded_cert_path = os.path.expanduser(cert_path)
    expanded_key_path = os.path.expanduser(key_path)

    print(f"Uploading certificate for domain--expanded_cert_path=: {expanded_cert_path}")
    print(f"Uploading certificate for domain---expanded_key_path=: {expanded_key_path}")
    print(f"domain_name=: {domain_name}")
    

    if not file_exists_and_not_empty(expanded_cert_path) or not file_exists_and_not_empty(expanded_key_path):
        raise FileNotFoundError(f"Certificate or key file for domain {domain_name} is missing or empty")
    
    with open(expanded_cert_path, 'r') as f:
        cert = f.read()

    with open(expanded_key_path, 'r') as f:
        key = f.read()

    request = SetCdnDomainSSLCertificateRequest.SetCdnDomainSSLCertificateRequest()

    # CDN加速域名
    request.set_DomainName(domain_name)
    # 证书名称
    request.set_CertName(domain_name + datetime.datetime.now().strftime("%Y%m%d"))
    request.set_CertType('upload')
    request.set_SSLProtocol('on')
    request.set_SSLPub(cert)
    request.set_SSLPri(key)
    request.set_CertRegion('cn-hangzhou')

    response = client.do_action_with_exception(request)
    print(str(response, encoding='utf-8'))

def main():
    access_key_id = get_env_var('ALIYUN_ACCESS_KEY_ID')
    access_key_secret = get_env_var('ALIYUN_ACCESS_KEY_SECRET')
    domains = get_env_var('DOMAINS').split(',')
    cdn_domains = get_env_var('ALIYUN_CDN_DOMAINS').split(',')

    client = AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
    first_domain = domains[0] if len(domains) > 0 else None
    if not first_domain:
        raise ValueError("DOMAINS 环境变量未包含有效域名")
    
    print(f"使用的第一个域名：{first_domain}")

    # 所有CDN域名共用同一个证书
    for i,cdn_domain in enumerate(cdn_domains):
        if i == 0:  # 只处理索引为0的第一个元素
            # 使用f-strings格式化路径
            cert_path = f'~/certs/{first_domain}/fullchain.pem'
            key_path = f'~/certs/{first_domain}/privkey.pem'

            # 展开为绝对路径
            expanded_cert = os.path.expanduser(cert_path)
            expanded_key = os.path.expanduser(key_path)

            # 检查文件是否存在
            if not os.path.exists(expanded_cert) or not os.path.exists(expanded_key):
                print(f"警告：证书文件不存在，跳过 {cdn_domain}")
                continue

            upload_certificate(client, cdn_domain, cert_path, key_path)

            domainlog = cdn_domain.strip()
            print(f"处理的第一个域名: {domainlog}")
            # 后续操作...
        else:
         break  # 跳过其他域名
        
    
    # for domain, cdn_domain in zip(domains, cdn_domains):
    #     cert_path = f'~/certs/{domain}/fullchain.pem'
    #     key_path = f'~/certs/{domain}/privkey.pem'
    #     upload_certificate(client, cdn_domain, cert_path, key_path)
    

if __name__ == "__main__":
    main()
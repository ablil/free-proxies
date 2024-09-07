#!/usr/bin/env python3

import requests
import argparse
import json
from typing import Dict, List

proxy_source = 'https://proxylist.geonode.com/api/proxy-list'

def build_parser():
    parser = argparse.ArgumentParser(
        prog='freeproxy',
        description='fetch a working proxy'
    )

    parser.add_argument('-p', '--protocol', choices=['socks4', 'socks5', 'http', 'https', 'all'], default='http')
    parser.add_argument('-c', '--count', type=int, default=1)

    return parser

def fetch_proxies_list(protocol) -> Dict:
    print("Fetching list of proxies ...")
    response = requests.get(proxy_source,
        params={
            'limit': 500,
            'sort_by': 'speed',
            'sort_type': 'asc',
            'protocols': protocol
        }
    )
    if response.status_code != 200:
        print("Failed to fetch proxies list")
        exit(1)
    return json.loads(response.text)

def is_proxy_working(host, port, protocol) -> bool:
    try:
        if protocol == 'http':
            response = requests.get('http://example.com',
                proxies={'http': f"{protocol}://{host}:{port}"},
                timeout=1
            )
            return response.status_code == 200
    except Exception as e:
        return False

    raise Exception(f"Unknow protocol {protocol}")

def find_first_working_proxy(proxies_list: List[Dict], count: int) -> List[str]:
    print("Filtering list of proxies ...")
    total = 0
    result = []

    for proxy in proxies_list:
        host = proxy['ip']
        port = proxy['port']
        protocol = proxy['protocols'][0]
        if is_proxy_working(host, port, protocol):
            total += 1
            result.append((f"Found {protocol}://{host}:{port}"))
            print(f"Found {protocol}://{host}:{port}")
        if total >= count:
            exit(0)

    return None

def main():
    parser = build_parser()
    args = parser.parse_args()
    
    proxies_list = fetch_proxies_list(args.protocol)['data']
    proxies = find_first_working_proxy(proxies_list, args.count)
    if len(proxies) > 0 :
        print('Done')
    else:
        print("Did NOT find any working proxy !!!")

if __name__ == '__main__':
    main()

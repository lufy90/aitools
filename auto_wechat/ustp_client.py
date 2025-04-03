
import requests
import sys

URL="http://10.7.55.191:8000/api/"

class Client():
    def __init__(self, baseurl, username, password):
        self.baseurl = baseurl[:-1] if baseurl.endswith('/') else baseurl
        if not self.baseurl:
            self.baseurl = URL
        self.username = username
        self.password = password
        self.headers = {}

    def get_headers(self):
        response = requests.post(f"{self.baseurl}/token/", json={"username": self.username, "password":self.password})
        response.raise_for_status()
        response = response.json()
        if response["code"] != 2000:
            raise Exception(response["msg"])
        token = response["data"]["access"]
        self.headers = {"Authorization": "JWT "+token}

    def request(self, method, apiurl, **kw):
        if not apiurl.startswith('/'):
            apiurl = '/'+apiurl
        url = f"{self.baseurl}{apiurl}"
        if not url.endswith("/"):
            url=f"{url}/"
        response = requests.request(method, url, headers=self.headers, **kw)
        response.raise_for_status()
        response = response.json()
        if response["code"] != 2000:
            self.get_headers()
            response = requests.request(method, url, headers=self.headers, **kw)
            response.raise_for_status()
            response=response.json()
        return response


def get_task_keys(c):
    import csv
    task_apis = ["task","sysmonitor","performance/task","uharden","domain/task","cveupdate","youqu/yqtask","ltp"]
    for task_api in task_apis:
        f=open('test.csv','a')

        try:
            instance = c.request("GET", task_api)["data"]["data"][0]
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            l=sorted(instance.keys())
            l.insert(0,task_api)
            wr.writerow(l)
            
            print(task_api, ":", sorted(instance.keys()))
        except:
            print(task_api, ":", "failed to get", file=sys.stderr)
        finally:
            f.close()


if __name__ == "__main__":
    api = input("Input API(eg. task): ")
    username = input("Input user name: ")
    password = input("Input password: ")
    c = Client(username, password)
    import json
    #print(json.dumps(c.request("GET", api),indent=2))
    #get_task_keys(c)

    nic_info = {
          "eth0": {
            "mac": "52:54:00:20:10:14",
            "type": "bridge",
            "model": "virtio",
            "source": "br0",
            "host_interface": "vnet14"
          },
          "eth111111111111111111": {
              "mac": "52:54:00:20:10:14",
            "type": "bridge",
            "model": "virtio",
            "source": "br0",
            "host_interface": "vnet14"
            }
        }
    print(json.dumps(c.request("PATCH", api, data = {"nic_info":json.dumps(nic_info)}),indent=2))


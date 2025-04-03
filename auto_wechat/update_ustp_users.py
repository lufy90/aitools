import os
import sys
import time
import json

from ustp_client import Client
from get_wechat_user import get_person
from config import USTP_API_URL, USER, PASSWORD

client = Client(USTP_API_URL, USER, PASSWORD)

def get_users(**kw):
    res = client.request('GET', '/system/user/', params={"limit":9999, **kw})
    users = res.get('data').get('data')
    return users

def get_depts():
    res = client.request('GET', '/system/dept/', params={'limit': 9999})
    depts = res.get('data').get('data')
    return depts

def update_user(user_info:dict, depts:list):
    username = user_info.get("name")
    wechat_user = get_person(username)

    # if user_name get same no in ustp and wechat
    if not wechat_user.no.lower() == user_info.get("username").lower():
        raise Exception(f'Different user No to {name}: {wechat_user.no}, {user_info.get("username")}')

    wechat_dept_names = wechat_user.dept.split('/')
    print(f'wechat_dept_names: {wechat_dept_names}')
    ustp_dept_names = wechat_dept_names[2:]
    print(f'ustp_dept_names: {ustp_dept_names}')

    ustp_depts = []
    for name in ustp_dept_names:
        try:
            parent_id = ustp_depts[-1].get('id')
        except IndexError:
            parent_id = None
        named_depts = [x for x in depts if name == x.get('name') and x.get('parent') == parent_id]
        if len(named_depts) > 1:
            raise Exception("Duplicated names: f{ustp_depts}")
        elif len(named_depts) == 0:
            print(f'no such dept: {name}, now create.')
            # create new dept
            res = client.request('POST', '/system/dept/', data={'parent':parent_id,'name':name})
            depts = get_depts()
            named_depts = [x for x in depts if name == x.get('name') and x.get('parent') == parent_id]
            if len(named_depts) != 1:
                raise Exception("cannot get named dept correctly")
            ustp_dept = named_depts[0]
        elif len(named_depts) == 1:
            ustp_dept = named_depts[0]
        ustp_depts.append(ustp_dept)
    print(f'uspt_depts: {ustp_depts}')

    exp_user_dept = ustp_depts[-1].get('id')
    current_user_dept = user_info.get('dept')

    if current_user_dept != exp_user_dept:
        # update user dept
        res = client.request('PATCH', f"/system/user/{user_info.get('id')}", data={'dept': exp_user_dept})
        if res.get('code') != 2000:
            print('res:', res)
        else:
            print(f'{username} has updated')
    else:
        print(f'{username} has no need to update')

def update_users(**kw):
    depts = get_depts()
    users = get_users(**kw)
    for user in users:
        update_user(user, depts)


if __name__ == "__main__":
    os.system('xdotool windowactivate 127926280')
    time.sleep(2)
    update_users(name=sys.argv[1])

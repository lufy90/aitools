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
    if not wechat_user.is_valid:
        print(f'Invalid user: {username}')
        print(f'Need deactivate: {username}')
        #res = client.request('PATCH', f"/system/user/{user_info.get('id')}", data={'is_active': False})
        return None

    # if user_name get same no in ustp and wechat
    if not wechat_user.no.lower() == user_info.get("username").lower():
        raise Exception(f'Different user No to {username}: {wechat_user.no}, {user_info.get("username")}')

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
            print(f'named_depts: {named_depts}')
            raise Exception(f"Duplicated names: {ustp_depts}")
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
    print(f'ustp_depts: {ustp_depts}')

    exp_user_dept = ustp_depts[-1].get('id')
    current_user_dept = user_info.get('dept')

    if current_user_dept != exp_user_dept:
        # update user dept
        res = client.request('PATCH', f"/system/user/{user_info.get('id')}", data={'dept': exp_user_dept})
        if res.get('code') != 2000:
            print('res:', res)
        else:
            print(f'{username} has been updated')
    else:
        print(f'{username} has no need to update')

def update_users(**kw):
    depts = get_depts()
    users = get_users(**kw)

    for user in users:
        try:
            update_user(user, depts)
        except Exception as e:
            print(f'user {user.get("name")} failed with exception {str(e)}')
            #raise(e)


if __name__ == "__main__":
    #os.system('xdotool windowactivate 127926280')
    time.sleep(2)
    #update_users(name=sys.argv[1])
    update_users(limit=999)

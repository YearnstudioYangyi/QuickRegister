import base64
from time import sleep
import requests
import json
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def get_validate_code():
    url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/validateCode/picture"
    t = random.random()
    full_url = f"{url}?t={t}"
    
    try:
        response = requests.get(full_url, stream=True)
        response.raise_for_status()
        
        with open('./pic.jpg', 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print("验证码图片已成功保存到 ./pic.jpg")
        return response.cookies.get("JSESSIONID")
    except requests.exceptions.RequestException as e:
        print(f"获取验证码失败: {e}")
        return None

def encode_credentials(account, password, checkcode):
    encoded_account = base64.b64encode(account.encode('utf-8')).decode('utf-8')
    combined = account + base64.b64encode(password.encode('utf-8')).decode('utf-8')
    encoded_password = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    return {
        "account": encoded_account,
        "password": encoded_password,
        "checkcode": checkcode
    }

def show_image_and_get_code():
    def on_submit(entry_var):
        root.destroy()
        return entry_var.get()

    root = tk.Tk()
    # 窗口居中
    root.geometry("+%d+%d" % (root.winfo_screenwidth() // 2 - 200, root.winfo_screenheight() // 2 - 100))
    root.title("验证码输入")
    
    image = Image.open('./pic.jpg')
    photo = ImageTk.PhotoImage(image)
    
    label = tk.Label(root, image=photo)
    label.image = photo  # 保持对图片的引用
    label.pack(pady=10)
    
    entry_var = tk.StringVar()
    entry = tk.Entry(root, font=('Arial', 14), textvariable=entry_var)
    entry.pack(pady=10)
    
    submit_button = tk.Button(root, text="提交", command=lambda: on_submit(entry_var))
    submit_button.pack(pady=10)
    
    root.mainloop()
    return entry_var.get()

def main():
    confirm = {
        "phoneOne": "",
        "phoneTwo": "",
        "postalCode": "",
        "address": "陕西省宝鸡市宝鸡中学",
        "gradSchoolName": "",
        "gradCityCode": "",
        "gradExamAreaCode": "",
        "gradSchoolId": ""
    }
    headers = {
        "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0""",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Origin": "https://www.sneac.edu.cn",
        "Sec-Ch-Ua": """Not.A/Brand";v="99", "Chromium";v="133", "Microsoft Edge";v="133""",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Dnt": "1",
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }
    
    accout = input('请输入账号:')
    password = input('请输入密码:')
    new_passwd = input('请输入新密码(已修改留空):')
    
    JSESSION = get_validate_code()
    if not JSESSION:
        return
    
    code = show_image_and_get_code()
    url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/login"
    data = encode_credentials(accout, password, code)
    re = requests.post(url, headers=headers, data=json.dumps(data), cookies={"JSESSIONID": JSESSION}).json()
    # print(f'调试信息：请求结果{re}')
    if re.get('recode_desc') == "首次登录，请及时修改密码！" or re.get('recode') == 0:
        if re.get('recode_desc') == "首次登录，请及时修改密码！":
            print(f"学生姓名: {re.get('data').get('userinfo').get('studName')}")
            print(f"获取到Token: {re.get('data').get('token')}")
            token = re.get('data').get('token')
        
            print('正在提交修改密码')
            data = {"oldPwd": password, "newPwd": new_passwd, "token": token}
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/modifypwd"
            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(f"修改密码响应: {response.json().get('desc')}")
        
            print('修改完成')
            print('正在重新获取Token')
            password = new_passwd
            JSESSION = get_validate_code()
            if not JSESSION:
                print("获取验证码失败，请重试")
                return
            code = show_image_and_get_code()
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/login"
            data = encode_credentials(accout, password, code)
            re = requests.post(url, headers=headers, data=json.dumps(data), cookies={"JSESSIONID": JSESSION}).json()
        # print(f'[Info]调试信息\n{re}')
        if re.get('recode') == 0:
            print(f"学生姓名: {re.get('data').get('userinfo').get('studName')}")
            print(f"获取到Token: {re.get('data').get('token')}")
            token = re.get('data').get('token')
            
            cookie = f'JSESSIONID={JSESSION};fz_student_token={token}'#{"JSESSIONID": JSESSION, 'fz_student_token': token}
            XToken = token
            headers['Cookie'] = cookie
            headers['X-Token'] = XToken
            
            print("1. 提交信息")
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/student/info/first/confirm"
            confirm['phoneOne'] = input('请输入手机号:')
            confirm['phoneTwo'] = input('请输入手机号2(没有请留空):')
            
            re = requests.post(url, headers=headers, data=json.dumps(confirm))
            print(re.json().get('recode_desc'))
            
            print('正在准备承诺书')
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/base/data/info/detail?informationClassId=6"
            requests.get(url, headers=headers).json()
            
            print('正在提交承诺书')
            headers['Cookie'] = "sidebarStatus=0;" + headers['Cookie']
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/base/data/student/undertaking/sure"
            requests.post(url, headers=headers, data=json.dumps({"content": "本人已阅读，并理解和同意遵守本承诺书所有条款。"}))
            
            print('2. 提交科目\n正在提交科目')
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/student/enroll/notice/get"
            requests.get(url, headers=headers)
            
            data = {
                "syllbus": [
                    {"syllabusCode": "05", "syllabusName": "历史"},
                    {"syllabusCode": "06", "syllabusName": "地理"},
                    {"syllabusCode": "09", "syllabusName": "生物学"},
                    {"syllabusCode": "10", "syllabusName": "信息技术"}
                ],
                "studExamCode": "2403011071530",
                "examinationCode": "202505",
                "typeCode": "save"
            }
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/subject/save"
            requests.post(url, headers=headers, data=json.dumps(data))
            
            print('正在确定提交(约3秒)')
            sleep(3)
            
            data = {
                "syllbus": [
                    {"syllabusCode": "05", "syllabusName": "历史"},
                    {"syllabusCode": "06", "syllabusName": "地理"},
                    {"syllabusCode": "09", "syllabusName": "生物学"},
                    {"syllabusCode": "10", "syllabusName": "信息技术"}
                ],
                "studExamCode": "2403011071510",
                "examinationCode": "202505",
                "typeCode": "commit"
            }
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/subject/save"
            ret = requests.post(url, headers=headers, data=json.dumps(data)).json()
            print(ret.get('recode_desc'))
            
            print("处理完成！正在退出登录")
            url = "https://www.sneac.edu.cn/xuekao/gzxyks_student/logout"
            requests.post(url, headers=headers)
            print("退出登录成功")
        else:
            print("重新登录失败:", re.get('recode_desc'))
    else:
        print("登录失败:", re.get('recode_desc'))
        print(f'[Info]调试信息{re}')

if __name__ == "__main__":
    print('水平考试自动报名工具 v1.0 by 阳毅')
    print('适用于物化生、物化地、物化政组合\n')
    main()
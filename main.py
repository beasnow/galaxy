# coding=utf-8
import urllib.request
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
import schedule
import time
import smtplib

# QQ邮箱提供的SMTP服务器
mail_host = 'smtp.qq.com'
# 服务器端口
port = 465
send_by = '542521464@qq.com'
password = 'hvhxetudvhyybbga'
send_to = '542521464@qq.com'


def send_email(title, content):
    # 创建了MIMEText类，相当于在写邮件内容，是plain类型
    message = MIMEText(','.join(content), 'plain', 'utf-8')
    message["From"] = send_by
    message['To'] = send_to
    message['Subject'] = title
    try:
        # 注意第三个参数，设置了转码的格式(我不设的时候会报解码错误)
        smpt = smtplib.SMTP_SSL(mail_host, port, 'utf-8')
        smpt.login(send_by, password)
        smpt.sendmail(send_by, send_to, message.as_string())
        print("发送成功")
    except:
        print("发送失败")


area = {
    '天府新区': '042'
}


def connect_with_url(pageNo=1):
    url = 'https://zw.cdzj.chengdu.gov.cn/lottery/accept/projectList'
    areaName = '天府新区'
    # 请求体 042表示天府新区
    param = {
        'pageNo': pageNo,
        'regioncode': area[areaName]
    }

    formdata = urllib.parse.urlencode(param).encode()
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }

    # 设置一个请求体
    req = urllib.request.Request(url, headers=headers, data=formdata, method='POST')

    # 发起请求
    response = urllib.request.urlopen(req)
    data = response.read().decode('utf-8')
    return data


def getEffectDom(pageNo=1):
    urlContent = connect_with_url(pageNo)
    # html结构
    soup = BeautifulSoup(urlContent)
    return soup.find('tbody', id='_projectInfo')
    # 当前html中的可选房屋的dom


def getTotalPage():
    urlContent = connect_with_url()
    soup = BeautifulSoup(urlContent)
    effectScript = soup.find_all('script')[8]
    scriptText = str(effectScript)
    totalPageStartIndex = scriptText.find('totalPage')
    return int(scriptText[totalPageStartIndex + 22:totalPageStartIndex + 24])


def formatData(effectDom):
    name = 3
    startTime = 8
    terminalTime = 9
    status = 13
    dataArr = []
    for tr in effectDom.find_all('tr'):
        td = tr.find_all('td')
        try:
            horseName = td[name].text.strip()
            startDate = td[startTime].text.strip()
            terminalDate = td[terminalTime].text.strip()
            horseStatus = td[status].text.strip()
            dataArr.append({'name': horseName, 'start': startDate, 'end': terminalDate, 'status': horseStatus})
            # print('%s_%s_%s_%s' % (
            #     td[name].text.strip(),
            #     td[startTime].text.strip(),
            #     td[terminalTime].text.strip(),
            #     td[status].text.strip()))

        except IndexError as e:
            pass
    return dataArr


totalPage = getTotalPage()


def getAllData(totalPage):
    for i in range(1, totalPage + 1):
        effectDom = getEffectDom(i)
        listdada = formatData(effectDom)
        listdada += listdada

    finalData = []
    for single in listdada:
        finalData.append(str(single))

    send_email('天府新区楼盘情况', finalData)


schedule.every(1).day.at("09:00").do(getAllData, totalPage)
while True:
    # 启动服务
    schedule.run_pending()
    time.sleep(1)

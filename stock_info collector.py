import requests
import zipfile
from xml.etree import ElementTree
import json
import pymysql

#고유번호 Zip 파일 내려받기
crtfc_key = "***************************************" #API 인증키(openapi.dart.or.kr에서 발급)
api = "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={crtfc_key}"
url = api.format(crtfc_key=crtfc_key)

file_name = ".\\temp\\CORPCODE.zip"
with open(file_name, "wb") as f:
    f.write(requests.get(url).content)

#종목코드, 고유번호 딕셔너리 생성
xml = zipfile.ZipFile(file_name).read("CORPCODE.xml")
root_element = ElementTree.fromstring(xml)
iter_element = root_element.iter(tag="list")

corp_code_dic = {}
for element in iter_element:
    stock_code = element.find("stock_code").text
    corp_code_dic[stock_code] = element.find("corp_code").text
    print(stock_code + ": " + corp_code_dic[stock_code])

#고유번호로 법인구분 수집
df = []
for corp_code in corp_code_dic.values():
    try:
        api = "https://opendart.fss.or.kr/api/company.json?crtfc_key={crtfc_key}&corp_code={corp_code}"
        url = api.format(crtfc_key=crtfc_key, corp_code=corp_code)
        response = requests.get(url).text
        data = json.loads(response)

        if data["corp_cls"] =="Y":
            corp_cls = "KOSPI"
        elif data["corp_cls"] =="K":
            corp_cls = "KOSDAQ"
        else:
            continue
        df.append([data["stock_code"], data["stock_name"], corp_cls, corp_code])
        print(data["stock_code"], data["stock_name"], corp_cls, corp_code)
    except:
        continue

#DBMS에 저장
conn = pymysql.connect(host="127.0.0.1", user="root", password="*********", db="****", charset="utf8")

for row in df:
    cur = conn.cursor()
    cur.execute("insert into stock_info values('" + row[0] + "', '" + row[1] + "', '" + row[2] + "', '" + row[3] +"')")

conn.commit()
conn.close()

print("작업 완료")
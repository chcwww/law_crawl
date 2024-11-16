"""
The script is for `Data Science for Public Affairs and Legal Application with Python`

能拿來查司法院裁判書系統的小東西，僅提供最基礎的功能，如有其他需求如輸入輸出的優化請自行根據需求調整。
司法院裁判書系統: https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx

Hung-Chih Chiang, 15 Nov 2024
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

HIDE = True # Don't want to see brower?
# DRIVER = None # Fake driver, in case you don't know there is a driver 

# Change it if you don't need all results
MAX_PAGE = 1 # the api only allowed 25 pages for each court
MAX_ITEM = 2 # the api only allowed 500 judgements for each court

LAW_URL = "https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx"
OUTPUT_FILE_NAME = "judgement_crawl_result.json"

QUERY = {
    "法院": [], # empty means all
    "案件類別": [], # empty means all
    "text": {
        "字號年度" : [""],
        "字號常用字別" : [""],
        "字號第[0]號到第[1]號" :  ["", ""],
        "期間民國年[0]到[1]" : ["", ""], 
        "期間民國月[0]到[1]" : ["", ""], 
        "期間民國日[0]到[1]" : ["", ""],
        "裁判案由" : [""],
        "裁判主文" : [""],
        "全文內容" : [""],
        "裁判大小[0]K到[1]K" : ["", ""]
    }
}

LAW_COURT_MAPPING = {
    '憲法法庭': 'JCC', 
    '司法院刑事補償法庭': 'TPC', 
    '司法院－訴願決定': 'TPU', 
    '最高法院': 'TPS', 
    '最高行政法院(含改制前行政法院)': 'TPA', 
    '懲戒法院－懲戒法庭': 'TPP', 
    '懲戒法院－職務法庭': 'TPJ', 
    '臺灣高等法院': 'TPH', 
    '臺灣高等法院－訴願決定': '001', 
    '臺北高等行政法院 高等庭(含改制前臺北高等行政法院)': 'TPB', 
    '臺北高等行政法院 地方庭': 'TPT', 
    '臺中高等行政法院 高等庭(含改制前臺中高等行政法院)': 'TCB', 
    '臺中高等行政法院 地方庭': 'TCT', 
    '高雄高等行政法院 高等庭(含改制前高雄高等行政法院)': 'KSB', 
    '高雄高等行政法院 地方庭': 'KST', 
    '智慧財產及商業法院': 'IPC', 
    '臺灣高等法院 臺中分院': 'TCH', 
    '臺灣高等法院 臺南分院': 'TNH', 
    '臺灣高等法院 高雄分院': 'KSH', 
    '臺灣高等法院 花蓮分院': 'HLH', 
    '臺灣臺北地方法院': 'TPD', 
    '臺灣士林地方法院': 'SLD', 
    '臺灣新北地方法院': 'PCD', 
    '臺灣宜蘭地方法院': 'ILD', 
    '臺灣基隆地方法院': 'KLD', 
    '臺灣桃園地方法院': 'TYD', 
    '臺灣新竹地方法院': 'SCD', 
    '臺灣苗栗地方法院': 'MLD', 
    '臺灣臺中地方法院': 'TCD', 
    '臺灣彰化地方法院': 'CHD', 
    '臺灣南投地方法院': 'NTD', 
    '臺灣雲林地方法院': 'ULD', 
    '臺灣嘉義地方法院': 'CYD', 
    '臺灣臺南地方法院': 'TND', 
    '臺灣高雄地方法院': 'KSD', 
    '臺灣橋頭地方法院': 'CTD', 
    '臺灣花蓮地方法院': 'HLD', 
    '臺灣臺東地方法院': 'TTD', 
    '臺灣屏東地方法院': 'PTD', 
    '臺灣澎湖地方法院': 'PHD', 
    '福建高等法院金門分院': 'KMH', 
    '福建金門地方法院': 'KMD', 
    '福建連江地方法院': 'LCD', 
    '臺灣高雄少年及家事法院': 'KSY'
    }

LAW_CLICK_MAPPING = { # id
    "憲法" : 'vtype_C',
    "民事" : 'vtype_V',
    "刑事" : 'vtype_M',
    "行政" : 'vtype_A',
    "懲戒" : 'vtype_P'
    }

LAW_INPUT_MAPPING = { # id
    "字號年度" : ['jud_year'],
    "字號常用字別" : ['jud_case'],
    "字號第[0]號到第[1]號" :  ['jud_no', 'jud_no_end'],
    "期間民國年[0]到[1]" : ['dy1', 'dy2'], 
    "期間民國月[0]到[1]" : ['dm1', 'dm2'], 
    "期間民國日[0]到[1]" : ['dd1', 'dd2'],
    "裁判案由" : ['jud_title'],
    "裁判主文" : ['jud_jmain'],
    "全文內容" : ['jud_kw'],
    "裁判大小[0]K到[1]K" : ['KbStart', 'KbEnd']
    }

i=-1
simple_input_map = {(i:=i+1): element for _, element in LAW_INPUT_MAPPING.items()}

i=-1
simple_click_map = {(i:=i+1): element for _, element in LAW_CLICK_MAPPING.items()}

# Initialize a driver with url
def init_driver():
    global DRIVER
    options = Options()
    if HIDE:
        options.add_argument('--headless')

    path = "./geckodriver.exe"
    service = Service(executable_path=path)

    options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
    DRIVER = webdriver.Firefox(service=service, options = options)
    
def back():
    DRIVER.back()
    
def finish():
    DRIVER.quit()
    
def driver_finds(*args):
    return DRIVER.find_elements(*args)

def driver_find(*args):
    try:
        return driver_finds(*args)[0]
    except:
        return list()
    
def driver_get(url):
    DRIVER.get(url)
    
def court_select(court): # can be lowercase
    driver_find(By.XPATH, f"//option[@value='{court.upper()}']").click()

def submit():
    driver_find("id", "btnQry").click()

def dynamic_crawl(href):
    driver_get(href)
    return driver_find("id", "jud").text

def static_crawl(href):
    r = requests.get(href)
    sp = BeautifulSoup(r.text, 'lxml')
    return sp.find(id = 'jud').text

if __name__ == "__main__" :
    print(QUERY)
    print(LAW_COURT_MAPPING)
    print(LAW_CLICK_MAPPING)
    print(LAW_INPUT_MAPPING)
    print(simple_input_map)
    print(simple_click_map)
    
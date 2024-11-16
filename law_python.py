"""
  The script is for `Data Science for Public Affairs and Legal Application with Python`
  
  Here is an example of how to use the script:
    如果要找 中央法規 和 憲法法庭裁判 且 含有 縣市長 且期間為 20101231~20201231 且發文文號為 10400151551
    且要看 法規名稱 和 法條內容 且要看 現行法規
    則在command line運行下面這行
    python ./law_python.py --L --B5 -kw1=縣市長 -w=10400151551 -ds 20101231 -dn 20201231  --A1 --A2 --FN
    可以參考以上範例以及依照parser那裡的help來下你有興趣的query
  
  Hung-Chih Chiang, NTPU STAT, 15 May 2024
"""
import re
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup


def add_args(parser):
    parser.add_argument('--L', action='store_true', help='中央法規')
    parser.add_argument('--C', action='store_true', help='條約協定')
    parser.add_argument('--A', action='store_true', help='兩岸協議')
    parser.add_argument('--B1', action='store_true', help='大法官解釋')
    parser.add_argument('--B2', action='store_true', help='最高法院民事判例')
    parser.add_argument('--B3', action='store_true', help='最高法院刑事判例')
    parser.add_argument('--B4', action='store_true', help='最高法院行政判例')
    parser.add_argument('--B5', action='store_true', help='憲法法庭裁判')

    parser.add_argument('--keyword1', '-kw1', type=str, default='', help="含有")
    parser.add_argument('--keyword2', '-kw2', type=str, default='', help="且含")
    parser.add_argument('--keyword3', '-kw3', type=str, default='', help="或")
    parser.add_argument('--keyword4', '-kw4', type=str, default='', help="不含")

    parser.add_argument('--date_start', '-ds', type=int, default=19110101, help="查詢起始日")
    parser.add_argument('--date_end', '-dn', type=int, default=20240515, help="查詢終止日")

    parser.add_argument('--word', '-w', type=int, default=None, help="發文文號")

    parser.add_argument('--A1', action='store_true', help='法規名稱')
    parser.add_argument('--A2', action='store_true', help='法條內容')

    parser.add_argument('--FN', action='store_true', help='現行法規')
    parser.add_argument('--FY', action='store_true', help='已廢止法規')

law_api = 'https://law.moj.gov.tw/Law/LawSearchResult.aspx'
api_arg = ['t', 'kw1', 'kw2', 'kw3', 'kw4', 'date', 'word', 'it', 'fei']

parser = argparse.ArgumentParser(description='Add argument for law api: https://law.moj.gov.tw/Law/LawSearchAll.aspx')
add_args(parser)

wargs = parser.parse_args()

kwargs = vars(wargs) # to dict
big_arg = ['t']*8 + ['kw1', 'kw2', 'kw3', 'kw4'] + ['date']*2 + ['word'] + ['it']*2 +['fei']*2
args = {a : {} for a in api_arg}
for i, obj in enumerate(kwargs.items()):
    args[big_arg[i]][obj[0]] = obj[1]
    
api_list = ['ty=Z']

valid_count = 0
for id, arg in args.items():
    if id=='date':
        # if arg.date_start is not None and arg.date_end is not None:
        api_list.append(f"{id}={arg['date_start']}_TO_{arg['date_end']}")
    else:
        temp=''
        for name, set in arg.items():
            if set:
                if id[:2] in ['kw', 'wo']:
                    valid_count += 1
                    temp+=str(set)
                else:
                    temp+=name
        api_list.append(f'{id}={temp}')    
# The search condition is not valid 這個api的規定是
# " 本單元檢索字詞、期間或發文文號欄位，需擇一輸入查詢條件，且可搭配複合查詢。 "
assert valid_count > 0, 'The search is not valid, you are asked to add some arguments.'

print('The query is valid, processing...\n')

all_cate = [f'J{i}' for i in range(1, 6)] + [i+o for i in ['L', 'C', 'A'] for o in ['n', 'd']]

arts = 0

def fake_crawl_process(url):
    global arts
    # Do something to extract info from the url
    # sample_data = pd._testing.makeMixedDataFrame()
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'html.parser')
    law_title = sp.find(id = 'hlLawName').text
    law_num = [ar.text for ar in sp.find_all(class_ = 'col-no')]
    law_articles = sp.find_all(class_ = 'law-article')
    text_all = [[law_title, '']]
    for idx, text in enumerate(law_articles):
        text_all.append([law_num[idx], text.text.replace('\n', '').replace('\t', '')])
        arts += 1
    text_all.append(['--skip--', '--skip--'])
    sample_data = pd.DataFrame(text_all, columns=['title', 'article'])
    return sample_data

full_data = pd.DataFrame()
kw_list = api_list[2:6]
api_temp = 'https://law.moj.gov.tw/LawClass/LawSearchContent.aspx?'

for cate in all_cate: # it’s ok since the cate not in the query will return empty page
    url_query = '&'.join([law_api+f'?cur={cate}'] + api_list)
    # print(api_list)
    # print(url_query)
    # print()
    """
    You can crawl the page or extract some law information here
    with the knowledge you learned from the course. I use `fake_crawl_process()` here,
    you can modify the function to fit your needs.
    You may create a temporary storage structure for the .csv file to save at the end. I
    use `full_data` as an example here.
    """
    try:
        r = requests.get(url_query)
        sp = BeautifulSoup(r.text, 'html.parser')
        full_table = sp.findAll('table')[0].findAll('tr')

        for a in full_table:
            try:
                href = a.find('a', href=True)['href']
                pcode = re.search(r'pcode=([0-9a-zA-Z]*)', href).group()
                url_page = '&'.join([api_temp, pcode] + kw_list)
                # print(url_page)
                """
                    `url_page` is the URL that contains the law articles you need. 
                    You should perform further processing, for example, in `fake_crawl_process()` (which you learned in class) 
                    to extract the text information from the table.
                """
                round_data = fake_crawl_process(url_page)
                full_data = pd.concat([full_data, round_data], axis=0).reset_index(drop=True)
            except:
                pass
                # print('No href this table\n')
    except Exception as e:
        pass
        # print(e) # 若是list index out of range大概就是那個頁面沒有資料 不管它就好 因為上面是所有可能的table都遍歷一遍
        # print('Catch error, continue.\n')
        
save_path = './result.csv'
full_data.to_csv(save_path, encoding='utf-8-sig', index=False)
print(f'Finish, catch {arts} articles.')
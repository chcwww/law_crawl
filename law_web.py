"""
The script is for `Data Science for Public Affairs and Legal Application with Python`

能拿來查司法院裁判書系統的小東西，僅提供最基礎的功能，如有其他需求如輸入輸出的優化請自行根據需求調整。
司法院裁判書系統: https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx

Hung-Chih Chiang, 15 Nov 2024
"""
import json
from tqdm.auto import tqdm
from selenium.webdriver.common.by import By

# Input useful utils from other .py file
from law_utils import *

def main():
    try:
        # Start crawling..
        init_driver()
        driver_get(LAW_URL)

        # check court
        court_visited = []
        for court_name in QUERY["法院"]:
            court_visited.append(LAW_COURT_MAPPING[court_name])
            court_select(LAW_COURT_MAPPING[court_name])
        if not QUERY["法院"]:
            for _, element in LAW_COURT_MAPPING.items():
                court_visited.append(element)
                
        # check category
        for cate_name in QUERY["案件類別"]:
            driver_find("id", LAW_CLICK_MAPPING[cate_name]).click()
        if not QUERY["案件類別"]:
            for _, element in LAW_CLICK_MAPPING.items():
                driver_find("id", element).click()

        # check text input
        for input_type, elements in QUERY["text"].items():
            for i, input_id in enumerate(LAW_INPUT_MAPPING[input_type]):
                driver_find("id", input_id).send_keys(elements[i])
                
        submit()

        # The result dict
        judgement_court_dict = {court: list() for court in court_visited}

        # href for courts we selected 
        court_element_dict = {court: driver_finds(By.XPATH, f"//a[@data-groupid='{court}']") for court in court_visited}
        court_href_dict = {court: element[0].get_attribute('href') for court, element in court_element_dict.items() if element}

        pbar = tqdm(court_href_dict.keys()) # tqdm bar
        for court in pbar:
            pbar.set_description(f"Processing court - {court}")
            driver_get(court_href_dict[court])
            
            # href for judgement in this court
            judgement_href_list = [element.get_attribute('href') for element in driver_finds("id", "hlTitle")]
            while (current_page:=driver_finds("id", "hlNext")):  # the list is not empty (next page exist)
                # go to next page
                current_page[0].click()
                # extend our href list
                judgement_href_list += [element.get_attribute('href') for element in driver_finds("id", "hlTitle")]
                pbar.set_postfix({'href page': len(judgement_href_list) // 20})
                if len(judgement_href_list) // 20 >= MAX_PAGE:
                    break

            judgement_text_list = []
            # Think about it, do we need SELENIUM here?
            for judgement_href in tqdm(judgement_href_list, desc='Processing judgement text', leave=False):
                if judgement_href is None:
                    continue
                
                # append text with crawl function
                judgement_text_list.append(dynamic_crawl(judgement_href))
                
                if len(judgement_text_list) == MAX_ITEM:
                    break

            # Add the result for this court
            judgement_court_dict[court] = judgement_text_list

        with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as f:
            json.dump(judgement_court_dict, f, indent=4, ensure_ascii=False)
            
    finally:
        finish() # close the driver

if __name__ == "__main__":
    main()

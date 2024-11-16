# TA course for Python資料科學-公共事務與法學應用 in NTPU.

## Environment
```shell
conda create --name ntpu_law python=3.11
conda activate ntpu_law
pip install -r requirements.txt
```
I used `walrus` operator in this code, so please ensure your python version is greater than `3.8`.
The versions for `requests`, `beautifulsoup4` and `selenium` should work freely, but I have only tested with the version specified in `requirements.txt`.


## [全國法規資料庫](https://law.moj.gov.tw/Law/LawSearchAll.aspx)
This is for the 112-2 course in NTPU. 
You should check `law_python.py`, then modify `law_search.sh`, and then run it.
```shell
bash law_python.sh
```

## [司法院裁判書](https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx)
This is for the 113-1 course in NTPU. 
You should check `law_utils.py`, then modify `QUERY` and other settings, and then run it. 
```shell
python law_python.py
```
Please make sure that both `Firefox` and `geckodriver.exe` are properly set up.
If you're using `MacOS` or don't like `Firefox`, and want to switch to a browser like `Edge` or `Chrome`, you can simply modify the `init_driver()` function in `law_utils.py` and continue the journel.

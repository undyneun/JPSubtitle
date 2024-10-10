from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from typing import *
import json
CACHE_FILE = r"/app/cache/cache.json"
optionsArgs = [
    "--disable-blink-features=AutomationControlled",
    "--headless",# 無頭模式
    "--no-sandbox",# 解決無特權 Docker 容器的問題
    "--disable-dev-shm-usage",# 解決共享內存不足問題
    "--disable-gpu",# 禁用 GPU
    "--remote-debugging-port=9222",# 遠端調試端口
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
    "--log-level=1"
]
driver = None
query_cache: dict = None


def close_driver():
    global driver
    if driver:
        driver.quit()
        driver = None

def init_driver():
    global optionsArgs, driver
    if driver is not None: 
        return
    from webdriver_manager.chrome import ChromeDriverManager # type: ignore
    options = webdriver.ChromeOptions()
    [options.add_argument(x) for x in optionsArgs]  
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

def get_string(url):
    global driver
    driver.get(url)
    string, state = "", False

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'suggest-box')))
    except TimeoutException: 
        return "查詢時間過長", state
    time.sleep(0.2)

    details = driver.find_elements(By.CLASS_NAME, 'mean-detail-range')
    if len(details) == 0:  
        return "查無此字", state

    state = True
    for detail in details:
        # 如果只有一個 example
        try:             
            detail.find_element(By.XPATH, './div[@class="example-range"]')
            mean = detail.find_element(By.TAG_NAME, 'h3')
            string += f"{mean.text}\n"
            try:
                rubys = detail.find_elements(By.TAG_NAME, 'ruby')
                span = detail.find_element(By.TAG_NAME, 'span')
                ruby_texts = [ruby.text for ruby in rubys if "\n" not in ruby.text]
                string += f"{''.join(ruby_texts)}\n"
                string += f"{span.text}\n"
                string += '\n'
            except NoSuchElementException:
                string += '\n'
                continue
            
        # 兩個以上
        except NoSuchElementException: 
            divs = detail.find_elements(By.XPATH, './div')
            for div in divs:
                # 排除裡面沒有mean與example的div
                try:
                    mean = div.find_element(By.TAG_NAME, 'h3')
                except NoSuchElementException:
                    continue

                string += f"{mean.text}\n"

                examples = div.find_elements(By.TAG_NAME, 'app-example')
                for example in examples:
                    rubys = example.find_elements(By.TAG_NAME, 'ruby')
                    span = example.find_element(By.TAG_NAME, 'span')
                    ruby_texts = [ruby.text for ruby in rubys]
                    ruby_texts = [text[:text.index('\n')] if '\n' in text else text for text in ruby_texts]
                    string += f"{''.join(ruby_texts)}\n"
                    string += f"{span.text}\n" 
                string += '\n'  
    return string, state

def load_cache():
    global query_cache
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            query_cache = json.load(f)
    except IOError:
        raise IOError("無此檔案")
    except Exception as e:
        raise e
    
def save_cache(word, result):
    global query_cache
    query_cache[word] = result
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(query_cache, f, ensure_ascii=False, indent=4)

def getResult(string, state):
    global driver
    result: List[dict] = []
    if state == False:
        result = [{"mean":f"{string}", "examples":[dict()]}]
    for means in string.split('\n\n')[:-1]: # means: mean, [examples]
        result.append(dict())

        if '\n' in means:  # 如果有例句
            meansList = means.split('\n')
            mean = meansList[0]
            examples: List[dict] = []
            for i in range(1, len(meansList), 2):
                examples.append(dict())
                examples[-1]["jp"] = meansList[i]
                examples[-1]["zh"] = meansList[i+1]
        else:
            mean, examples = means, []

        result[-1]["mean"] = mean
        result[-1]["examples"] = examples

    return result, state

def main(word1, word2):
    global driver, query_cache
    if word1 in query_cache:  return query_cache[word1], True
    if word2 in query_cache:  return query_cache[word2], True
    
    def f(word):
        string, state = get_string(f"https://mazii.net/zh-TW/search/word/jatw/{word}")
        result, state = getResult(string, state)
        if state != False:
            save_cache(word, result)
        return result, state
    
    state = None
    if word1:
        result, state = f(word1)
    # 沒有word1或word1查詢失敗時嘗試word2
    if (state is None or state == False) and word2:
        result, state = f(word2)
    return result, state

load_cache()
init_driver()
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import math
import os

# 크롬 headless 설정
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# 상호명 불러오기
df = pd.read_csv('C:/Users/sj123/KSEB_Project/KSEB_Project_output/inha_restaurant_FE.csv')
store_names = df['상호명'].tolist()

# 몇 개씩 나눌지
batch_size = 50
total_batches = math.ceil(len(store_names) / batch_size)

for batch_index in range(total_batches):
    print(f"\n📦 ▶▶ [Batch {batch_index+1}/{total_batches}] 시작")

    # 해당 배치의 상호명만 추출
    batch_names = store_names[batch_index * batch_size : (batch_index + 1) * batch_size]
    results = []

    for name in batch_names:
        print(f" 검색 중: {name}")
        url = f"https://map.naver.com/v5/search/{name}"
        driver.get(url)
        time.sleep(5)

        try:
            if "entryIframe" in driver.page_source:
                driver.switch_to.frame("entryIframe")
            elif "searchIframe" in driver.page_source:
                driver.switch_to.frame("searchIframe")
                time.sleep(2)
                try:
                    first = driver.find_element(By.CLASS_NAME, "search_place_title")
                    first.click()
                    time.sleep(2)
                    driver.switch_to.default_content()
                    driver.switch_to.frame("entryIframe")
                except NoSuchElementException:
                    raise Exception("검색결과 클릭 실패")
            else:
                print(f"iframe 없음: {name}")
                continue

            # 메뉴 영역 스크롤
            driver.execute_script("window.scrollBy(0, 600)")
            time.sleep(1)

            # 메뉴 가격 크롤링
            menu_prices = driver.find_elements(By.CLASS_NAME, "menu_price")
            prices = []
            for p in menu_prices:
                try:
                    price = int(p.text.replace(",", "").replace("원", "").strip())
                    prices.append(price)
                except:
                    continue

            avg_price = sum(prices) // len(prices) if prices else None
            results.append({
                "상호명": name,
                "1인 평균 가격": avg_price,
                "메뉴 수": len(prices)
            })

        except Exception as e:
            print(f"{name} 처리 중 오류 발생: {e}")
            results.append({
                "상호명": name,
                "1인 평균 가격": None,
                "메뉴 수": 0
            })

    # 배치 결과 저장
    filename = f"KSEB_Project_output/output_가게평균_{batch_index+1}.csv"
    os.makedirs("KSEB_Project_output", exist_ok=True)
    pd.DataFrame(results).to_csv(filename, index=False)
    print(f"저장 완료 → {filename}")

driver.quit()
print("\n모든 배치 완료")

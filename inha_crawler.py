import pandas as pd
import time
import os
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import difflib  # 유사도 비교용

# 크롬 headless 옵션
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# 데이터 불러오기
df = pd.read_csv('C:/Users/sj123/KSEB_Project/KSEB_Project_output/inha_restaurant_FE.csv')
store_names = df['상호명'].tolist()
batch_size = 50
total_batches = math.ceil(len(store_names) / batch_size)

for batch_index in range(total_batches):
    print(f"\n ▶▶ [Batch {batch_index+1}/{total_batches}] 시작")
    batch_names = store_names[batch_index * batch_size : (batch_index + 1) * batch_size]
    results = []

    for name in batch_names:
        print(f"검색 중: {name}")
        url = f"https://map.naver.com/v5/search/{name}"
        driver.get(url)
        time.sleep(5)

        try:
            if "entryIframe" in driver.page_source:
                driver.switch_to.frame("entryIframe")
            elif "searchIframe" in driver.page_source:
                driver.switch_to.frame("searchIframe")
                try:
                    wait = WebDriverWait(driver, 5)
                    candidates = wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "search_place_title"))
                    )

                    # 유사도 기반 클릭
                    candidate_texts = [c.text for c in candidates]
                    best_match = difflib.get_close_matches(name, candidate_texts, n=1, cutoff=0.6)

                    if best_match:
                        for c in candidates:
                            if c.text == best_match[0]:
                                c.click()
                                break
                        time.sleep(2)
                        driver.switch_to.default_content()
                        driver.switch_to.frame("entryIframe")
                    else:
                        print(f" 유사 상호명 없음: {name}")
                        continue

                except Exception:
                    raise Exception("검색결과 클릭 실패")
            else:
                print(f"iframe 없음: {name}")
                continue

            # 메뉴 스크롤 후 메뉴 가격 수집
            driver.execute_script("window.scrollBy(0, 600)")
            time.sleep(1)

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

    os.makedirs("KSEB_Project_output", exist_ok=True)
    filename = f"KSEB_Project_output/output_가게평균_{batch_index+1}.csv"
    pd.DataFrame(results).to_csv(filename, index=False)
    print(f"✅ 저장 완료 → {filename}")

driver.quit()
print("\n전체 배치 크롤링 완료")

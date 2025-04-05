# inha_batch_crawler.py
# 배치 처리 루프 코드
# 크롤링 함수 코드와 배치 루프 코드 분리 커맨드 창으로 배치 돌림
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from inha_crawling_util import crawling_get_menus  # 크롤링 함수 import

# 크롬 headless 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

df = pd.read_csv("C:\Users\sj123\KSEB_Project\KSEB_Project_output\inha_restaurant_FE.csv", encoding="utf-8-sig")
store_names = df["상호명"].tolist()
results = []

for name in store_names:
    print(f"크롤링 중: {name}")
    try:
        data = crawling_get_menus(name, driver)
        prices = []
        for menu_name, price in data["menu"]:
            try:
                num = int(price.replace(",", "").replace("원", "").strip())
                prices.append(num)
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

# 저장
os.makedirs("KSEB_Project_output", exist_ok=True)
pd.DataFrame(results).to_csv("KSEB_Project_output/inha_result_final.csv", index=False, encoding="utf-8-sig")
driver.quit()
print("크롤링 완료 및 저장")

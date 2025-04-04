from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# 크롬 드라이버 설정 (백그라운드 실행)
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# 가게 목록 불러오기
df = pd.read_csv('C:/Users/sj123/KSEB_Project/KSEB_Project_output/inha_restaurant_FE.csv')
store_names = df['상호명'].tolist()

result = []

for name in store_names:
    print(f"▶ 검색 중: {name}")
    url = f"https://map.naver.com/v5/search/{name}"
    driver.get(url)
    time.sleep(5)

    try:
        driver.switch_to.frame("searchIframe")
        time.sleep(2)

        # 첫 번째 검색 결과 클릭
        first = driver.find_element(By.CLASS_NAME, "search_place_title")
        first.click()
        time.sleep(2)

        driver.switch_to.default_content()
        driver.switch_to.frame("entryIframe")
        time.sleep(2)

        # 메뉴 섹션 스크롤
        driver.execute_script("window.scrollBy(0, 600)")
        time.sleep(2)

        menu_elems = driver.find_elements(By.CLASS_NAME, "place_section_content")
        prices = []

        for menu in menu_elems:
            try:
                price = menu.find_element(By.CLASS_NAME, "menu_price").text
                price = int(price.replace(",", "").replace("원", ""))
                prices.append(price)
            except:
                continue

        if prices:
            avg_price = sum(prices) // len(prices)
        else:
            avg_price = None

        result.append({
            "상호명": name,
            "1인 평균 가격": avg_price,
            "메뉴 수": len(prices)
        })

    except Exception as e:
        print(f"⚠️ {name} 처리 중 오류 발생: {e}")
        result.append({
            "상호명": name,
            "1인 평균 가격": None,
            "메뉴 수": 0
        })

driver.quit()

# 데이터프레임으로 저장
avg_df = pd.DataFrame(result)
avg_df.to_csv("가게별_1인평균가격.csv", index=False)
print("결과 저장")

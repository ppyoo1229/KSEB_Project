# inha_crawling_util.py
# 네이버 지도에서 가게 상호명을 검색하여 메뉴 이름과 가격을 크롤링하는 함수

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def crawling_get_menus(store_name, driver):
    """
    Parameters:
           - store_name (str): 가게 이름
           - driver (webdriver): Selenium Chrome WebDriver 인스턴스
    """
    # 결과 저장용 딕셔너리 초기화
    menu_data = {
        "place_name": store_name,
        # menu: [(메뉴명1, 가격1), (메뉴명2, 가격2), ...]
        "menu": []
    }

    # 1. 네이버 지도에서 가게명 검색
    driver.get("https://map.naver.com/v5/search/" + store_name)
    time.sleep(2.5)  # 페이지 로딩 대기

    # 2. 검색결과가 들어 있는 iframe 진입
    try:
        WebDriverWait(driver, 2).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe"))
        )
    except TimeoutException:
        print("searchIframe 로딩 실패")
        return menu_data

    # 3. 검색 결과 리스트 로딩 대기
    try:
        container = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="_pcmap_list_scroll_container"]/ul'))
        )
    except TimeoutException:
        print("검색 리스트 컨테이너 로딩 실패")
        return menu_data

    # 4. 결과 리스트에서 첫 번째 가게 클릭
    buttons = container.find_elements(By.TAG_NAME, 'a')
    if not buttons:
        print("검색 결과 없음")
        return menu_data

    first_btn_class = buttons[0].get_attribute("class")
    if "place_thumb" in first_btn_class and len(buttons) > 1:
        buttons[1].send_keys(Keys.ENTER)
    else:
        buttons[0].send_keys(Keys.ENTER)

    # 5. 상세 페이지 iframe으로 전환
    driver.switch_to.default_content()
    try:
        entry_iframe = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "entryIframe"))
        )
        driver.switch_to.frame(entry_iframe)
    except TimeoutException:
        print("entryIframe 로딩 실패")
        return menu_data

    # 6. 메뉴 섹션 로딩 유도 (스크롤)
    driver.execute_script("window.scrollTo(0, 700)")
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.place_section.Sv9Ys"))
        )
    except TimeoutException:
        print("메뉴 섹션 로딩 실패")
        return menu_data

    # 7. 사진 포함 메뉴 (ul.t1osG > li.ipNNM)
    photo_menu_list = driver.find_elements(By.CSS_SELECTOR, "ul.t1osG")
    if photo_menu_list:
        li_elements = photo_menu_list[0].find_elements(By.CSS_SELECTOR, "li.ipNNM")
        for li in li_elements:
            menu_name = li.find_element(By.CSS_SELECTOR, "span.VQvNX").text
            menu_price = li.find_element(By.CSS_SELECTOR, "div.gl2cc").text
            menu_data["menu"].append((menu_name, menu_price))
        return menu_data

    # 8. 사진 없는 텍스트 메뉴 (ul.jnwQZ > li.gHmZ_)
    text_menu_list = driver.find_elements(By.CSS_SELECTOR, "ul.jnwQZ")
    if text_menu_list:
        li_elements = text_menu_list[0].find_elements(By.CSS_SELECTOR, "li.gHmZ_")
        for li in li_elements:
            menu_name = li.find_element(By.CSS_SELECTOR, "div.ds3HZ a").text
            menu_price = li.find_element(By.CSS_SELECTOR, "div.mkBm3").text
            menu_data["menu"].append((menu_name, menu_price))
        return menu_data

    # 9. 메뉴 정보가 없을 경우
    print("메뉴 정보 없음")
    return menu_data

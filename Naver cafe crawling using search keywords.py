#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
from selenium import webdriver
import csv
import pandas as pd
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Naver login url / your id / your passward
url='https://nid.naver.com/nidlogin.login'
id_ = 'your id'
pw = 'your password'
    
browser = webdriver.Chrome()
browser.get(url)

browser.implicitly_wait(2)

# Naver login 네이버 로그인
browser.execute_script("document.getElementsByName('id')[0].value=\'"+ id_ + "\'")
browser.execute_script("document.getElementsByName('pw')[0].value=\'"+ pw + "\'")
browser.find_element(by=By.XPATH,value='//*[@id="log.login"]').click()
time.sleep(1)
    
# wanted naver cafe url
baseurl='https://cafe.naver.com/(your cafe id)'

# wanted keyword list
Search_Keyword = ['a','b','c']

results = []

for search_key in Search_Keyword:
    # Connecting Naver Cafe 네이버 카페 접속
    browser.get(base_url)

    # Input search keyword 검색어 입력
    search_box = browser.find_element(By.ID, "topLayerQueryInput")
    search_box.send_keys(search_key)

    # Click search box 검색 버튼 클릭
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    
    # driver창의 frame 을 iframe의 태그인 cafe_main으로 바꿔주기
    browser.switch_to.frame("cafe_main")

    # Click Dropdown menu 검색 옵션 드롭다운 메뉴 클릭
    search_option_dropdown = browser.find_element(By.ID, "divSearchByTop")
    search_option_dropdown.click()
    time.sleep(1)

    # Select option 'only title' '제목만' 옵션 선택
    title_only_option = browser.find_element(
        By.XPATH, "//a[contains(text(), '제목만')]")
    title_only_option.click()
    time.sleep(2)

    # Click search box 검색 버튼 클릭
    search_btn = browser.find_element(
        By.XPATH, "//button[contains(text(), '검색')]")
    search_btn.click()
    time.sleep(2)

    # Select option 'get 50 posts each' (1)/ "50개씩" 보기 옵션을 선택하기 위한 드롭다운 메뉴 클릭
    dropdown_menu = browser.find_element(By.ID, "listSizeSelectDiv")
    dropdown_menu.click()
    time.sleep(1)  # 드롭다운 메뉴 옵션들이 표시될 때까지 대기

    # Select option 'get 50 posts each' (2)/"50개씩" 옵션 선택
    fifty_option = browser.find_element(
        By.XPATH, "//a[contains(text(), '50개씩')]")
    fifty_option.click()
    time.sleep(2)  # 옵션 선택 후 페이지 로딩 대기

    # BeautifulSoup으로 HTML을 파싱
    soup = bs(browser.page_source, 'html.parser')

    # 해당 class를 가진 모든 게시글 링크들을 찾음
    article = soup.select('div.inner_list a.article')
    titles = [link.text.strip() for link in article]
    links = [link['href'] for link in article]
    # pp.pprint(article)

    for title, link in zip(titles, links):
        retries = 1 # how many retries / 해당 글을 몇번 들어갈건지 선정
        success = False # 글 접속 성공여부

        while retries > 0 and not success:
            # 게시글의 링크로 이동
            browser.get('https://cafe.naver.com' + link)
            time.sleep(3)
            browser.switch_to.frame("cafe_main")

            # 해당 페이지의 HTML 소스 가져오기
            page_source = browser.page_source

            # BeautifulSoup으로 HTML 파싱
            soup_article = bs(page_source, 'html.parser')

            # Date
            date = soup_article.find('div', class_='article_info').find('span', class_='date').text.strip()

            # Nickname
            nickname_div = soup_article.find('div', class_='article_writer')
            nickname_strong = nickname_div.find('strong', class_='user')
            nickname = nickname_strong.text.strip()
            
            # Writer ID is private
            
            # Post number
            post_num = int(soup_article.find('div', class_='text_area').find(class_='naver-splugin').get('data-url').split('/')[-1])
        
            # 가격 정보 추출
            #price_div = soup_article.find('div', class_='ProductPrice')
            #if price_div:
            #    price_strong = price_div.find('strong', class_='cost')
            #    if price_strong:
            #        price = price_strong.text.strip()
            #        success = True  # 정보를 성공적으로 가져왔음
            #    else:
            #        price = '가격 정보 없음1'
            #else:
            #    price = '가격 정보 없음2'
            retries -= 1  # 재시도 횟수 감소

        results.append({
            'Title': title,
            'Post number': post_num,
            'Date': date,
            'Nickname': nickname,
            'Link': 'https://cafe.naver.com' + link
        })
# DataFrame으로 변환 후 CSV 파일로 저장
df = pd.DataFrame(data=results)
df.to_csv("data3_test.csv", index=True, encoding="utf-8-sig")


#!/usr/bin/env python
# coding: utf-8

# In[4]:


import time
from selenium import webdriver
import csv
import pandas as pd
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from urllib.request import urlretrieve
import os

df = pd.DataFrame([],columns=["title","Post number","Date","ID","Nickname","Image Link","Image save path","Commenter ID","Commenter Nickname",
        "Comment","Comment Date","Reply ID","Reply Nickname","Reply","Reply Date",],)

# driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options)

# Naver login url / your id / your passward
url='https://nid.naver.com/nidlogin.login'
id_ = 'your id'
pw = 'your password'
    
driver.get(url)
driver.implicitly_wait(1)

# Naver login 네이버 로그인
driver.execute_script("document.getElementsByName('id')[0].value=\'"+ id_ + "\'")
driver.execute_script("document.getElementsByName('pw')[0].value=\'"+ pw + "\'")
driver.find_element(by=By.XPATH,value='//*[@id="log.login"]').click()
time.sleep(1)
    
# wanted naver cafe url
baseurl='https://cafe.naver.com/(name of naver cafe)/'
clubid = '(write club id number)' # what is your naver cafe's clubid? / 네이버 카페 클럽 아이디 입력

# login time you should login within 2 sec
time.sleep(1)

# ASSUME LOGIN  SUCCESS
num_page = 2  # how many pages do you want? / 총 페이지 수

##########################################################################
# do not touch
page = 0
index = 0

while page < num_page:
    driver.get("https://cafe.naver.com/ArticleList.nhn?search.clubid="+str(clubid)+"&search.boardtype=L&search.totalCount=151&search.cafeId="+str(clubid)+"&search.page="+ str(page + 1))
    driver.switch_to.frame("cafe_main")
    
    time.sleep(1)  # 페이지 로딩 시간
    driver.implicitly_wait(1)
   
    # BeautifulSoup으로 HTML을 파싱
    driver_page_source = driver.page_source
    soup = bs(driver_page_source, 'html.parser')

    # 해당 class를 가진 모든 게시글 링크들을 찾음
    article = soup.find_all(class_="inner_list")

    links = []
    post_num_list = []
    find_one = 0
    for idx, link in enumerate(article):
        idid = link.find(class_='article')['href'].split('articleid=')[-1]
        if idid[-1] == 'e':
            if find_one == 0:
                find_idx = idx
                find_one += 10
            idid = idid.split('&')[0]
        post_num_list.append(int(idid))
        links.append(baseurl + idid)

    wow_gongi = pd.read_html(driver_page_source)[0].iloc[[_ for _ in range(0,len(pd.read_html(driver_page_source)[0]),2)],[1,2,3,4]]
    wow_gongi = wow_gongi.reset_index(drop=True)
    wow_gongi.iloc[:,1] = wow_gongi.iloc[:,1].str.split('w').str[0]
    
    text_column = wow_gongi.columns
    
    wow = pd.read_html(driver_page_source)[find_idx+1].iloc[[_ for _ in range(0,len(pd.read_html(driver_page_source)[find_idx+1]),2)],[1,2,3,4]]
    wow = wow.reset_index(drop=True)
    wow.iloc[:,1] = wow.iloc[:,1].str.split('w').str[0]
    wow.columns = text_column
    
    wow = pd.concat([wow_gongi, wow], axis=0)
    wow = pd.concat([wow.reset_index(drop=True), pd.DataFrame({'번호': post_num_list})], axis=1)
    wow = pd.concat([wow, pd.DataFrame({'링크': links})], axis=1)
    
    idx_wow = 0
    while idx_wow < len(wow):
        print(page + 1, "번 페이지", idx_wow + 1, "번째 게시물")
        post_num = wow.iloc[idx_wow,4]
        print('글 번호:',post_num)          
        driver.get(wow.iloc[idx_wow,5])
        driver.switch_to.frame("cafe_main")
        time.sleep(1)
        driver.implicitly_wait(1)
        
        # BeautifulSoup으로 HTML을 파싱
        another_soup = bs(driver.page_source, 'html.parser')

        # 해당 class를 가진 모든 게시글 링크들을 찾음
        another_article = another_soup.find_all(class_="inner_list")     
        
        # Title
        title = driver.find_element(By.CLASS_NAME, "title_text").text

        # Date
        date = driver.find_element(By.CLASS_NAME, "date").text

        # Nickname
        nickname = driver.find_element(By.CLASS_NAME, "nickname").text

        # Writer ID
        writer_info = driver.find_element(By.CLASS_NAME, "thumb").get_attribute("href")
        writer_id = ""
        if "members/" in writer_info:
            writer_id = writer_info[writer_info.index("members/") + 8 :]

        # Image link
        image_list = driver.find_elements(By.CLASS_NAME, "se-image-resource")

        image = """"""
        image_dir = """"""
        count = 0
        
        if not os.path.isdir("save_images"):
            os.mkdir("save_images")
        
        for im in image_list:
            url = im.get_attribute("src")
            lcs_add = "save_images/img_" + str(index) + "_" + str(count + 1) + ".jpg"
            urlretrieve(url, lcs_add)  # download image into directory

            image_dir += "save_images/img_" + str(index) + "_" + str(count + 1) + ".jpg"
            image_dir += "\n"

            image += im.get_attribute("src")
            image += "\n"
            count += 1

        # Nickname of commenter & Comment
        comtemp_list = another_soup.find_all('span', {'class':'text_comment'})
        commenter_1_list = []
        comment_1_list = []
        comment_time_1_list = []
        commenter_id_1_list = []
        for idx in range(len(comtemp_list)):
            another_soup_find_all_div_class_comment_area = another_soup.find_all('div', {'class':'comment_area'})[idx]
            commenter = another_soup_find_all_div_class_comment_area.find_all('a', {'aria-expanded':'false'})[0].text.strip()
            comment = another_soup_find_all_div_class_comment_area.find_all('span', {'class':'text_comment'})[0].text
            comment_time = another_soup_find_all_div_class_comment_area.find_all('span', {'class':'comment_info_date'})[0].text   
            
            commenter_1_list.append(commenter)
            comment_1_list.append(comment)
            comment_time_1_list.append(comment_time)
            
            # Commenter ID
            comment_id = another_soup_find_all_div_class_comment_area.find_all('a', {'class':'comment_thumb'})[0]['href'].split('/')[-1]
            commenter_id_1_list.append(commenter_id)
                
        if len(comtemp_list) == 0:
            commenter_1_list.append("NO COMMENT")
            comment_1_list.append("NO COMMENT")
            comment_time_1_list.append("NO COMMENT")
            commenter_id_1_list.append("NO COMMENT")

        if idx_wow < len(wow) - 1:
            idx_wow += 1
        else:
            print("ALL posts comsumed\nGO TO NEXT PAGE")
            page += 1
            idx_wow = 0            
            
            driver.get("https://cafe.naver.com/ArticleList.nhn?search.clubid="
               +str(clubid)
               +"&search.boardtype=L&search.totalCount=151&search.cafeId="
               +str(clubid)
               +"&search.page="
               + str(page + 1))
            driver.switch_to.frame("cafe_main")
    
            time.sleep(1)  # 페이지 로딩 시간
            driver.implicitly_wait(1)
            print(page + 1, " 번 페이지", idx_wow + 1, "번째 게시물")
            #############################################
            
            # BeautifulSoup으로 HTML을 파싱
            driver_page_source = driver.page_source
            soup = bs(driver_page_source, 'html.parser')

            # 해당 class를 가진 모든 게시글 링크들을 찾음
            article = soup.find_all(class_="inner_list")

            links = []
            post_num_list = []
            find_one = 0
            for idx, link in enumerate(article):
                idid = link.find(class_='article')['href'].split('articleid=')[-1]
                if idid[-1] == 'e':
                    if find_one == 0:
                        find_idx = idx
                        find_one += 10
                    idid = idid.split('&')[0]
                post_num_list.append(int(idid))
                links.append(baseurl + idid)
            
            wow = pd.read_html(driver_page_source)[1].iloc[[_ for _ in range(0,len(pd.read_html(driver_page_source)[1]),2)],[1,2,3,4]]
            wow = wow.reset_index(drop=True)
            wow.iloc[:,1] = wow.iloc[:,1].str.split('w').str[0]
            wow.columns = text_column
            wow = pd.concat([wow.reset_index(drop=True), pd.DataFrame({'번호': post_num_list})], axis=1)
            wow = pd.concat([wow, pd.DataFrame({'링크': links})], axis=1)

        # Go to main page to track reply page
        driver.get("https://cafe.naver.com/ArticleList.nhn?search.clubid="
                   +str(clubid)
                   +"&search.boardtype=L&search.totalCount=151&search.cafeId="
                   +str(clubid)
                   +"&search.page="
                   + str(page + 1))
        driver.switch_to.frame("cafe_main")
        time.sleep(1)
        driver.implicitly_wait(1)

        # Reply Test
        # if not a reply, visit again
        driver.get(wow.iloc[idx_wow,5])
        driver.switch_to.frame("cafe_main")
        driver.implicitly_wait(1)
        time.sleep(1)

        # reply title
        reply_title = driver.find_element(By.CLASS_NAME, "title_text").text

        # Reply if title = reply_title
        if title == reply_title:
            print("It's reply")
            reply_date = driver.find_element(By.CLASS_NAME, "date").text
            reply_nickname = driver.find_element(By.CLASS_NAME, "nickname").text
            reply_text = """"""  # se-fs- se-ff-
            for info in driver.find_elements(By.CSS_SELECTOR, ".se-fs-.se-ff-"):
                reply_text += info.text
                reply_text += " "

            # Reply ID
            reply_info = driver.find_element(By.CLASS_NAME, "thumb").get_attribute("href")
            reply_id = ""
            if "members/" in reply_info:
                reply_id = reply_info[reply_info.index("members/") + 8 :]

            # To the next page
            idx_wow += 1
        else:
            print("It's NOT reply. Stay on the same page")
            reply_date = "No reply"
            reply_nickname = "No reply"
            reply_text = "No reply"
            reply_id = "No reply"

        # 16 columns
        df.loc[index] = [title,post_num,date, writer_id, nickname, image, image_dir, commenter_id_1_list, commenter_1_list, comment_1_list, comment_time_1_list, reply_id, reply_nickname, reply_text, reply_date,        ]
        df.to_csv(r"test.csv",encoding="utf-8-sig",index=False,)
        
        # Go to main page
        driver.get("https://cafe.naver.com/ArticleList.nhn?search.clubid="+str(clubid)+"&search.boardtype=L&search.totalCount=151&search.cafeId="+str(clubid)+"&search.page="+ str(page + 1))
        driver.implicitly_wait(1)
        driver.switch_to.frame("cafe_main")
        time.sleep(1)
        index += 1
        if page >= num_page:
            break

print(df)


# In[ ]:

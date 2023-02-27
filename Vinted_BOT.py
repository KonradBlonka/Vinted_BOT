from selenium import webdriver as wd
import chromedriver_binary
import time
from bs4 import BeautifulSoup
import pandas as pd

wd = wd.Chrome() #open cart
wd.implicitly_wait(10) #wait 10 secons
wd.get("https://accounts.google.com/o/oauth2/auth/identifier?access_type=offline&client_id=370947398364-4ei5612p3evupc6qm8frglhfk356l7ib.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fwww.vinted.pl%2Fmember%2Fsignup%2Fselect_type&response_type=code&scope=email%20profile&state=%2F&service=lso&o2v=1&flowName=GeneralOAuthFlow")

time.sleep(5)

login = wd.find_element_by_id("identifierId").send_keys("**********") #in place of stars type mail
netx_button1 = wd.find_element_by_xpath("//*[@id='identifierNext']/div/button/span").click()
time.sleep(2)
password = wd.find_element_by_name("password").send_keys("*******") #in place of stars type password
next_button2 = wd.find_element_by_xpath("//*[@id='passwordNext']/div/button/span").click()

wd.implicitly_wait(5)
wd.get("https://www.vinted.pl/vetements?search_text=&currency=PLN&search_id=8365236945&order=newest_first&catalog[]=1904&catalog[]=5&time=1677077795")
soup = BeautifulSoup(wd.page_source)

#find price, title, and url link
def FindResults(searchPage):
    rows = []
    for result in searchPage:
        title = result.find("div", {"class": "web_ui__ItemBox__details"})
        price = result.find("div", {"class": "web_ui__ItemBox__title-content"})
        url = result.find("a", {"class": "web_ui__ItemBox__overlay"})
        if price:
            row = [title.text, price.text, url['href']]
        rows.append(row)

    df = pd.DataFrame.from_records(rows, columns=['Title', 'Price', 'URL'])
    return df

#find elements from FindResults on next pages
def PageSearch(url):
    wd.get(url)
    i = 1
    df_all_search_results = pd.DataFrame(columns=['Title', 'Price', 'URL'])
    while i<5:  #search 5 cards 
        searchPage = soup.findAll("div", {"class": "feed-grid__item feed-grid__item--native_aspect_ratio"})
        df = FindResults(searchPage)
        df_all_search_results = pd.concat([df_all_search_results, df])

        nextPageLink = wd.find_element_by_class_name('web_ui__Pagination__next')
        nextPageLink.click()
        i += 1

        time.sleep(5)
    if i == 5:
        print("END OF SEARCH")
        
    #change price string to float
    df_all_search_results['Price'] = df_all_search_results['Price'].str.replace(",",".")
    df_all_search_results['Price'] = df_all_search_results['Price'].str.replace("\xa0zł","")
    df_all_search_results['Price'] = df_all_search_results['Price'].astype(float)  
    
    return df_all_search_results


while True:
    df = PageSearch("https://www.vinted.pl/vetements?search_text=&currency=PLN&search_id=8365236945&order=newest_first&catalog[]=1904&catalog[]=5&time=1677077795")
    df_filtr = df[(df.Price >= 0) & (df.Title.str.contains("Nike"))]
    
    if (not df_filtr.empty):
        print("U WILL LIKE THIS")
        print(df_filtr)
        break
    else:
        time.sleep(60)
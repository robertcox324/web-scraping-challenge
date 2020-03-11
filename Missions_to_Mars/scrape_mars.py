from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from pprint import pprint
import time

def openWebpage():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    mars_scraped = {}

    # Maybe put in time.sleep(1) or something after each url access to allow it all to load
    
    #Mars news access (part 1)
    url = 'https://mars.nasa.gov/news/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    results = soup.find('div', class_="content_title") #only need the first result
    news_title = results.text.strip() #use .strip() to get rid of empty space before and after
    #have to do a different seach for the body paragraph since not part of the same easy body or anything
    results = soup.find('div', class_="rollover_description_inner")
    news_p = results.text.strip()
    #add the result of each scrape to the dictionary for the results
    mars_scraped["News_Title"] = news_title
    mars_scraped["News_Text"] = news_p
    
    #Mars Space image (part 2)
    browser = openWebpage() #open up the browser
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(1)
    soup = BeautifulSoup(browser.html, 'lxml')
    imgUrl = "https://www.jpl.nasa.gov"
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(1)
    html = browser.html
    soup = BeautifulSoup(html, 'lxml')
    img = soup.find('img', class_="fancybox-image")
    full_img_url = imgUrl + img['src']
    mars_scraped["Space_Image"] = full_img_url
    browser.quit #close out of the browser when it's finished its job
    
    #Mars Weather Twitter (part 3)
    browser = openWebpage()
    browser.visit("https://twitter.com/marswxreport?lang=en")
    time.sleep(1)
    html = requests.get("https://twitter.com/marswxreport?lang=en").text
    soup = BeautifulSoup(html, 'lxml')
    try:
        tweet = soup.find_all('div', class_="js-tweet-text-container")
        i = 0
        for tweets in tweet:
            if "InSight" in tweet[i].text:
                tweetText = tweet[i].text.split("pic")[0]
                break
            i += 1
        mars_scraped["Weather_Tweet"] = tweetText
    except:
        mars_scraped["Weather_Tweet"] = "Mars weather tweet not found"
    browser.quit
    
    #Mars Facts (part 4)
    tables = pd.read_html("https://space-facts.com/mars/")
    #instead of each column and row being numbers with no description, let's change that
    marsHtml = tables[0]
    marsHtml.columns = ["Mars Fact", "Value"]
    mars_scraped["Mars_Facts_Html"] = marsHtml.to_html()
    
    #Mars Hemiphere Photos (part 5)
    browser = openWebpage()
    browser.visit("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
    soup = BeautifulSoup(browser.html, 'lxml')
    imgUrl = "https://astrogeology.usgs.gov"
    MarsHemispheres = [] #list to append the dictionaries to
    for i in range(4):
        images = browser.find_by_tag('h3') #only the links we want are using an h3 tag
        images[i].click()
        time.sleep(1)
        html = browser.html
        soup = BeautifulSoup(html, 'lxml')
        img = soup.find("img", class_="wide-image")["src"] #the images we want are the src of img files with class wide-image
        title = soup.find("h2", class_="title").text.split("Enhanced")[0] #find the title of the hemisphere, and remove the "Enhanced" description for the image
        full_img_url = imgUrl + img
        Hemisphere={"title":title,"img url":full_img_url}
        MarsHemispheres.append(Hemisphere)
        browser.back()
    mars_scraped["MarsHemispheres"] = MarsHemispheres
    browser.quit
    
    return mars_scraped
    
# test = scrape()
# print(test["News_Title"])

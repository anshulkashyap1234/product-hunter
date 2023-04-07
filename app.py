
from flask import Flask, render_template, request, redirect, url_for, flash,send_file
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
import concurrent.futures
#create flask app
app = Flask(__name__)

#create home window
@app.route("/")
def home():
    return render_template("home.html")

#get data from text field
@app.route('/gettext', methods=["POST"])
def gettext():
    


    def fetch_data_amazon():
        driver = webdriver.Chrome()
        driver.get("https://www.amazon.in/")

        # We use .find_element_by_id here because we know the id

        text_input = driver.find_element("id", "twotabsearchtextbox")

        text_input.send_keys(object)

        text_input.submit()

        time.sleep(5)
        driver.page_source
        tag = BeautifulSoup(driver.page_source, "html.parser")


        object_name = tag.findAll(
                "span", {'class': 'a-size-medium a-color-base a-text-normal'})
        object_price = tag.findAll("span", {'class': 'a-price-whole'})
        object_link = tag.findAll("a", {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        object_img = tag.findAll("div", {'class': 'a-section aok-relative s-image-fixed-height'})
        object_review = tag.findAll("div", {'class': 'a-row a-size-small'})

        d = []
        for i in zip(object_name, object_price, object_link, object_img, object_review):
                d.append({"object_name": i[0].getText(), "object_price": float(i[1].getText().replace(
                    '₹', '').replace(',', '')), "object_link": "https://www.amazon.in"+i[2]['href'], "object_img": i[3].find("img").get("src"), "object_details": "", "object_review": i[4].find('span').get('aria-label')})

        if d == []:

                df="ivalid input please enter a valid input"


        else:

                df = pd.DataFrame(d)  
        return df
    #flipkart
    def second_fetch_data(tag):
        d = []
        

        object_price = tag.findAll("div", {'class': '_30jeq3'})
        object_name = [div["title"]
                    for div in tag.find_all("a", attrs={"class": "s1Q9rs"})]
        object_link = tag.find_all('a', {'class': 's1Q9rs'})
        object_review = tag.findAll("span", {'class': '_2_R_DZ'})
        object_img = tag.findAll("div", {'class': 'CXW8mj'})

        d = []
        for i in zip(object_name, object_price, object_link, object_img, object_review):
            d.append({"object_name": i[0], "object_price": float(i[1].getText().replace(
                '₹', '').replace(',', '')), "object_link": "https://www.flipkart.com"+i[2]['href'], "object_img": i[3].find("img").get("src"), "object_details": "", "object_review": i[4].getText()})

        return d


    def fetch_data_flipkart():
        driver = webdriver.Chrome()
        
        driver.get("https://www.flipkart.com/")

        text_input = driver.find_element("name", "q")

        # Then we'll fake typing into it
        text_input.send_keys(object)


        # Now we can grab the search button and click it


        text_input.submit()

        time.sleep(5)
        # Instead of using requests.get, we just look at .page_source of the driver
        driver.page_source
        tag = BeautifulSoup(driver.page_source, "html.parser")

        object_name = tag.findAll("div", {'class': '_4rR01T'})
        object_price = tag.findAll("div", {'class': '_30jeq3 _1_WHN1'})
        object_link = tag.find_all('a', {'class': '_1fQZEK'})
        object_img = tag.findAll("div", {'class': 'CXW8mj'})
        object_review = tag.findAll("span", {'class': '_2_R_DZ'})

        object_details = tag.findAll("div", {'class': 'fMghEO'})
        d = []
        for i in zip(object_name, object_price, object_link, object_img, object_details, object_review):
            d.append({"object_name": i[0].getText(), "object_price": float(i[1].getText().replace(
                '₹', '').replace(',', '')), "object_link": "https://www.flipkart.com"+i[2]['href'], "object_img": i[3].find("img").get("src"), "object_details": i[4].getText().split('|'), "object_review": i[5].getText()})

        if d == []:
            d = second_fetch_data(tag)
            data = pd.DataFrame(d)

        else:
            data = pd.DataFrame(d)

        return data

        

#get text data from text tag
    name=['amazon','flipkart']
    object=request.form['text_data']
    
    object_filter=object.split(" ")
    object_filters='.'.join(object_filter)
#connect to a web
    
#call amazon function
   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        amazon_data = executor.submit(fetch_data_amazon)
        flipkart_data = executor.submit(fetch_data_flipkart)
    try:
        amazon_data = amazon_data.result()
        flipkart_data = flipkart_data.result()
    except :
        return render_template('home.html', error="invalid input please enter a valid input 1")


    try:

#add one more column to identify which values is match to pattern in dataframe
        global amazon_data_filter
        amazon_data_filter = amazon_data[amazon_data['object_name'].str.lower().str.contains(object_filters,regex=True)]
        global flipkart_data_filter
        flipkart_data_filter =flipkart_data[flipkart_data['object_name'].str.lower().str.contains(object_filters,regex=True)]

        #drop none rows from database
        
    
        # doing empty dataframes
        
        #drop none columns from dataframe
        
       
        # get min price object from dataframe of amazon
        amazon_best_offer=amazon_data_filter[amazon_data_filter['object_price']==amazon_data_filter['object_price'].min()]
        # get min price object from dataframe of flipkart
        flipkart_best_offer=flipkart_data_filter[flipkart_data_filter['object_price']==flipkart_data_filter['object_price'].min()]


    except:
        return render_template('home.html', error="invalid input please enter a valid input 2")



    
    try:
        price_amazon =float(amazon_best_offer['object_price'].min())
        price_flipkart =float(flipkart_best_offer['object_price'].min())
        if (price_amazon < price_flipkart):
            name=amazon_best_offer.iloc[0,0]
            price=amazon_best_offer.iloc[0,1]
            link=amazon_best_offer.iloc[0,2]
            img=amazon_best_offer.iloc[0,3]
            rating =amazon_best_offer.iloc[0,5]
            e_name="amazon"
        else:
                name=flipkart_best_offer.iloc[0,0]
                price=flipkart_best_offer.iloc[0,1]
                link=flipkart_best_offer.iloc[0,2]
                img=flipkart_best_offer.iloc[0,3]
                rating =flipkart_best_offer.iloc[0,5]
                e_name="flipkart"
        
       
        flip=[]
        for i in range(len(flipkart_data_filter)):
            flip.append(flipkart_data_filter.iloc[i,0:].values.tolist())
        amaz=[]
        for i in range(0,len(amazon_data_filter)):
            amaz.append(amazon_data_filter.iloc[i,0:].values.tolist())

        return render_template('home_img.html', flipkart=flip,amazon=amaz,name=name,price=price,link=link,img=img,rating=rating,e_name=e_name)
   
   
    except:
       
            if(len(amazon_data)<=2 and len(flipkart_data)<=2):
                return render_template('home.html', error="invalid input please enter a valid input3")

            else:
                table_amazon=amazon_data_filter.to_html()
                table_flipkart=flipkart_data_filter.to_html()
                return  render_template('home_not_img.html',table_amazon=table_amazon,table_flipkart=table_flipkart)

@app.route('/get_trans_history')
def get_trans_history():
    
    
    df=pd.concat([amazon_data_filter,flipkart_data_filter])
    df.drop(columns=['object_img'],inplace=True)
    df.to_excel("userinformation\\transfer.xlsx")
    p="userinformation\\transfer.xlsx"
    return send_file(p,as_attachment=True)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("/error page/404.html"), 404

#internal server
@app.errorhandler(500)
def page_not_found(e):
    return render_template("/error page/500.html",error="server not running"), 500



if __name__ == "__main__":
    app.run(debug=True)

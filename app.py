
from flask import Flask, render_template, request, redirect, url_for, flash
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
    # find pattern in dataframe
    def split_it(data):
        obj=object
        obj=obj.strip().split(" ")
        pattern=""
        for i in obj[1:-1]:
            pattern=pattern+'*'+i+'.'
        pattern=f"{obj[0]}.{pattern}{obj[-1]}"
        x = re.findall(pattern, data)
        if x :
            return x


#fetch data from amazon 
    def fetch_data_amazon():
        driver = webdriver.Chrome()
    
        # data fetch from amazon
    # call website
        driver.get("https://www.amazon.in/")
    #find input element of website
        text_input = driver.find_element("id", "twotabsearchtextbox")
    #enter value in input element
        text_input.send_keys(object)
    # submit event
        text_input.submit()
    #wait for 2 second to fetch data
        time.sleep(2)
        img_tag = BeautifulSoup(driver.page_source, "html.parser")
        global image
        image = img_tag.find(
                "img", {'class': 's-image'})
        image=image['src']
        tag = BeautifulSoup(driver.page_source, "html.parser")

        mobile_name = tag.findAll(
            "span", {'class': 'a-size-medium a-color-base a-text-normal'})
        mobile_price = tag.findAll("span", {'class': 'a-price-whole'})
        mobile_link = tag.findAll("a", {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
    
        list1=[]

        for i in mobile_link:

            str="https://www.amazon.in/"+i['href']
            list1.append(str)
        d = []
        for i in zip(mobile_name, mobile_price,list1):
            d.append({"mobilename": i[0].getText(), "mobile_price": float(i[1].getText().replace(
                '₹', '').replace(',', '')),"mobilelink":i[2]})
    

        data = pd.DataFrame(d)
        return data
# fetch data from flipkart if first fuction will not work
        
# fetch data from flipkart
    def second_fetch_data(tag):
        soup = tag

        mobile_name = [div["title"]
                    for div in soup.find_all("a", attrs={"class": "s1Q9rs"})]
        mobile_price = soup.findAll("div", {'class': '_30jeq3'})
        mobile_link=soup.find_all('a',{'class':'s1Q9rs'})
        list1=[]
        d=[]
        for i in mobile_link:

            str="https://www.flipkart.com"+i['href']
            list1.append(str)
        for i in zip(mobile_name, mobile_price,list1):
            d.append({"mobilename": i[0], "mobile_price": float(i[1].getText().replace(
                '₹', '').replace(',', '')),'mobilelink':i[2]})

                
        return d
    def fetch_data_flipkart():
        driver = webdriver.Chrome()
        driver.get("https://www.flipkart.com/")

        text_input = driver.find_element("name", "q")

        text_input.send_keys(object)

        text_input.submit()
        
        time.sleep(2)

        tag = BeautifulSoup(driver.page_source, "html.parser")

        mobile_name = tag.findAll("div", {'class': '_4rR01T'})
        mobile_price = tag.findAll("div", {'class': '_30jeq3 _1_WHN1'})
        d = []
        mobile_link=tag.find_all('a',{'class':'_1fQZEK'})
        list1=[]
        for i in mobile_link:

            str="https://www.flipkart.com"+i['href']
            list1.append(str)
        for i in zip(mobile_name, mobile_price,list1):
            d.append({"mobilename": i[0].getText(), "mobile_price": float(i[1].getText().replace(
                '₹', '').replace(',', '')),"mobilelink":i[2]})
        if d == []:
            d = second_fetch_data(tag)
            data = pd.DataFrame(d)

        else:
            data = pd.DataFrame(d)

        return data

#get text data from text tag
    name=['amazon','flipkart']
    object=request.form['text_data']

#connect to a web
    
#call amazon function
   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        amazon_data = executor.submit(fetch_data_amazon)
        flipkart_data = executor.submit(fetch_data_flipkart)
    try:
        amazon_data = amazon_data.result()
        flipkart_data = flipkart_data.result()
    except:
        return render_template('home.html', error="invalid input please enter a valid input")




#add one more column to identify which values is match to pattern in dataframe
    amazon_data['Season2'] = amazon_data['mobilename'].str.lower().apply(split_it)
    flipkart_data['Season2'] =flipkart_data['mobilename'].str.lower().apply(split_it)

    #drop none rows from database
    amazon_deal_offer=amazon_data.dropna()
   
    flipkart_deal_offer=flipkart_data.dropna()
   
    # doing empty dataframes
    
    #drop none columns from dataframe
    
    flipkart_deal_offer.drop(['Season2'],axis=1,inplace=True)
    flipkart_data.drop(['Season2'],axis=1,inplace=True)
    amazon_deal_offer.drop(['Season2'],axis=1,inplace=True)
    amazon_data.drop(['Season2'],axis=1,inplace=True)
    # get min price object from dataframe of amazon
    amazon_best_offer=amazon_deal_offer[amazon_deal_offer['mobile_price']==amazon_deal_offer['mobile_price'].min()]
    # get min price object from dataframe of flipkart
    flipkart_best_offer=flipkart_deal_offer[flipkart_deal_offer['mobile_price']==flipkart_deal_offer['mobile_price'].min()]




    
    try:
        price_amazon =float(amazon_best_offer['mobile_price'].min())
        price_flipkart =float(flipkart_best_offer['mobile_price'].min())
        if (price_amazon < price_flipkart):
            best_deal=amazon_best_offer
            webname="amazon"
        elif (price_amazon > price_flipkart):
                best_deal=flipkart_best_offer
                webname="flipkart"
        else:
            best_deal=pd.concat(amazon_best_offer,flipkart_best_offer)
            webname="both have some"
        lis=[]
        for i in best_deal.itertuples():
            lis.append(i)
                
                
            return render_template('home_img.html', tables_amazon=[amazon_deal_offer.to_html(classes='amazon_data')], tables_flipkart=[flipkart_deal_offer.to_html(classes='flipkart_data')],best_item=lis[0][1],best_price=f"Price {lis[0][2]}rs",link=lis[0][3],webname=f"the best deal for you is on {webname}",image=image,show="show",name=name)
   
   
    except:
       
            if(len(amazon_data)==0 and len(flipkart_data)==0):
                return render_template('home.html', error="invalid input please enter a valid input")

            else:
                return  render_template('home_not_img.html', tables_amazon=[amazon_data.to_html(classes='amazon_data')],tables_flipkart=[flipkart_data.to_html(classes="flipkart_data")],error=" this is similar to your products",name=name)
      



if __name__ == "__main__":
    app.run(debug=True)

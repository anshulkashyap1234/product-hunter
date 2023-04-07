from flask import Flask,render_template
import pandas as pd

hello=Flask(__name__)


@hello.route("/")
def home():
    
  
    flipkart_data_filter=pd.read_excel("flipkartdata.xlsx")
    a=[]
    for i in range(0,len(flipkart_data_filter)):
        a.append(flipkart_data_filter.iloc[i,1:].values.tolist())
    
    return render_template("servicesforuser.html",flipkart=a)











if __name__ == "__main__":
    hello.run(debug=True)
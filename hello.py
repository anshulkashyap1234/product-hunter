from flask import Flask,render_template
import pandas as pd

hello=Flask(__name__)


@hello.route("/")
def home():
    
    
    
     return render_template('home.html')









if __name__ == "__main__":
    hello.run(debug=True)
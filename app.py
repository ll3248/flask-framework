import pandas as pd
import numpy as np
import json
import requests
import bokeh

from flask import Flask, render_template, request, redirect, Markup

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.embed import file_html


def valid_response(stock_ticker): 
	key = "XXX"
	url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(stock_ticker, key)
	response = requests.get(url)
	return response

def stock_dataset(response): 
	df = pd.DataFrame(response.json().get('Time Series (Daily)')).transpose().iloc[::-1]

	df_rename = df.rename(columns={'1. open':'Open',  '2. high':'High',
								   '3. low':'Low', '4. close':'Close', 
                                   '5. adjusted close':'Adjusted_Close', '6. volume':'Volume', 
                                   '7. dividend amount':'Dividend Amount', '8. split coefficient':'Split Coefficient'})
	return pd.DataFrame(df_rename)

def stock_plot(df, adjusted_close_check, open_check, close_check, high_check, low_check): 
	dates = list(df.index)

	x = np.array(dates, dtype=np.datetime64)
	# y = list(pd.to_numeric(stock_record.iloc[:,0]))
	# y = list(pd.to_numeric(stock_record.loc[:,"4. close"]))
	y1 = list(pd.to_numeric(df.Adjusted_Close))
	y2 = list(pd.to_numeric(df.Open))
	y3 = list(pd.to_numeric(df.Close))
	y4 = list(pd.to_numeric(df.High))
	y5 = list(pd.to_numeric(df.Low))

	# create a new plot with a title and axis labels
	p = figure(title="Stock Price Over Time", # THIS VALUE GETS CHANGED DEPENDING ON USER INPUT
	           x_axis_label='Date', 
	           x_axis_type="datetime", 
	           y_axis_label='Price') # THIS VALUE GETS CHANGED DEPENDING ON USER INPUT

	# add a line renderer with legend and line thickness

	if adjusted_close_check == True: 
		p.line(x, y1, legend_label="Adjusted_Close", line_width=2, line_color = "black")
	if open_check == True: 
		p.line(x, y2, legend_label="Open", line_width=2, line_color = "blue")
	if close_check == True: 
		p.line(x, y3, legend_label="Close", line_width=2, line_color = "red")
	if high_check == True: 
		p.line(x, y4, legend_label="High", line_width=2, line_dash = "dashed", line_color = "blue")
	if low_check == True: 
		p.line(x, y5, legend_label="Low", line_width=2, line_dash = "dashed", line_color = "red")
	

	script, div = components(p)

	cdn_js = CDN.js_files
	cdn_css = CDN.css_files

	return script, div, cdn_js, cdn_css



app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/analysis', methods=["POST"])
def analysis():
	
	stock_ticker = str(request.form.get("stock_ticker"))

	response = valid_response(stock_ticker = stock_ticker)

	if not stock_ticker or bool(response.json().get('Time Series (Daily)')) == False: 
		error_message = "You need to specify a proper stock ticker or this ticker does not exist."
		return render_template("fail.html", error_message = error_message, stock_ticker = stock_ticker)

	if request.form.get("adjusted_close"):
		adjusted_close_check = True
	else: 
		adjusted_close_check = False

	if request.form.get("open"):
		open_check = True
	else:
		open_check = False

	if request.form.get("close"):
		close_check = True
	else:
		close_check = False

	if request.form.get("high"):
		high_check = True
	else:
		high_check = False

	if request.form.get("low"):
		low_check = True
	else:
		low_check = False

	stock_record = stock_dataset(response = response)


	div, script, cdn_js, cdn_css = stock_plot(df = stock_record, 
											adjusted_close_check = adjusted_close_check,
											open_check = open_check, close_check = close_check, 
											high_check = high_check, low_check = low_check)


	return render_template("analysis.html", 
		stock_ticker = stock_ticker, 
		script = script, 
		div = div, 
		cdn_js = cdn_js, 
		cdn_css = cdn_css
		)

if __name__ == '__main__':  
  app.run(port=33507)

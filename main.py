import os

from flask import Flask, render_template, request
from google.cloud import datastore
from graphing import data_plot
from table import data_table

app = Flask(__name__)

# Initialize the Datastore client
client = datastore.Client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data_plot')
def graph():
    ticker = request.args.get('ticker')
    industry = request.args.get('industry')
    startmonth = request.args.get('startmonth')
    endmonth = request.args.get('endmonth')
    return data_plot(ticker=ticker, industry=industry, startmonth=startmonth, endmonth=endmonth)

@app.route('/data_table')
def table():
    ticker = request.args.get('ticker')
    industry = request.args.get('industry')
    startmonth = request.args.get('startmonth')
    endmonth = request.args.get('endmonth')
    return data_table(ticker=ticker, industry=industry, startmonth=startmonth, endmonth=endmonth)

@app.route('/submit_company_info', methods=['POST'])
def submit_company_info():
    if request.method == 'POST':
        yahoo_ticker = request.form['yahoo_ticker']
        industry = request.form['industry']
        long_name = request.form['long_name']

        # Check if the Yahoo ticker already exists in the database
        query = client.query(kind='CompanyInfo')
        query.add_filter('YahooTicker', '=', yahoo_ticker)
        results = list(query.fetch(limit=1))

        # If the ticker exists, update the entity
        if results:
            company_entity = results[0]  # Get the existing entity
            company_entity.update({
                'YahooTicker': yahoo_ticker,
                'Industry': industry,
                'LongName': long_name,
            })
            client.put(company_entity)
            return 'Yahoo ticker information updated successfully!'
        else:
            # If the ticker doesn't exist, create a new entity
            key = client.key('CompanyInfo')
            company_entity = datastore.Entity(key=key)
            company_entity.update({
                'YahooTicker': yahoo_ticker,
                'Industry': industry,
                'LongName': long_name,
            })
            client.put(company_entity)
            return 'Company information submitted successfully!'

    # If the request method is not POST, just return the form page
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
import pandas as pd # for dataframes
import matplotlib.pyplot as plt # for plotting graphs
import seaborn as sns # for plotting graphs
import datetime as dt
import numpy as np
from sklearn.cluster import KMeans
from scipy import stats
from scipy.stats import kruskal
from statsmodels.graphics.gofplots import qqplot
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import os
import json 

app = Flask(__name__)
uploads_dir = './upload'

def order_cluster(cluster_field_name, target_field_name,data,ascending):
    new_cluster_field_name = 'new_' + cluster_field_name
    data_new = data.groupby(cluster_field_name)[target_field_name].mean().reset_index()
    data_new = data_new.sort_values(by=target_field_name,ascending=ascending).reset_index(drop=True)
    data_new['index'] = data_new.index
    data_final = pd.merge(data,data_new[[cluster_field_name,'index']], on=cluster_field_name)
    data_final = data_final.drop([cluster_field_name],axis=1)
    data_final = data_final.rename(columns={"index":cluster_field_name})

    return data_final


def rfm_json(data, filter_option=''):
    n_clusters = 5
    df = pd.json_normalize(data)
    df['created_at_date'] = pd.to_datetime(df['created_at_date'])

    #create a user dataframe to hold CustomerID and new segmentation scores
    user = pd.DataFrame(df['customer_id'].unique())
    user.columns = ['customer_id']

    #get the max purchase date for each customer and create a dataframe with it
    max_purchase = df.groupby('customer_id').created_at_date.max().reset_index()
    max_purchase.columns = ['customer_id','MaxPurchaseDate']

    #we take the observation point as the max invoice date in the dataset
    max_purchase['Recency'] = (max_purchase['MaxPurchaseDate'].max() - max_purchase['MaxPurchaseDate']).dt.days

    #merge this dataframe to the new user dataframe
    user = pd.merge(user, max_purchase[['customer_id','Recency']], on='customer_id')
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(user[['Recency']])
    user['RecencyCluster'] = kmeans.predict(user[['Recency']])

    #function for ordering cluster numbers

    user = order_cluster('RecencyCluster', 'Recency',user,False)
    #k-means

    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(user[['Recency']])
    user['RecencyCluster'] = kmeans.predict(user[['Recency']])

    #order the recency cluster
    user = order_cluster('RecencyCluster', 'Recency',user,True)

    #get order counts for each user and create a dataframe with it
    frequency = df.groupby('customer_id').created_at_date.count().reset_index()
    frequency.columns = ['customer_id','Frequency']

    #add this data to our main dataframe
    user = pd.merge(user, frequency, on='customer_id')

    #k-means
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(user[['Frequency']])
    user['FrequencyCluster'] = kmeans.predict(user[['Frequency']])

    #order the recency cluster
    user = order_cluster('FrequencyCluster', 'Frequency',user,True)

    #see details of each cluster
    user.groupby('FrequencyCluster')['Frequency'].describe()

    #calculate revenue for each customer
    df['Monetary'] = df['amount'] # * df['Quantity']
    monetary = df.groupby('customer_id').Monetary.sum().reset_index()

    #merge it with our main dataframe
    user = pd.merge(user, monetary, on='customer_id')

    #apply clustering
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(user[['Monetary']])
    user['MonetaryCluster'] = kmeans.predict(user[['Monetary']])

    #order the cluster numbers
    user = order_cluster('MonetaryCluster','Monetary', user, True)

    # For # API getSegmentsWithCount

    if filter_option == '':
        recency = user.groupby(['RecencyCluster'])['customer_id'].count().set_axis([x + 1 for x in range(n_clusters)], axis='index').to_json()
        frequency = user.groupby(['FrequencyCluster'])['customer_id'].count().set_axis([x + 1 for x in range(n_clusters)], axis='index').to_json()
        monetary = user.groupby(['MonetaryCluster'])['customer_id'].count().set_axis([x + 1 for x in range(n_clusters)], axis='index').to_json()
        
        return  {
                    'recency': recency,
                    'frequency': frequency,
                    'monetary': monetary
                }

    # For API getSegmentCustomerIds
    recency_range = filter_option[0]['recency']
    frequency_range = filter_option[1]['frequency']



    filtered_df = user.query('RecencyCluster >= {} and RecencyCluster <= {} and FrequencyCluster >= {} and FrequencyCluster <= {}'
        .format(recency_range['min'], recency_range['max'], frequency_range['min'], frequency_range['max']))

    return filtered_df['customer_id'].values.tolist()

@app.route('/getSegmentsWithCount', methods=['POST'])
def getSegmentsWithCount():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            if len(data) == 1:
                result = rfm_json(data)
                return jsonify(result)
        except:
            return jsonify({'message': 'Error'})
        pass
    else:
        return jsonify({'message': 'The GET method is not supported for this route'})

@app.route('/getSegmentCustomerIds', methods=['POST'])
def getSegmentCustomerIds():
    if request.method == 'POST':
        data_filter = json.loads(request.data)
        if len(data_filter) == 2:
            data = data_filter[0]
            filter_option = data_filter[1]
            
            recency_range = filter_option[0]['recency']
            frequency_range = filter_option[1]['frequency']

            if recency_range['min'] < 0 or recency_range['max'] < 0 or frequency_range['min'] < 0 or frequency_range['max'] < 0:
                return jsonify({'message': 'Filter value can not be negative'})

            if recency_range['min'] > recency_range['max']:
                return jsonify({'message': 'The the min is greater then max'})

            if frequency_range['min'] > frequency_range['max']:
                return jsonify({'message': 'The the min is greater then max'})

            result = rfm_json(data, filter_option)
            return jsonify(result)
        try:
            pass
        except:
            return jsonify({'message': 'Error'})
    else:
        return jsonify({'message': 'The GET method is not supported for this route'})


if __name__ == "__main__":
    app.run(debug=True)
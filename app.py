import pandas as pd # for dataframes
import matplotlib.pyplot as plt # for plotting graphs
import numpy as np
from sklearn.cluster import KMeans
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import os
import json 
import datetime

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


def rfm_json(data, filter_option='', count=False):
    n_clusters = 5
    random_state = 2020
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
    user = pd.merge(user, max_purchase[['customer_id','Recency', 'MaxPurchaseDate']], on='customer_id')
    # kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    # kmeans.fit(user[['Recency']])
    # user['RecencyCluster'] = kmeans.predict(user[['Recency']])

    #function for ordering cluster numbers

    # user = order_cluster('RecencyCluster', 'Recency',user,False)
    #k-means

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
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
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    kmeans.fit(user[['Frequency']])
    user['FrequencyCluster'] = kmeans.predict(user[['Frequency']])

    #order the recency cluster
    user = order_cluster('FrequencyCluster', 'Frequency',user,False)

    #see details of each cluster
    # print(user.groupby('FrequencyCluster')['Frequency'].describe())

    #calculate revenue for each customer
    df['Monetary'] = df['amount']
    monetary = df.groupby('customer_id').Monetary.sum().reset_index()

    #merge it with our main dataframe
    user = pd.merge(user, monetary, on='customer_id')

    #apply clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    kmeans.fit(user[['Monetary']])
    user['MonetaryCluster'] = kmeans.predict(user[['Monetary']])

    #order the cluster numbers
    user = order_cluster('MonetaryCluster','Monetary', user, True)


    # For # API getSegmentsWithCount

    if filter_option == '':
        user = order_cluster('FrequencyCluster','Frequency', user, True)

        # user = order_cluster('RecencyCluster','Recency', user, False)
        recency = user.groupby(['RecencyCluster'])['customer_id'].nunique().set_axis([x + 1 for x in range(n_clusters)], axis='index').to_json()
        
        # user = order_cluster('FrequencyCluster','Frequency', user, True)
        frequency = user.groupby(['FrequencyCluster'])['customer_id'].nunique().set_axis([x + 1 for x in range(n_clusters)], axis='index').to_json()
        
        # user = order_cluster('MonetaryCluster','Monetary', user, False)
        monetary = user.groupby(['MonetaryCluster'])['customer_id'].nunique().set_axis([x + 1 for x in range(n_clusters)], axis='index').to_json()
        
        return  {
                    'recency': recency,
                    'frequency': frequency,
                    'monetary': monetary
                }

    # For API getSegmentCustomerCount
    if count:
        user = order_cluster('FrequencyCluster','Frequency', user, True)
        # frequency = pd.merge(df, user, on='customer_id').groupby(['FrequencyCluster'])['customer_id'].count().set_axis([x + 1 for x in range(n_clusters)], axis='index').to_json()

        df_frequency = pd.merge(df, user, on='customer_id').groupby(['FrequencyCluster'])[['customer_id', 'FrequencyCluster']].apply(lambda x: x) 
        frequency = {}
        for i in range(n_clusters):
            temp_frequency = df_frequency.query("FrequencyCluster == {}".format(i))
            frequency[str(i+1)] = int(min(temp_frequency.groupby(['customer_id']).size().values))
    
        recency = {}
        user = order_cluster('RecencyCluster','Recency', user, False)
        for i in range(n_clusters):
            temp_recency = user.query("RecencyCluster == {}".format(i))
            max_date = datetime.datetime.today() - temp_recency["MaxPurchaseDate"].max()
            recency[str(i+1)] =  max_date.days

        results =   {
                        "rfm_definitions": {
                            "frequency": frequency,
                            "recency": recency
                        },
                        "segment_results": {

                        }
                    }

        for name, option in filter_option.items():
            recency_range = option[0]['recency']
            frequency_range = option[1]['frequency']
            filtered_df = user.query('RecencyCluster >= {} and RecencyCluster <= {} and FrequencyCluster >= {} and FrequencyCluster <= {}'
            .format(recency_range['min'], recency_range['max'], frequency_range['min'], frequency_range['max']))
            results["segment_results"].update({
                name: len(set(filtered_df['customer_id'].values.tolist()))
            })
        
        return results

    # For API getSegmentCustomerIds
    results = []
    user = order_cluster('FrequencyCluster','Frequency', user, True)
    user = order_cluster('RecencyCluster','Recency', user, False)

    # users_count = df['customer_id'].value_counts()

    for name, option in filter_option.items():
        recency_range = option[0]['recency']
        frequency_range = option[1]['frequency']
        filtered_df = user.query('RecencyCluster >= {} and RecencyCluster <= {} and FrequencyCluster >= {} and FrequencyCluster < {}'
        .format(recency_range['min'], recency_range['max'], frequency_range['min'], frequency_range['max']))
        
        # users_count = df[df['customer_id'].isin(filtered_df['customer_id'])].groupby('customer_id').count()
        users_count = df[df['customer_id'].isin(filtered_df['customer_id'])][['customer_id']].value_counts()
        us = []

        for index, val in users_count.iteritems():
            us.append({
                "id": index[0],
                "count": int(val)
            })

        results.append({
            # name: list(set(filtered_df['customer_id'].values.tolist()))
            name: us
        })
        

    return results



def rfm_json_manually(data, scoreDefination, filter_option='', count=False):
    n_clusters = scoreDefination["scoreCount"]
    recency_filter = scoreDefination["scoreValues"]["recency"]
    frequency_filter = scoreDefination["scoreValues"]["frequency"]

    df = pd.json_normalize(data)
    df['created_at_date'] = pd.to_datetime(df['created_at_date'])

    #create a user dataframe to hold CustomerID and new segmentation scores
    user = pd.DataFrame(df['customer_id'].unique())
    user.columns = ['customer_id']

    #get the max purchase date for each customer and create a dataframe with it
    max_purchase = df.groupby('customer_id').created_at_date.max().reset_index()
    max_purchase.columns = ['customer_id', 'MaxPurchaseDate']

    #we take the observation point as the max invoice date in the dataset
    max_purchase['Recency'] = (max_purchase['MaxPurchaseDate'].max() - max_purchase['MaxPurchaseDate']).dt.days

    #merge this dataframe to the new user dataframe
    user = pd.merge(user, max_purchase[['customer_id','Recency', 'MaxPurchaseDate']], on='customer_id')
    frequency = df.groupby('customer_id').created_at_date.count().reset_index()
    frequency.columns = ['customer_id','Frequency']

    #add this data to our main dataframe
    user = pd.merge(user, frequency, on='customer_id')
    
    df['Monetary'] = df['amount']
    monetary = df.groupby('customer_id').Monetary.sum().reset_index()

    #merge it with our main dataframe
    user = pd.merge(user, monetary, on='customer_id')

    recency_conditions = []
    frequency_conditions = []
    name_cluster = [*range(1, 1+n_clusters)]

    for x in name_cluster:
        # if x == 1:
        #     recency_condition = (user['Recency'] >= recency_filter[str(x)])
        #     frequency_condition = (user['Frequency'] <= frequency_filter[str(x)])
        if x != n_clusters:
            recency_condition = ((user['Recency'] <= recency_filter[str(x)]) & (user['Recency'] > recency_filter[str(x + 1)]))
            frequency_condition = ((user['Frequency'] >= frequency_filter[str(x)]) & (user['Frequency'] < frequency_filter[str(x + 1)]))
        else:
            recency_condition = (user['Recency'] <= recency_filter[str(x)])
            frequency_condition = (user['Frequency'] >= frequency_filter[str(x)])

        recency_conditions.append(recency_condition)
        frequency_conditions.append(frequency_condition)


    user['RecencyCluster'] = np.select(recency_conditions, name_cluster)
    user['FrequencyCluster'] = np.select(frequency_conditions, name_cluster)

    # For API getSegmentCustomerCount
    if count:
        user = order_cluster('FrequencyCluster','Frequency', user, True)

        df_frequency = pd.merge(df, user, on='customer_id').groupby(['FrequencyCluster'])[['customer_id', 'FrequencyCluster']].apply(lambda x: x) 
        frequency = {}
        for i in range(n_clusters):
            temp_frequency = df_frequency.query("FrequencyCluster == {}".format(i+1))
            frequency[str(i+1)] = int(min(temp_frequency.groupby(['customer_id']).size().values))
    
        recency = {}
        user = order_cluster('RecencyCluster','Recency', user, False)
        for i in range(n_clusters):
            temp_recency = user.query("RecencyCluster == {}".format(i+1))
            max_date = datetime.datetime.today() - temp_recency["MaxPurchaseDate"].max()
            recency[str(i+1)] =  max_date.days

        results =   {
                        "rfm_definitions": {
                            "frequency": frequency,
                            "recency": recency
                        },
                        "segment_results": {

                        }
                    }

        for name, option in filter_option.items():
            recency_range = option[0]['recency']
            frequency_range = option[1]['frequency']
            filtered_df = user.query('RecencyCluster >= {} and RecencyCluster <= {} and FrequencyCluster >= {} and FrequencyCluster <= {}'
            .format(recency_range['min'], recency_range['max'], frequency_range['min'], frequency_range['max']))
            results["segment_results"].update({
                name: len(set(filtered_df['customer_id'].values.tolist()))
            })
        
        return results

    # For API getSegmentCustomerIds
    results = []
    user = order_cluster('FrequencyCluster','Frequency', user, True)
    user = order_cluster('RecencyCluster','Recency', user, False)

    for name, option in filter_option.items():
        recency_range = option[0]['recency']
        frequency_range = option[1]['frequency']
        filtered_df = user.query('RecencyCluster >= {} and RecencyCluster <= {} and FrequencyCluster >= {} and FrequencyCluster < {}'
        .format(recency_range['min'], recency_range['max'], frequency_range['min'], frequency_range['max']))
        
        users_count = df[df['customer_id'].isin(filtered_df['customer_id'])][['customer_id']].value_counts()
        us = []

        for index, val in users_count.iteritems():
            us.append({
                "id": index[0],
                "count": int(val)
            })

        results.append({
            name: us
        })
        

    return results



@app.route("/")
def home_view():
    return "<h1>It works</h1>"

@app.route('/getSegmentsWithCount', methods=['POST'])
def getSegmentsWithCount():
    if request.method == 'POST':
        data = json.loads(request.data)
        result = rfm_json(data)
        try:
            return jsonify(result)
        except:
            return jsonify({'message': 'Error'})
    else:
        return jsonify({'message': 'The GET method is not supported for this route'})


@app.route('/getSegmentCustomerCount', methods=['POST'])
def getSegmentCustomerCount():
    if request.method == 'POST':
        data_filter = json.loads(request.data)

        if "data" not in data_filter and "filters" not in data_filter:
            return jsonify({'message': 'Data is invalid'})

        data = data_filter["data"]
        filter_option = data_filter["filters"]

        if len(filter_option) == 0:
            return jsonify({'message': 'Filter is invalid'})

        if "scoreDefination" in data_filter:
            scoreDefination = data_filter["scoreDefination"]
            result = rfm_json_manually(data, scoreDefination, filter_option)
            return jsonify(result)

        result = rfm_json(data, filter_option, True)
        try:
            return jsonify(result)
        except:
            return jsonify({'message': 'Error'})
    else:
        return jsonify({'message': 'The GET method is not supported for this route'})

@app.route('/getSegmentCustomerIds', methods=['POST'])
def getSegmentCustomerIds():
    if request.method == 'POST':
        data_filter = json.loads(request.data)

        if "data" not in data_filter and "filters" not in data_filter:
            return jsonify({'message': 'Data is invalid'})

        data = data_filter["data"]
        filter_option = data_filter["filters"]

        if len(filter_option) == 0:
            return jsonify({'message': 'Filter is invalid'})

        if "scoreDefination" in data_filter:
            scoreDefination = data_filter["scoreDefination"]
            result = rfm_json_manually(data, scoreDefination, filter_option)
            return jsonify(result)


        result = rfm_json(data, filter_option)
        return jsonify(result)

        try:
            pass
        except:
            return jsonify({'message': 'Error'})
    else:
        return jsonify({'message': 'The GET method is not supported for this route'})


if __name__ == "__main__":
    app.run()
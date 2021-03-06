# LOCAL TESTING

Clone the source by the following command:

```
git clone https://github.com/toantranct94/rfm_api.git
```

Move to the ```rfm_api``` folder:

```
cd rfm_api
```

## Prepare environment

 - Install the ```Python version 3.8```

 - Download here [https://www.python.org/downloads/release/python-388/](https://www.python.org/downloads/release/python-388/)

 - Install the required package by the following command
```
pip install -r requirements.txt
```

## Usage

Run command line as below:

```
python app.py
```

 - Get Segments: `POST` [http://127.0.0.1:5000/getSegmentsWithCount](http://127.0.0.1:5000/getSegmentsWithCount)

**Input**

```
[
    {"index":0,"customer_id":"vpnqlkmaoasmi","created_at_date":"2021-03-26 13:24:44.234000","order_number":"GV45919","amount":1990.0},
    {"index":1,"customer_id":"14cslklvjwtrs","created_at_date":"2021-03-27 13:00:19.942000","order_number":"GV46095","amount":1900.0}
]
```

**Output**

```
{
    "frequency": "{"1":16557,"2":2856,"3":625,"4":209,"5":12}",
    "monetary": "{"1":5352,"2":9533,"3":3720,"4":1330,"5":324}",
    "recency": "{"1":4418,"2":4519,"3":3578,"4":4029,"5":3715}"
}
```

 - Get Segments customer id: `POST` [http://127.0.0.1:5000/getSegmentCustomerIds](http://127.0.0.1:5000/getSegmentCustomerIds)


**Input**

```
[
    {"index":0,"customer_id":"vpnqlkmaoasmi","created_at_date":"2021-03-26 13:24:44.234000","order_number":"GV45919","amount":1990.0},
    {"index":1,"customer_id":"14cslklvjwtrs","created_at_date":"2021-03-27 13:00:19.942000","order_number":"GV46095","amount":1900.0}
],
[
    {"recency": {"min": 1, "max": 2}},
    {"frequency": {"min": 4, "max": 5}}
]
```

**Output**

```
[
    "14cslkm0hn3dw",
    "1xh60ckd7ykpciwzp2",
    "1xh60ck9lzkk1efniw"
]
```

# DEPLOYMENT

Clone the source by the following command:

```
git clone https://github.com/toantranct94/rfm_api.git
```

Move to the ```rfm_api``` folder:

```
cd rfm_api
```

After install ```heroku``` sucessfully, run the command to login:

```
heroku login
```

Run orderly the following commands to deploy:

```
heroku create
```

```
git push heroku main
```

```
heroku ps:scale web=1
```


Or follow the instructions to deploy with ```heroku```  at: [https://devcenter.heroku.com/articles/getting-started-with-python](https://devcenter.heroku.com/articles/getting-started-with-python)

Note: every required files for deploying with ```heroku``` are prepared, including:

 - requirements.txt
 - Procfile
 - Procfile.windows
 - runtime.txt

## Usage

Once the app has deployed, the API can be served as:

 - Get Segments: `POST` [https://your-app-name.herokuapp.com/getSegmentsWithCount](https://your-app-name.herokuapp.com/getSegmentsWithCount)

**Input**

```
[
    {"index":0,"customer_id":"vpnqlkmaoasmi","created_at_date":"2021-03-26 13:24:44.234000","order_number":"GV45919","amount":1990.0},
    {"index":1,"customer_id":"14cslklvjwtrs","created_at_date":"2021-03-27 13:00:19.942000","order_number":"GV46095","amount":1900.0}
]
```

**Output**

```
{
    "frequency": "{"1":16557,"2":2856,"3":625,"4":209,"5":12}",
    "monetary": "{"1":5352,"2":9533,"3":3720,"4":1330,"5":324}",
    "recency": "{"1":4418,"2":4519,"3":3578,"4":4029,"5":3715}"
}
```

 - Get Segments customer id: `POST` [https://your-app-name.herokuapp.com/getSegmentCustomerIds](https://your-app-name.herokuapp.com/getSegmentCustomerIds)


**Input (using algorithm)** 

```
{
    "data": [
        {
            "index": 0,"customer_id": "vpnqlkmaoasmi",
            "created_at_date": "2021-03-26 13:24:44.234000",
            "order_number": "GV45919", "amount": 1990.0
        },
        {
            "index": 1,
            "customer_id": "14cslklvjwtrs",
            "created_at_date": "2021-03-27 13:00:19.942000",
            "order_number": "GV46095",
            "amount": 1900.0
        },
        {
            "index": 2,
            "customer_id": "wsw4lkl6ugfaf",
            "created_at_date": "2021-03-27 13:05:37.651000",
            "order_number": "GV46096",
            "amount": 500.0
        }
    ],
    "filters": {
        "segment-a": [
            {
                "recency": {
                    "min": 1,
                    "max": 2
                }
            },
            {
                "frequency": {
                    "min": 4,
                    "max": 5
                }
            }
        ],
        "segment-b": [
            {
                "recency": {
                    "min": 1,
                    "max": 2
                }
            },
            {
                "frequency": {
                    "min": 4,
                    "max": 5
                }
            }
        ]
    }
}
```

**Input (using parameters)** 

```
{
    "data": [
        {
            "index": 0,"customer_id": "vpnqlkmaoasmi",
            "created_at_date": "2021-03-26 13:24:44.234000",
            "order_number": "GV45919", "amount": 1990.0
        },
        {
            "index": 1,
            "customer_id": "14cslklvjwtrs",
            "created_at_date": "2021-03-27 13:00:19.942000",
            "order_number": "GV46095",
            "amount": 1900.0
        },
        {
            "index": 2,
            "customer_id": "wsw4lkl6ugfaf",
            "created_at_date": "2021-03-27 13:05:37.651000",
            "order_number": "GV46096",
            "amount": 500.0
        }
    ],
    "filters": {
        "segment-a": [
            {
                "recency": {
                    "min": 1,
                    "max": 2
                }
            },
            {
                "frequency": {
                    "min": 4,
                    "max": 5
                }
            }
        ],
        "segment-b": [
            {
                "recency": {
                    "min": 1,
                    "max": 2
                }
            },
            {
                "frequency": {
                    "min": 4,
                    "max": 5
                }
            }
        ]
    },
    "scoreDefination":{
        "scoreCount": 5,
        "scoreValues": {
            "recency":{
                "1": 97,
                "2": 72,
                "3": 50,
                "4": 31,
                "5": 12
            },
            "frequency": {
                "1": 1,
                "2": 2,
                "3": 3,
                "4": 4,
                "5": 7
            }
        }
    }
}
```

**Output (sample)**

```
[
    {
        "segment-a": [
            {
                "count": 6,
                "id": "15ee6qlkkwoezg4"
            },
            {
                "count": 6,
                "id": "1xh60ckfyrklm9716a"
            },
            {
                "count": 6,
                "id": "1e8sqmknga2v5u"
            },
            {
                "count": 5,
                "id": "vojwml7lkmp6jmjd"
            },
            {
                "count": 5,
                "id": "1dltlkni9qags"
            },
            {
                "count": 4,
                "id": "1xh60ckj9ckmf18rl1"
            },
            {
                "count": 4,
                "id": "1xh60ckj9ckmsol0br"
            },
            {
                "count": 4,
                "id": "1xh60ckj9ckmk5e24x"
            },
            {
                "count": 4,
                "id": "1xh60ckj9ckmk9owsx"
            }
        ]
    },
    {
        "segment-b": [
            {
                "count": 11,
                "id": "vojwml7lkmrhdfap"
            },
            {
                "count": 10,
                "id": "14cslkm0hn3dw"
            },
            {
                "count": 8,
                "id": "1xh60ck65ykmx7se8m"
            },
            {
                "count": 7,
                "id": "15ee6qlkktfq4yo"
            }
        ]
    }
]
```

 - Get Segments: `POST` [https://your-app-name.herokuapp.com/getSegmentCustomerCount](https://your-app-name.herokuapp.com/getSegmentCustomerCount)


**Input**

```
{
    "data": [
        {
            "index": 0,"customer_id": "vpnqlkmaoasmi",
            "created_at_date": "2021-03-26 13:24:44.234000",
            "order_number": "GV45919", "amount": 1990.0
        },
        {
            "index": 1,
            "customer_id": "14cslklvjwtrs",
            "created_at_date": "2021-03-27 13:00:19.942000",
            "order_number": "GV46095",
            "amount": 1900.0
        },
        {
            "index": 2,
            "customer_id": "wsw4lkl6ugfaf",
            "created_at_date": "2021-03-27 13:05:37.651000",
            "order_number": "GV46096",
            "amount": 500.0
        }
    ],
    "filters": {
        "segment-a": [
            {
                "recency": {
                    "min": 1,
                    "max": 2
                }
            },
            {
                "frequency": {
                    "min": 4,
                    "max": 5
                }
            }
        ],
        "segment-b": [
            {
                "recency": {
                    "min": 1,
                    "max": 2
                }
            },
            {
                "frequency": {
                    "min": 4,
                    "max": 5
                }
            }
        ]
    }
}
```

**Output**

```
{
    "rfm_defenation": {
        "frequency": {"1":16557,"2":5712,"3":1875,"4":900,"5":101},
        "recency": {
            "1": 6,
            "2": 27,
            "3": 48,
            "4": 71,
            "5": 95
        }
    },
    "segment_results": {
        "segment-a": 3,
        "segment-b": 3
    }
}
```


# Sample data

The testing data can be found at ```orders.json``` which is converted from the ```orders.csv``` for testing purpose.
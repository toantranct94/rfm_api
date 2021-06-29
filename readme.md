# LOCAL TESTING

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

Follow the instructions to deploy with ```heroku``` 

[https://devcenter.heroku.com/articles/getting-started-with-python](https://devcenter.heroku.com/articles/getting-started-with-python)

Note: every required files for deploying with ```heroku``` are prepared, including:

 - requirements.txt
 - Procfile
 - Procfile.windows
 - runtime.txt
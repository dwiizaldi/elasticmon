from flask import Flask
from flask import request
import json
import re
import requests
import socket
import time

ElasticMON_URL="192.168.12.98:9200"
#url_flexran = "http://192.168.12.94:9999"
url_flexran = "http://192.168.12.98:9999"

app = Flask(__name__)

@app.route('/')
def init():
    return 'Greetings from ElasticMON Webserver'

@app.route('/elasticmon',methods=['GET'])
def page_elasticmonurl_get():
    """
    @api {get} /elasticmon: Get ElasticMON url and port
    @apiVersion 1.0.0
    @apiName get_elasticmonurl
    @apiGroup ElasticMonitoring

    @apiDescription Gets the current ElasticMON url and port. This endpoint is the destination point of requests from this webserver.
    
    @apiExample Example usage:
    curl -i http://elasticmonserver:port/elasticmon
    @apiSuccessExample {json} Success-Response:
         {"ElasticMON_URL": "localhost:9200"}
    @apiErrorExample {Object} Error-Response:
        HTTP/1.1 400 BadRequest 
    """
    elasticmonurl_results={}
    elasticmonurl_results['ElasticMON_URL']=ElasticMON_URL
    return json.dumps(elasticmonurl_results),200

@app.route('/elasticmon/endpoint/<string:url>',methods=['POST'])
def page_elasticmonurl_set(url):
    """
    @api {post} /elasticmon/endpoint/:ep: Set ElasticMON url and port
    @apiVersion 1.0.0
    @apiName set_elasticmonurl
    @apiGroup ElasticMonitoring
    @apiParam {string} url The endpoint in the form `IP:Port`
    @apiDescription Sets the current ElasticMON url and port.
    The endpoint needs to be in the form `IP:Port` where IP is either a numerical IPv4 address or a hostname.
    More specifically, it needs to match the regex `^(?:[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+|[a-zA-Z0-9-]+):\d+$`.
    Note that it is not not actually checked that the endpoint exists.

    
    @apiExample Example usage:
    curl -X POST http://elasticmonserver:port/elasticmon/endpoint/192.168.12.25:9200
    @apiSuccessExample {Object} Success-Response:
         HTTP/1.1 200 OK
    @apiErrorExample {json} Error-Response:
        { "error": "The given endpoint is not of the correct form. Expected format elasticmonip:port"}
        HTTP/1.1 400 BadRequest 
    """
    global ElasticMON_URL
    response={}
    regex=r'^(?:[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+|[a-zA-Z0-9-]+):\d+$'

    if(re.match(regex,url)):
        ElasticMON_URL=url
    else:
        response['error']="The given endpoint is not of the correct form. Expected format elasticmonip:port"
        return json.dumps(response),400
    return "OK",200

@app.route('/count/<string:indexname>/',methods=['GET'])
def get_index_count(indexname):
    """
    @api {get} /count/:indexname: Get count from an index between given times
    @apiVersion 1.0.0
    @apiName count_by_index_and_time
    @apiGroup BasicQueries
    @apiParam {string} indexname The index to be searched for count query
    @apiParam {string} start The minimum time before `now` to be found (i.e 2m, 3h, 5d , 3h/h etc)
    @apiParam {string} end The The maximum time before `now` to be found (i.e 2m, 3h, 5d , 3h/h etc)
    @apiDescription get count of measurements in elasticmon for a specific metric for given time periods.
    The index will be searched only for count and between time periods from `now-start` until `now-end`.
    Both start and end parameters are optional and can be given by URL. Default values will count between `now-1m` and `now`
    Allowed formats for times are as follows: X`s`,`m`,`h`,`d`,`y` for basics or `/d` in the end to round the time.(i.e 3d/d will round to 3 days ago 24:00h)
    
    @apiExample Example usage:
    curl -X GET http://elasticmonserver:port/count/mac_stats/
    curl -X GET http://elasticmonserver:port/count/mac_stats/?start=now
    curl -X GET http://elasticmonserver:port/count/mac_stats/?start=3h
    curl -X GET http://elasticmonserver:port/count/mac_stats/?start=4d&end=0s
    @apiSuccessExample {json} Success-Response:
        {"index": "mac_stats","count": 305303}
        HTTP/1.1 200 OK
    @apiErrorExample {json} Error-Response:
        {"index": "mac_stats", "error": "unit [n] not supported for date math [-now]"}
        HTTP/1.1 400 BadRequest 

    @apiErrorExample {json} Error-Response:
        {"index": "mac_stats", "error": "no such index"}
        HTTP/1.1 400 BadRequest 
    """
    timeperiodstart = request.args.get('start', "1m")
    timeperiodend = request.args.get('end', "0s")

    requestbody={"query":{"bool":{"must":[{"range":{"date_time":{"gte":"now","lt":"now"}}}]}}}
    requestbody['query']['bool']['must'][0]['range']['date_time']['gte']="now"+"-"+timeperiodstart
    requestbody['query']['bool']['must'][0]['range']['date_time']['lt']="now"+"-"+timeperiodend
    response = requests.get('http://'+ElasticMON_URL+'/'+indexname+'/_count',headers={'Content-Type': 'application/json'},data=str(requestbody).replace("'", '"'))
    print str(requestbody).replace("'", '"')
    result={}
    try:
        result['index'] = indexname
        result['count'] = json.loads(response.text)['count']
        return json.dumps(result),200
    except:
        result['error']=json.loads(response.text)['error']['root_cause'][0]['reason']
        return json.dumps(result),400
    return json.loads(response.text),400


@app.route('/latest/<string:indexname>/',methods=['GET'])
def get_index_latest(indexname):
    """
    @api {get} /latest/:indexname: Get latest recorded X results
    @apiVersion 1.0.0
    @apiName latest_by_index_and_size
    @apiGroup BasicQueries
    @apiParam {string} indexname The index to be searched for search query, supports wildcard usage such as `*` which will return elements from all matching indexes.
    @apiParam {int} size The amount of records to be returned back. Default value is 1 which only returns the latest recorded element

    @apiDescription get the latest recorded X elements from a given index. As the size increases the size of transfered response also increases.
    Thus there is a `index.max_result_window` configuration on ElasticSearch control panel to adjust the maximum allowed result window.


    @apiExample Example usage:
    curl -X GET http://elasticmonserver:port/latest/mac_stats
    curl -X GET http://elasticmonserver:port/latest/enb_config
    curl -X GET http://elasticmonserver:port/latest/mac_stats/?size=3
    curl -X GET http://elasticmonserver:port/count/predictor*/?start=3h
    @apiSuccessExample {json} Success-Response:
    
    {
    "index": "mac_stats",
    "result": [
            {
            "date_time": "2019-02-16T18:47:05.390",
            "mac_stats": {...}
            },
            {
            "date_time": "2019-02-16T18:47:05.380",
            "mac_stats": {...}
            },
            {
            "date_time": "2019-02-16T18:47:05.370",
            "mac_stats": {...}
            },
        ]
    }
    HTTP/1.1 200 OK

    @apiSuccessExample {json} Success-Response:
    {
  "index": "enb_config",
  "result": [
            {
            "date_time": "2019-02-19T15:22:00.600",
            "eNB_config": [...]
            }
        ]
    }

    HTTP/1.1 200 OK


    @apiErrorExample {json} Error-Response:
    {"index": "random_index","error": "no such index"}
    HTTP/1.1 400 BadRequest 
    @apiErrorExample {json} Error-Response:
    {"index": "enb_config","error": "Result window is too large, from + size must be less than or equal to: [10000] but was [100000]. See the scroll api for a more efficient way to request large data sets. This limit can be set by changing the [index.max_result_window] index level setting."}
    HTTP/1.1 400 BadRequest 

    """
    input_size = request.args.get('size', 1)
    requestbody={"size" : 1,"sort": [{"date_time": {"order": "desc"}}],"query":{"match_all":{}}}
    requestbody['size']=input_size
    
    response = requests.get('http://'+ElasticMON_URL+'/'+indexname+'/_search',headers={'Content-Type': 'application/json'},data=str(requestbody).replace("'", '"'))
    result={}
    try:
        result['index'] = indexname
        result['result'] = [i['_source'] for i in json.loads(response.text)['hits']['hits']]
        return json.dumps(result),200
    except:
        result['error']=json.loads(response.text)['error']['root_cause'][0]['reason']
        return json.dumps(result),400
    return json.loads(response.text),400


@app.route('/slices/',methods=['GET'])
def get_slice_configs():
    """
    @api {get} /slices/: Get slice configurations
    @apiVersion 1.0.0
    @apiName get_slice_configs
    @apiGroup SliceQueries
    @apiParam {int} sliceid The id of the slice to return its UL and DL configurations
    @apiParam {string} slicelabel The label of the slice to return its UL and DL configurations

    @apiDescription Get the latest known slice configurations recorded with `eNBId` by also filtering with `eNB_config.eNB.cellConfig.sliceConfig.dl/ul.id` or `eNB_config.eNB.cellConfig.sliceConfig.dl/ul.label`.
    Note that filtering with both features id not supported as it is redundant, in such case sliceid has priority over slicelabel. Timed query is not supported as slice configurations can change over time and cause
    unbalanced JSON tree. Refer to fields and size queries to retrieve slice configurations in timed manner.
    With no parameters given the request will return all slice configurations known.

    @apiExample Example usage:
    curl -X GET http://elasticmonserver:port/slices/
    curl -X GET http://elasticmonserver:port/slices/?sliceid=0
    curl -X GET http://elasticmonserver:port/slices/?slicelabel=xMBB
    @apiSuccessExample {json} Success-Response:
    
    {
    "date_time": [
        "2019-02-22T12:03:50.315"
    ],
    "eNB_config": [
        [
        {
            "eNB": {
            "eNBId": "234881024",
            "cellConfig": [
                {
                "sliceConfig": {
                    "ul": [
                    {
                        "firstRb": 0,
                        "maxmcs": 20,
                        "percentage": 100,
                        "isolation": false,
                        "id": 0,
                        "label": "xMBB",
                        "accounting": "POLU_FAIR",
                        "priority": 0,
                        "schedulerName": "schedule_ulsch_rnti"
                    }
                    ],
                    "dl": [
                    {
                        "positionLow": 0,
                        "maxmcs": 28,
                        "percentage": 100,
                        "sorting": [
                        "CR_ROUND",
                        "CR_SRB12",
                        "CR_HOL",
                        "CR_LC",
                        "CR_CQI",
                        "CR_LCP"
                        ],
                        "positionHigh": 25,
                        "isolation": false,
                        "id": 0,
                        "label": "xMBB",
                        "accounting": "POL_FAIR",
                        "priority": 10,
                        "schedulerName": "schedule_ue_spec"
                    }
                    ]
                }
                }
            ]
            }
        }
        ]
    ]
    }
    HTTP/1.1 200 OK

    @apiSuccessExample {json} Success-Response:
    {
    "date_time": [],
    "eNB_config": []
    }
    HTTP/1.1 200 OK


    @apiErrorExample {json} Error-Response:
    {
        "error": "failed to create query: {
            "multi_match" : {
                "query" : "randomstring",
                "fields" : ["eNB_config.eNB.cellConfig.sliceConfig.dl.id","eNB_config.eNB.cellConfig.sliceConfig.ul.id"]
            }
        }
    }
    HTTP/1.1 400 BadRequest 
    """

    sliceid = request.args.get('sliceid')
    slicelabel = request.args.get('slicelabel')
    requestbody={ "size": 1,"_source": {"includes": ["date_time","eNB_config.eNB.cellConfig.sliceConfig.dl","eNB_config.eNB.cellConfig.sliceConfig.ul","eNB_config.eNB.eNBId"]}, "sort": [{"date_time": {"order": "desc"}}], "query":{"match_all":{}} }

    if('sliceid' in request.args): #ID search
        requestbody['query'] = {"multi_match":{"query":"","fields":["eNB_config.eNB.cellConfig.sliceConfig.dl.id","eNB_config.eNB.cellConfig.sliceConfig.ul.id"]}}
        requestbody['query']['multi_match']['query'] = sliceid
    elif('slicelabel' in request.args): #Label search
        requestbody['query'] = {"multi_match":{"query":"","fields":["eNB_config.eNB.cellConfig.sliceConfig.dl.label","eNB_config.eNB.cellConfig.sliceConfig.ul.label"]}}
        requestbody['query']['multi_match']['query'] = slicelabel
    else: #All search
        requestbody['query'] = {"match_all":{}}

    response = requests.get('http://'+ElasticMON_URL+'/enb_config/_search',headers={'Content-Type': 'application/json'},data=str(requestbody).replace("'", '"'))

    result={}
    try:
        result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
        result['eNB_config'] = [i['_source']['eNB_config'] for i in json.loads(response.text)['hits']['hits']]
        return json.dumps(result),200
    except:
        result['error']=json.loads(response.text)['error']['root_cause'][0]['reason']
        return json.dumps(result),400
    return json.loads(response.text),400


@app.route('/get/rnti',methods=['GET'])
def get_rnti():
    """
        @api {get} /get/rnti/ Get the latest value of rnti
        @apiVersion 1.0.0
        @apiName get_rnti
        @apiGroup MacStatsQueries

        @apiDescription Get rnti value in mac_stats and also print the time

        @apiExample Example usage:
        curl -X GET http://elasticmonserver:port/get/rnti
        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-17T17:15:23.044"
            ],
        "rnti": [
            49112
            ]
        }
        HTTP/1.1 200 OK

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 400 BadRequest
    """

    input_size = request.args.get('size', 1)
    requestbody = {"size": 1, "sort": [{"date_time": {"order": "desc"}}], "query": {"match_all": {}}}
    requestbody['size'] = input_size

    response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search', headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
    result = {}
    try:
        result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
        result['rnti'] = [i['_source']['mac_stats']['rnti'] for i in json.loads(response.text)['hits']['hits']]
        return json.dumps(result), 200
    except:
        result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
        return json.dumps(result), 400
    return json.loads(response.text), 400


@app.route('/get/wbcqi/<string:query>/',methods=['GET'])
def get_wbcqi_query(query):
    """
        @api {get} /get/wbcqi/:query Extract the values of wbCqi
        @apiVersion 1.0.0
        @apiName get_wbcqi_query
        @apiGroup MacStatsQueries
        @apiParam {string} start The time before now to start searching for the values (i.e 2m, 3h, 5d , 3h/h etc)
        @apiParam {string} end The time (before now and after start) to end searching for the values (i.e 2m, 3h, 5d , 3h/h etc)

        @apiDescription Return either all, average, or the latest value of wbCqi in mac_stats. For all values, it will return maximum 10 values with ascending order time.
        For average values, it will return the average within the given period time.
        For the latest values, it will return the latest available wbCqi value and print the time.
        Both start and end parameters are required for `all` and `interval` query. Allowed formats for times are as follows: X`s`,`m`,`h`,`d`,`y` for basics or `/d` in the end to round the time.(i.e 3d/d will round to 3 days ago 24:00h)

        @apiExample Example usage:
        curl -X GET "http://elasticmonserver:port/get/wbcqi/interval/?start=10d&end=2d"
        curl -X GET "http://elasticmonserver:port/get/wbcqi/average/?start=10d&end=2d"
        curl -X GET "http://elasticmonserver:port/get/wbcqi/latest/"
        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T10:20:05.606",
            "2019-06-26T10:20:05.706",
            "2019-06-26T10:20:05.806",
            "2019-06-26T10:20:05.906",
            "2019-06-26T10:20:06.006",
            "2019-06-26T10:20:06.106",
            "2019-06-26T10:20:06.206",
            "2019-06-26T10:20:06.306",
            "2019-06-26T10:20:06.406",
            "2019-06-26T10:20:06.506",
            ],
        "wbcqi": [
            15,
            15,
            15,
            15,
            15,
            15,
            15,
            15,
            15,
            15
            ]
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "average_wbcqi": 15
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T11:56:02.140"
            ],
        "latest_wbcqi": [
            15
            ]
        }
        HTTP/1.1 200 OK

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 400 BadRequest
    """

    if (query == 'interval') or (query == 'average'):
        start= request.args.get('start', default="1m")
        periodstart = start.encode('ascii', 'ignore')
        end = request.args.get('end', default="1m")
        periodend = end.encode('ascii', 'ignore')

        requestbody = {"query": {"constant_score": {"filter": {"bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field":"mac_stats.mac_stats"}}], "must_not": {"term": {"mac_stats": ""}}}}}}, "sort": {"date_time": {"order": "asc"}}}
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['gte']="now"+"-"+periodstart
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['lt']="now"+"-"+periodend
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search', headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}

        if query == 'interval':
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['wbcqi'] = [i['_source']['mac_stats']['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        elif query == 'average':
            sum_wbcqi = [i['_source']['mac_stats']['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi']for i in json.loads(response.text)['hits']['hits']]
            result['average_wbcqi'] = (sum(sum_wbcqi) / len(sum_wbcqi))
            return json.dumps(result), 200
        else:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400

    elif query == 'latest':
        requestbody = {"size": 1, "query": {"constant_score": {"filter": {"bool": {"must": {"exists": {"field": "mac_stats.mac_stats"}}, "must_not": {"term": {"mac_stats": ""}}}}}},"sort": {"date_time": {"order": "desc"}}}
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search',headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}
        try:
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['latest_wbcqi'] = [i['_source']['mac_stats']['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        except:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400


@app.route('/get/phr/<string:query>/',methods=['GET'])
def get_phr_query(query):
    """
        @api {get} /get/phr/:query Extract the values of phr
        @apiVersion 1.0.0
        @apiName get_interval_phr
        @apiGroup MacStatsQueries
        @apiParam {string} start The time before now to start searching for the values (i.e 2m, 3h, 5d , 3h/h etc)
        @apiParam {string} end The time (before now and after start) to end searching for the values (i.e 2m, 3h, 5d , 3h/h etc)

        @apiDescription Return either all, average, or the latest value of phr in mac_stats. For all values, it will return maximum 10 values with ascending order time.
        For average values, it will return the average within the given period time.
        For the latest values, it will return the latest available phr value and print the time.
        Both start and end parameters are required for `all` and `interval` query. Allowed formats for times are as follows: X`s`,`m`,`h`,`d`,`y` for basics or `/d` in the end to round the time.(i.e 3d/d will round to 3 days ago 24:00h)

        @apiExample Example usage:
        curl -X GET "http://elasticmonserver:port/get/phr/interval/?start=10d&end=2d"
        curl -X GET "http://elasticmonserver:port/get/phr/average/?start=10d&end=2d"
        curl -X GET "http://elasticmonserver:port/get/phr/latest/"

        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T10:20:05.606",
            "2019-06-26T10:20:05.706",
            "2019-06-26T10:20:05.806",
            "2019-06-26T10:20:05.906",
            "2019-06-26T10:20:06.006",
            "2019-06-26T10:20:06.106",
            "2019-06-26T10:20:06.206",
            "2019-06-26T10:20:06.306",
            "2019-06-26T10:20:06.406",
            "2019-06-26T10:20:06.506",
            ],
        "phr": [
            40,
            40,
            40,
            40,
            40,
            40,
            40,
            40,
            40,
            40
            ]
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "average_phr": 40
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T10:20:05.606"
            ],
        "latest_phr": [
            40
            ]
        }
        HTTP/1.1 200 OK

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 400 BadRequest
    """

    if (query == 'interval') or (query == 'average'):
        start= request.args.get('start', default="1m")
        periodstart = start.encode('ascii', 'ignore')
        end = request.args.get('end', default="1m")
        periodend = end.encode('ascii', 'ignore')


        requestbody = {"query": {"constant_score": {"filter": {"bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field":"mac_stats.mac_stats"}}], "must_not": {"term": {"mac_stats": ""}}}}}}, "sort": {"date_time": {"order": "asc"}}}
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['gte']="now"+"-"+periodstart
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['lt']="now"+"-"+periodend
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search', headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}

        if query == 'interval':
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['phr'] = [i['_source']['mac_stats']['mac_stats']['phr']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        if query == 'average':
            sum_phr = [i['_source']['mac_stats']['mac_stats']['phr']for i in json.loads(response.text)['hits']['hits']]
            result['average_phr'] = (sum(sum_phr) / len(sum_phr))
            return json.dumps(result), 200
        else:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400

    elif query == 'latest':
        requestbody = {"size": 1, "query": {"constant_score": {"filter": {"bool": {"must": {"exists": {"field": "mac_stats.mac_stats"}}, "must_not": {"term": {"mac_stats": ""}}}}}}, "sort": {"date_time": {"order": "desc"}}}
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search', headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}
        try:
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['latest_phr'] = [i['_source']['mac_stats']['mac_stats']['phr']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        except:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400


@app.route('/get/rsrp/<string:query>/',methods=['GET'])
def get_rsrp_query(query):
    """
        @api {get} /get/rsrq/:query Extract the values of rsrp
        @apiVersion 1.0.0
        @apiName get_rsrp_by_query
        @apiGroup MacStatsQueries
        @apiParam {string} start The time before now to start searching for the values (i.e 2m, 3h, 5d , 3h/h etc)
        @apiParam {string} end The time (before now and after start) to end searching for the values (i.e 2m, 3h, 5d , 3h/h etc)

        @apiDescription Return either all, average, or the latest value in mac_stats. For all values, it will return maximum 10 values with ascending order time.
        For average values, it will return the average within the given period time.
        For the latest values, it will return the latest available rsrq value and print the time.
        Both start and end parameters are required for `all` and `interval` query. Allowed formats for times are as follows: X`s`,`m`,`h`,`d`,`y` for basics or `/d` in the end to round the time.(i.e 3d/d will round to 3 days ago 24:00h)

        @apiExample Example usage:
        curl -X GET "http://elasticmonserver:port/get/rsrp/interval/?start=10d&end=2d"
        curl -X GET "http://elasticmonserver:port/get/rsrp/average/?start=3d&end=1s"
        curl -X GET 'http://localhost:5000/get/rsrp/latest/'

        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T10:20:05.606",
            "2019-06-26T10:20:05.706",
            "2019-06-26T10:20:05.806",
            "2019-06-26T10:20:05.906",
            "2019-06-26T10:20:06.006",
            "2019-06-26T10:20:06.106",
            "2019-06-26T10:20:06.206",
            "2019-06-26T10:20:06.306",
            "2019-06-26T10:20:06.406",
            "2019-06-26T10:20:06.506",
            ],
        "rsrp": [
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1
            ]
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "average_rsrp": -1
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T11:56:02.140"
            ],
        "rsrp": [
            -1
            ]
        }
        HTTP/1.1 200 OK


        @apiErrorExample {json} Error-Response:
        HTTP/1.1 400 BadRequest
    """

    if (query == 'interval') or (query == 'average'):
        start= request.args.get('start', default="1m")
        periodstart = start.encode('ascii', 'ignore')
        end = request.args.get('end', default="1m")
        periodend = end.encode('ascii', 'ignore')


        requestbody = {"query": {"constant_score": {"filter": {"bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field":"mac_stats.mac_stats"}}], "must_not": {"term": {"mac_stats": ""}}}}}}, "sort": {"date_time": {"order": "asc"}}}
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['gte']="now"+"-"+periodstart
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['lt']="now"+"-"+periodend
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search', headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}

        if query == 'interval':
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['rsrp'] = [i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrp']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        elif query == 'average':
            sum_rsrp = [i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrp']for i in json.loads(response.text)['hits']['hits']]
            result['average_rsrp'] = (sum(sum_rsrp) / len(sum_rsrp))
            return json.dumps(result), 200
        else:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400

    elif query == 'latest':
        requestbody = {"size": 1, "query": {"constant_score": {"filter": {"bool": {"must": {"exists": {"field": "mac_stats.mac_stats"}}, "must_not": {"term": {"mac_stats": ""}}}}}},"sort": {"date_time": {"order": "desc"}}}
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search',headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}
        try:
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['latest_rsrp'] = [i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrp']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        except:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400


@app.route('/get/rsrq/<string:query>/',methods=['GET'])
def get_rsrq_query(query):
    """
        @api {get} /get/rsrq/:query Extract the values of rsrq
        @apiVersion 1.0.0
        @apiName get_rsrq_by_query
        @apiGroup MacStatsQueries
        @apiParam {string} start The time before now to start searching for the values (i.e 2m, 3h, 5d , 3h/h etc)
        @apiParam {string} end The time (before now and after start) to end searching for the values (i.e 2m, 3h, 5d , 3h/h etc)

        @apiDescription Return either all, average, or the latest value in mac_stats. For all values, it will return maximum 10 values with ascending order time.
        For average values, it will return the average within the given period time.
        For the latest values, it will return the latest available rsrq value and print the time.
        Both start and end parameters are required for `all` and `interval` query. Allowed formats for times are as follows: X`s`,`m`,`h`,`d`,`y` for basics or `/d` in the end to round the time.(i.e 3d/d will round to 3 days ago 24:00h)

        @apiExample Example usage:
        curl -X GET "http://elasticmonserver:port/get/rsrq/interval/?start=10d&end=2d"
        curl -X GET "http://elasticmonserver:port/get/rsrq/average/?start=3d&end=1s"
        curl -X GET 'http://localhost:5000/get/rsrq/latest/'

        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T10:20:05.606",
            "2019-06-26T10:20:05.706",
            "2019-06-26T10:20:05.806",
            "2019-06-26T10:20:05.906",
            "2019-06-26T10:20:06.006",
            "2019-06-26T10:20:06.106",
            "2019-06-26T10:20:06.206",
            "2019-06-26T10:20:06.306",
            "2019-06-26T10:20:06.406",
            "2019-06-26T10:20:06.506",
            ],
        "rsrq": [
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1
            ]
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "average_rsrq": -1
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "date_time": [
            "2019-06-26T11:56:02.140"
            ],
        "rsrq": [
            -1
            ]
        }
        HTTP/1.1 200 OK


        @apiErrorExample {json} Error-Response:
        HTTP/1.1 400 BadRequest
    """

    if (query == 'interval') or (query == 'average'):
        start= request.args.get('start', default="1m")
        periodstart = start.encode('ascii', 'ignore')
        end = request.args.get('end', default="1m")
        periodend = end.encode('ascii', 'ignore')


        requestbody = {"query": {"constant_score": {"filter": {"bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field":"mac_stats.mac_stats"}}], "must_not": {"term": {"mac_stats": ""}}}}}}, "sort": {"date_time": {"order": "asc"}}}
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['gte']="now"+"-"+periodstart
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['lt']="now"+"-"+periodend
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search', headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}

        if query == 'interval':
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['rsrq'] = [i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrq']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        elif query == 'average':
            sum_rsrq = [i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrq']for i in json.loads(response.text)['hits']['hits']]
            result['average_rsrq'] = (sum(sum_rsrq) / len(sum_rsrq))
            return json.dumps(result), 200
        else:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400

    elif query == 'latest':
        requestbody = {"size": 1, "query": {"constant_score": {"filter": {"bool": {"must": {"exists": {"field": "mac_stats.mac_stats"}}, "must_not": {"term": {"mac_stats": ""}}}}}},"sort": {"date_time": {"order": "desc"}}}
        response = requests.get('http://' + ElasticMON_URL + '/mac_stats' + '/_search',headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
        result = {}
        try:
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            result['latest_rsrq'] = [i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrq']for i in json.loads(response.text)['hits']['hits']]
            return json.dumps(result), 200
        except:
            result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
            return json.dumps(result), 400


@app.route('/get/dlBandwidth/', methods=['GET'])
def get_dlbandwidth():

    start = request.args.get('start', default="1m")
    periodstart = start.encode('ascii', 'ignore')
    end = request.args.get('end', default="1m")
    periodend = end.encode('ascii', 'ignore')

    requestbody = {"query": {"constant_score": {"filter": {"bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field": "eNB_config"}}], "must_not": {"term": {"eNB_config": ""}}}}}},"sort": {"date_time": {"order": "desc"}}}
    requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['gte'] = "now" + "-" + periodstart
    requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['lt'] = "now" + "-" + periodend
    response = requests.get('http://' + ElasticMON_URL + '/enb_config' + '/_search',headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
    result = {}
    try:
        result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
        result['dlBandwidth'] = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['dlBandwidth']for i in json.loads(response.text)['hits']['hits']]
        return json.dumps(result), 200
    except:
        result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
        return json.dumps(result), 400


@app.route('/get/throughput/<string:dir>', methods=['GET'])
def get_latest_throughput(dir):
    """
            @api {get} /get/throughput/:dir Calculate the latest throughput
            @apiVersion 1.0.0
            @apiName get_latest_throughput
            @apiGroup CalculationQueries
            @apiParam {string} dir Defines downlink or uplink direction. Allowed values: `dl`, `ul`

            @apiDescription Calculate the latest throughput in a given direction, either downlink or uplink, and print the time. This API assumes that no MIMO is enabled (one single antenna)he time.(i.e 3d/d will round to 3 days ago 24:00h)

            @apiExample Example usage:
            curl -X GET "http://elasticmonserver:port/get/throughput/dl"
            curl -X GET "http://elasticmonserver:port/get/throughput/ul"

            @apiSuccessExample {json} Success-Response:
            {
            "date_time": [
                "2019-07-10T05:59:12.704"
                ],
            "throughput_dl": 36.696
            }
            HTTP/1.1 200 OK

            @apiSuccessExample {json} Success-Response:
            {
            "date_time": [
                "2019-07-10T05:59:12.704"
                ],
            "throughput_ul": 15.264
            }
            HTTP/1.1 200 OK

            @apiErrorExample {json} Error-Response:
            HTTP/1.1 400 BadRequest
        """

    requestbody = {"size": 1, "query": {"constant_score": {"filter": {"bool": {"must": {"exists": {"field": "eNB_config"}}, "must_not": {"term": {"eNB_config": ""}}}}}},"sort": {"date_time": {"order": "desc"}}}
    response = requests.get('http://' + ElasticMON_URL + '/enb_config' + '/_search',headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
    result = {}
    enable64QAM = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['enable64QAM']for i in json.loads(response.text)['hits']['hits']]

    try:
        if dir == 'dl':
            mcs = 28
            tbs_index = 26
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            dlBandwidth = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['dlBandwidth']for i in json.loads(response.text)['hits']['hits']]
            print dlBandwidth

            if int("".join(map(str,dlBandwidth))) == 6:
                prb = 4392
            elif int("".join(map(str,dlBandwidth))) == 15:
                prb = 11064
            elif int("".join(map(str,dlBandwidth))) == 25:
                prb = 18336
            if int("".join(map(str,dlBandwidth))) == 50:
                prb = 36696
            else:
                prb = 75376

#           result['throughput_dl'] = prb * 1000 * 1 / 10^6
            result['throughput_dl'] = prb * 0.001 * 1
            return json.dumps(result), 200

        elif dir == 'ul' and int("".join(map(str,enable64QAM))) == 0:
            mcs = 16
            tbs_index = 15
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            ulBandwidth = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['ulBandwidth'] for i in json.loads(response.text)['hits']['hits']]

            if int("".join(map(str,ulBandwidth))) == 6:
                prb = 1800
            elif int("".join(map(str,ulBandwidth))) == 15:
                prb = 4584
            elif int("".join(map(str,ulBandwidth))) == 25:
                prb = 7736
            if int("".join(map(str,ulBandwidth))) == 50:
                prb = 15264
            else:
                prb = 30576

            result['throughput_ul'] = prb * 0.001 * 1
            return json.dumps(result), 200

        elif dir == 'ul' and int("".join(map(str,enable64QAM))) != 0:
            mcs = 28
            tbs_index = 26
            result['date_time'] = [i['_source']['date_time'] for i in json.loads(response.text)['hits']['hits']]
            ulBandwidth = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['ulBandwidth'] for i in json.loads(response.text)['hits']['hits']]

            if int("".join(map(str,ulBandwidth))) == 6:
                prb = 4392
            elif int("".join(map(str,ulBandwidth))) == 15:
                prb = 11064
            elif int("".join(map(str,ulBandwidth))) == 25:
                prb = 18336
            elif int("".join(map(str,ulBandwidth))) == 50:
                prb = 36696
            else:
                prb = 75376

            result['throughput_ul'] = prb * 0.001 * 1
            return json.dumps(result), 200

    except:
        result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
        return json.dumps(result), 400


@app.route('/get/average/throughput/<string:dir>/', methods=['GET'])
def get_average_throughput(dir):
    """
        @api {get} /get/throughput/:dir Calculate the average throughput
        @apiVersion 1.0.0
        @apiName get_average_throughput
        @apiGroup CalculationQueries
        @apiParam {string} dir Defines downlink or uplink direction. Allowed values: `dl`, `ul`
        @apiParam {string} start The time before now to start searching for the values (i.e 2m, 3h, 5d , 3h/h etc)
        @apiParam {string} end The time (before now and after start) to end searching for the values (i.e 2m, 3h, 5d, 3h/h etc)

        @apiDescription Calculate the average throughput in a given direction, either downlink or uplink, within a given period time.
        This API assumes that no MIMO is enabled (one single antenna).
        Allowed formats for times are as follows: X`s`,`m`,`h`,`d`,`y` for basics or `/d` in the end to round the time.(i.e 3d/d will round to 3 days ago 24:00h)

        @apiExample Example usage:
        curl -X GET "http://elasticmonserver:port/get/average/throughput/dl/?start=3d&end=0s"
        curl -X GET "http://elasticmonserver:port/get/average/throughput/ul/?start=3d&end=0s"

        @apiSuccessExample {json} Success-Response:
        {
        "average_throughput_dl": 36.696
        }
        HTTP/1.1 200 OK

        @apiSuccessExample {json} Success-Response:
        {
        "average_throughput_ul": 15.264
        }
        HTTP/1.1 200 OK

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 400 BadRequest
    """

    start = request.args.get('start', default="2s")
    periodstart = start.encode('ascii', 'ignore')
    end = request.args.get('end', default="0s")
    periodend = end.encode('ascii', 'ignore')

    requestbody = {"query": {"constant_score": {"filter": {"bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field": "eNB_config"}}], "must_not": {"term": {"eNB_config": ""}}}}}},"sort": {"date_time": {"order": "asc"}}}
    requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['gte']="now"+"-"+periodstart
    requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time']['lt']="now"+"-"+periodend
    response = requests.get('http://' + ElasticMON_URL + '/enb_config' + '/_search',headers={'Content-Type': 'application/json'}, data=str(requestbody).replace("'", '"'))
    result = {}

    enable64QAM = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['enable64QAM']for i in json.loads(response.text)['hits']['hits']]

    try:
        if dir == 'dl':
            mcs = 28
            tbs_index = 26
            dlBandwidth = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['dlBandwidth']for i in json.loads(response.text)['hits']['hits']]
            throughput_list = []

            for i in dlBandwidth:
                if i == 6:
                    prb = 4392
                    throughput_dl = prb * 0.001 * 1
                    throughput_list.append(throughput_dl)
                elif i == 15:
                    prb = 11064
                    throughput_dl = prb * 0.001 * 1
                    throughput_list.append(throughput_dl)
                elif i == 25:
                    prb = 18336
                    throughput_dl = prb * 0.001 * 1
                    throughput_list.append(throughput_dl)
                elif i == 50:
                    prb = 36696
                    throughput_dl = prb * 0.001 * 1
                    throughput_list.append(throughput_dl)
                else:
                    prb = 75376
                    throughput_dl = prb * 0.001 * 1
                    throughput_list.append(throughput_dl)

            result['average_throughput_dl'] = sum(throughput_list) / len(throughput_list)
            return json.dumps(result), 200

        elif dir == 'ul' and int("".join(map(str,enable64QAM))) == 0:
            mcs = 16
            tbs_index = 15
            ulBandwidth = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['ulBandwidth'] for i in json.loads(response.text)['hits']['hits']]
            throughput_list = []

            for i in ulBandwidth:
                if i == 6:
                    prb = 1800
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                elif i == 15:
                    prb = 4584
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                elif i == 25:
                    prb = 7736
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                elif i == 50:
                    prb = 15264
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                else:
                    prb = 30576
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)

            result['average_throughput_ul'] = sum(throughput_list) / len(throughput_list)
            return json.dumps(result), 200

        elif dir == 'ul' and int("".join(map(str,enable64QAM))) != 0:
            mcs = 28
            tbs_index = 26
            ulBandwidth = [i['_source']['eNB_config'][0]['eNB']['cellConfig'][0]['ulBandwidth'] for i in json.loads(response.text)['hits']['hits']]
            throughput_list = []

            for i in ulBandwidth:
                if i == 6:
                    prb = 4392
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                elif i == 15:
                    prb = 11064
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                elif i == 25:
                    prb = 18336
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                elif i == 50:
                    prb = 36696
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)
                else:
                    prb = 75376
                    throughput_ul = prb * 0.001 * 1
                    throughput_list.append(throughput_ul)

            result['average_throughput_ul'] = sum(throughput_list) / len(throughput_list)
            return json.dumps(result), 200

    except:
        result['error'] = json.loads(response.text)['error']['root_cause'][0]['reason']
        return json.dumps(result), 400


if __name__ == "__main__":

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('192.168.12.98', 9999))
    if result == 0:
        sock.close()
        print "FlexRAN is running"
        req = requests.get(url_flexran + '/elasticmon')
        json_data = json.loads(req.text)
        flex_producer = str(json_data['active'])
        endpoint = json_data['endpoint']
        response = {}

        if any(ElasticMON_URL in s for s in endpoint):
            if flex_producer == 'False':
                req_enable = requests.post(url_flexran + '/elasticmon/enable')
                if req_enable.status_code == 200:
                    print "OK"
                else:
                    print json.dumps(response), 400
            else:
                print "FlexRAN producer has been activated"

            app.run()

        else:
            print "Please add ElasticSearch endpoint via FlexRAN!"

    else:
        sock.close()
        print "Make sure FlexRAN is running!"
        pass
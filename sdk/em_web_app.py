from lib import elasticmon_web_sdk_git
from flask import Flask
from flask import request
import json
import requests
import socket

ElasticMON_URL = "192.168.12.98:9200"
url_flexran = "http://192.168.12.98:9999"

app = Flask(__name__)


@app.route('/')
def init():
    return 'Greetings from ElasticMON Webserver'


@app.route('/enb/get/<string:query>/<string:value>/', methods=['GET'])
def enb_query_value(query, value): # (enb=0, ue=0, key, func, t_start=0, t_end=now, dir='dl')
    result = {}
    start = request.args.get('start', default="1m").encode('ascii', 'ignore')
    end = request.args.get('end', default="0s").encode('ascii', 'ignore')
    dir = request.args.get('dir', default="ul").encode('ascii', 'ignore')
    enb = int(request.args.get('enb', default="0"))
    cc = int(request.args.get('cc', default="0"))

    if query == 'latest':
        init = elasticmon_web_sdk_git.get_enb_config(ElasticMON_URL, query, "", "")
        result['date_time'] = init.get_date_time()
        try:
            if value == 'rb':
                result['resource_block'] = init.get_cell_rb(enb, cc, dir)
            elif value == 'max_mcs':
                result['maximum_MCS'] = init.get_cell_maxmcs(enb, cc, dir)
            else:
                result['message'] = ['variable not exist']
            return json.dumps(result), 200
        except:
            result['error'] = init.get_error()
            return json.dumps(result), 400

    elif (query == 'interval') or (query == 'average'):
        init = elasticmon_web_sdk_git.get_enb_config(ElasticMON_URL, query, start, end)
        if query == 'interval':
            result['date_time'] = init.get_date_time()
            try:
                if value == 'rb':
                    result['resource_block'] = init.get_cell_rb(enb, cc, dir)
                elif value == 'num_enb':
                    result['num_enb'] = init.get_num_enb()
                elif value == 'bw':
                    result['bandwidth'] = init.get_cell_bw(enb, cc, dir)
                else:
                    result['message'] = ['variable not exist']
                return json.dumps(result), 200
            except:
                result['error'] = init.get_error()
                return json.dumps(result), 400
            
        elif query == 'average':
            try:
                if value == 'rb':
                    result['average_rb'] = (sum(init.get_cell_rb(enb, cc, dir)) / len(init.get_cell_rb(enb, cc, dir)))
                elif value == 'bw':
                    result['average_bandwidth'] = (sum(init.get_cell_bw(enb, cc, dir)) / len(init.get_cell_bw(enb, cc, dir)))
                else:
                    result['message'] = ['variable not exist']
                return json.dumps(result), 200
            except:
                result['error'] = init.get_error()
                return json.dumps(result), 400
    else:
        return 0


@app.route('/mac/get/<string:query>/<string:value>/', methods=['GET'])
def mac_query_value(query, value):
    result = {}
    start = request.args.get('start', default="1m").encode('ascii', 'ignore')
    end = request.args.get('end', default="0s").encode('ascii', 'ignore')
    dir = request.args.get('dir', default="ul").encode('ascii', 'ignore')

    if query == 'latest':
        init = elasticmon_web_sdk_git.get_mac_stats(ElasticMON_URL, query, "", "")

        result['date_time'] = init.get_date_time()
        try:
            if value == 'rnti':
                result['rnti'] = init.get_rnti()
            elif value == 'wbcqi':
                result['wbcqi'] = init.get_wbcqi()
            elif value == 'phr':
                result['phr'] = init.get_phr()
            elif value == 'rsrp':
                result['rsrp'] = init.get_rsrp()
            elif value == 'rsrq':
                result['rsrq'] = init.get_rsrq()
            elif value == 'ue_pdcp_pkt':
                result['ue_pdcp_pkt'] = init.get_ue_pdcp_pkt(dir)
            else:
                result['message'] = ['variable not exist']

            return json.dumps(result), 200

        except:
            result['error'] = [init.get_error()]
            return json.dumps(result), 400

    elif (query == 'interval')  or (query == 'average'):
        init = elasticmon_web_sdk_git.get_mac_stats(ElasticMON_URL, query, start, end)
        if query == 'interval':
            result['date_time'] = init.get_date_time()
            try:
                if value == 'rnti':
                    result['rnti'] = init.get_rnti()
                elif value == 'wbcqi':
                    result['wbcqi'] = init.get_wbcqi()
                elif value == 'phr':
                    result['phr'] = init.get_phr()
                elif value == 'rsrp':
                    result['rsrp'] = init.get_rsrp()
                elif value == 'rsrq':
                    result['rsrq'] = init.get_rsrq()
                else:
                    result['message'] = ['variable not exist']

                return json.dumps(result), 200

            except:
                result['error'] = [init.get_error()]
                return json.dumps(result), 400

        elif query == 'average':
            try:
                if value == 'rnti':
                    result['average_rnti'] = (sum(init.get_rnti()) / len(init.get_rnti()))
                elif value == 'wbcqi':
                    result['wbcqi'] = (sum(init.get_wbcqi()) / len(init.get_wbcqi()))
                elif value == 'phr':
                    result['phr'] = (sum(init.get_phr()) / len(init.get_phr()))
                elif value == 'rsrp':
                    result['rsrp'] = (sum(init.get_rsrp()) / len(init.get_rsrp()))
                elif value == 'rsrq':
                    result['rsrq'] = (sum(init.get_rsrq()) / len(init.get_rsrq()))
                else:
                    result['message'] = ['variable not exist']

                return json.dumps(result), 200

            except:
                result['error'] = [init.get_error()]
                return json.dumps(result), 400
    else:
        return 0


if __name__ == "__main__":

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect = sock.connect_ex(('192.168.12.98', 9999))
    if connect == 0:
        sock.close()
        print "FlexRAN is running"
        req = requests.get(url_flexran + '/elasticmon')
        json_data = json.loads(req.text)
        flex_producer = str(json_data['active'])
        endpoint = json_data['endpoint']
        response = {}

        if not any (ElasticMON_URL in s for s in endpoint):
            req = requests.post(url_flexran + '/elasticmon/endpoint/' + ElasticMON_URL)
            print "ElasticSearch endpoint has been added to FlexRAN"
        else:
            print "ElasticSearch endpoint exists in FlexRAN"

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
        sock.close()
        print "Make sure FlexRAN is running!"
        pass

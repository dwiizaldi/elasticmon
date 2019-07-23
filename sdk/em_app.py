from lib import elasticmon_sdk_git
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


@app.route('/get/<string:query>/<string:value>/', methods=['GET'])
def query_value(query, value):
    result = {}
    start = request.args.get('start', default="1m")
    periodstart = start.encode('ascii', 'ignore')
    end = request.args.get('end', default="0s")
    periodend = end.encode('ascii', 'ignore')

    if query == 'latest':
        init = elasticmon_sdk_git.get_mac_stats(ElasticMON_URL, query, "", "")

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
            elif value == 'pdcpbyte_ul':
                result['pdcp_byte_ul'] = init.get_pdcp_byte_ul()
            elif value == 'pdcpbyte_dl':
                result['pdcp_byte_dl'] = init.get_pdcp_byte_dl()
            else:
                result['message'] = ['variable not exist']

            return json.dumps(result), 200

        except:
            result['error'] = [init.get_error()]
            return json.dumps(result), 400

    elif (query == 'interval')  or (query == 'average'):
        init = elasticmon_sdk_git.get_mac_stats(ElasticMON_URL, query, periodstart, periodend)
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
                elif value == 'pdcpbyte_ul':
                    result['pdcp_byte_ul'] = init.get_pdcp_byte_ul()
                elif value == 'pdcpbyte_dl':
                    result['pdcp_byte_dl'] = init.get_pdcp_byte_dl()
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
                elif value == 'pdcpbyte_ul':
                    result['pdcp_byte_ul'] = (sum(init.get_pdcp_byte_ul()) / len(init.get_pdcp_byte_ul()))
                elif value == 'pdcpbyte_dl':
                    result['pdcp_byte_dl'] = (sum(init.get_pdcp_byte_dl()) / len(init.get_pdcp_byte_dl()))
                else:
                    result['message'] = ['variable not exist']

                return json.dumps(result), 200

            except:
                result['error'] = [init.get_error()]
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
import requests

class url_api(object):

    url_mac_stats = 'http://192.168.12.98:9200/mac_stats/_search'
    url_enb_config = 'http://192.168.12.98:9200/enb_config/_search'

class get_mac_stats(object):

    def __init__(self, url, query, start, end):

        self.query = query
        self.data = []
        self.url = url
        self.status = 0
        self.result = {}
        self.start = start
        self.end = end

        if (self.query == 'interval') or (self.query == 'average'):
            requestbody = {"query": {"constant_score": {"filter": {"bool": {
                "must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}},
                         {"exists": {"field": "mac_stats.mac_stats"}}], "must_not": {"term": {"mac_stats": ""}}}}}},
                           "sort": {"date_time": {"order": "asc"}}}
            requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'gte'] = "now" + "-" + self.start
            requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'lt'] = "now" + "-" + self.end

        elif (self.query == 'latest'):
            requestbody = {"size": 1, "query": {"constant_score": {"filter": {
                "bool": {"must": {"exists": {"field": "mac_stats.mac_stats"}},
                         "must_not": {"term": {"mac_stats": ""}}}}}}, "sort": {"date_time": {"order": "desc"}}}

        try:
            response = requests.get(url_api.url_mac_stats, headers={'Content-Type': 'application/json'},
                                    data=str(requestbody).replace("'", '"'))
            self.data = response.json()

        except:
            pass

    def get_error(self):
        error = self.data['error']['root_cause'][0]['reason']
        return error

    def get_date_time(self):
        date_list = []
        for i in self.data['hits']['hits']:
            date_time = i['_source']['date_time']
            date_list.append(date_time)
        return date_list

    def get_rnti(self):
        rnti_list = []
        for i in self.data['hits']['hits']:
            rnti = i['_source']['mac_stats']['rnti']
            rnti_list.append(rnti)
        return rnti_list

    def get_wbcqi(self):
        wbcqi_list = []
        for i in self.data['hits']['hits']:
            wbcqi = i['_source']['mac_stats']['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi']
            wbcqi_list.append(wbcqi)
        return wbcqi_list

    def get_phr(self):
        phr_list = []
        for i in self.data['hits']['hits']:
            phr = i['_source']['mac_stats']['mac_stats']['phr']
            phr_list.append(phr)
        return phr_list

    def get_rsrp(self):
        rsrp_list = []
        for i in self.data['hits']['hits']:
            rsrp = i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrp']
            rsrp_list.append(rsrp)
        return rsrp_list

    def get_rsrq(self):
        rsrq_list = []
        for i in self.data['hits']['hits']:
            rsrq = i['_source']['mac_stats']['mac_stats']['rrcMeasurements']['pcellRsrq']
            rsrq_list.append(rsrq)
        return rsrq_list

    def get_pdcp_byte_dl(self):
        pdcp_byte_dl_list = []
        for i in self.data['hits']['hits']:
            pdcpByteDl = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTxBytes']
            pdcp_byte_dl_list.append(pdcpByteDl)
        return pdcp_byte_dl_list

    def get_pdcp_byte_ul(self):
        pdcp_byte_ul_list = []
        for i in self.data['hits']['hits']:
            pdcpByteUl = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxBytes']
            pdcp_byte_ul_list.append(pdcpByteUl)
        return pdcp_byte_ul_list


class get_enb_config(object):

    def __init__(self, log, url='http://192.168.12.98', port='9200', query='average'):
        self.url = url + ':' + port
        self.query = query
        self.status = 0
        self.log = log
        self.stats_data = ''


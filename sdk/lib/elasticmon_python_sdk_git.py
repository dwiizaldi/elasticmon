import requests

class url_api(object):

    url_mac_stats = 'http://192.168.12.98:9200/mac_stats/_search'
    url_enb_config = 'http://192.168.12.98:9200/enb_config/_search'


class mac_stats(object):

    def __init__(self, enb, ue, key, t_start, t_end, dir):
        super(mac_stats, self).__init__()
        self.data = []
        self.enb = enb
        self.ue = ue
        self.key = key
        self.t_start = t_start
        self.t_end = t_end
        self.dir = dir
        self.path_key = self.get_path_key()

        requestbody = {"query": {"constant_score": {"filter": {
            "bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}},
                              {"exists": {"field": "mac_stats.mac_stats"}}],
                     "must_not": {"term": {"mac_stats.mac_stats": ""}}}}}},
            "sort": {"date_time": {"order": "desc"}},
            "aggs": {"value_in_range": {
                "date_range": {"field": "date_time", "ranges": {"from": "now", "to": "now"}},
                "aggs": {"stats_value": {"stats": {"field": "mac_stats.mac_stats."}}}}}}

        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'gte'] = "now" + "-" + self.t_start
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'lt'] = "now" + "-" + self.t_end
        requestbody['aggs']['value_in_range']['date_range']['ranges']['from'] = "now" + "-" + self.t_start
        requestbody['aggs']['value_in_range']['date_range']['ranges']['to'] = "now" + "-" + self.t_end
        requestbody['aggs']['value_in_range']['aggs']['stats_value']['stats'][
                'field'] = "mac_stats.mac_stats." + self.path_key

        try:
            response = requests.get(url_api.url_mac_stats, headers={'Content-Type': 'application/json'},
                                    data=str(requestbody).replace("'", '"'))
            self.data = response.json()

        except:
            error = self.data['error']['root_cause'][0]['reason']
            return error

    def get_path_key(self):
        if self.key == 'rnti':
            path = 'rnti'
        elif self.key == 'phr':
            path = 'phr'
        elif self.key == 'wbcqi':
            path = 'dlCqiReport.csiReport.p10csi.wbCqi'
        elif self.key == 'rsrp':
            path = 'rrcMeasurements.pcellRsrp'
        elif self.key == 'rsrq':
            path = 'rrcMeasurements.pcellRsrq'
        elif self.key == 'enb_sfn':
            path = 'dlCqiReport.sfnSn'
        elif self.key == 'pdcp_sfn':
            path = 'pdcpStats.sfn'
        elif self.key == 'ue_pdcp_pkt':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRx'
            else:
                path = 'pdcpStats.pktTx'
        elif self.key == 'ue_pdcp_pkt_bytes':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRxBytes'
            else:
                path = 'pdcpStats.pktTxBytes'
        elif self.key == 'ue_pdcp_pkt_sn':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRxSn'
            else:
                path = 'pdcpStats.pktTxSn'
        elif self.key == 'ue_pdcp_pkt_w':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRxW'
            else:
                path = 'pdcpStats.pktTxW'
        elif self.key == 'ue_pdcp_pkt_aiat':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRxAiat'
            else:
                path = 'pdcpStats.pktTxAiat'
        elif self.key == 'ue_pdcp_pkt_bytes_w':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRxBytesW'
            else:
                path = 'pdcpStats.pktTxBytesW'
        elif self.key == 'ue_pdcp_pkt_aiat_w':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRxAiatW'
            else:
                path = 'pdcpStats.pktTxAiatW'
        elif self.key == 'ue_pdcp_pkt_oo':
            if self.dir == 'ul':
                path = 'pdcpStats.pktRxOo'
            else:
                path = 'pdcpStats.pktRxOo'
        else:
            return 0
        return path

    def get_avg(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['avg']

    def get_min(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['min']

    def get_max(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['max']

    def get_sum(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['sum']

    def get_count(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['count']


class enb_config(object):

    def __init__(self, enb, ue, key, t_start, t_end, dir):
        super(enb_config, self).__init__()
        self.data = []
        self.enb = enb
        self.ue = ue
        self.key = key
        self.t_start = t_start
        self.t_end = t_end
        self.dir = dir
        self.path_key = self.get_path_key()

        requestbody = {"size": 1, "query": {"constant_score": {"filter": {"bool": {
            "must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field": "eNB_config"}}],
            "must_not": {"term": {"eNB_config": ""}}}}}}, "sort": {"date_time": {"order": "asc"}}, "aggs": {
            "value_in_range": {"date_range": {"field": "date_time", "ranges": {"from": "now", "to": "now"}},
                               "aggs": {"stats_value": {"stats": {"field": "eNB_config."}}}}}}
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
            'gte'] = "now" + "-" + self.t_start
        requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
            'lt'] = "now" + "-" + self.t_end
        requestbody['aggs']['value_in_range']['date_range']['ranges']['from'] = "now" + "-" + self.t_start
        requestbody['aggs']['value_in_range']['date_range']['ranges']['to'] = "now" + "-" + self.t_end
        requestbody['aggs']['value_in_range']['aggs']['stats_value']['stats']['field'] = "eNB_config." + self.path_key

        try:
            response = requests.get(url_api.url_enb_config, headers={'Content-Type': 'application/json'},
                                data=str(requestbody).replace("'", '"'))
            self.data = response.json()

        except:
            error = self.data['error']['root_cause'][0]['reason']
            return error

    def get_path_key(self):
        if self.key == 'cell_rb':
            if self.dir == 'ul':
                path = 'eNB.cellConfig.ulBandwidth'
            else:
                path = 'eNB.cellConfig.dlBandwidth'
        if self.key == 'cell_freq':
            if self.dir == 'ul':
                path = 'eNB.cellConfig.ulFreq'
            else:
                path = 'eNB.cellConfig.dlFreq'
        if self.key == 'cell_power':
            if self.dir == 'ul':
                path = 'eNB.cellConfig.ulPuschPower'
            else:
                path = 'eNB.cellConfig.dlPdschPower'
        if self.key == 'cell_band':
            path = 'eNB.cellConfig.eutraBand'

        return path

    def get_avg(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['avg']

    def get_min(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['min']

    def get_max(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['max']

    def get_sum(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['sum']

    def get_count(self):
        return self.data['aggregations']['value_in_range']['buckets'][0]['stats_value']['count']








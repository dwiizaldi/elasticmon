import requests


class url_api(object):

    url_mac_stats = 'http://192.168.12.98:9200/mac_stats/_search'
    url_enb_config = 'http://192.168.12.98:9200/enb_config/_search'


class get_mac_stats(object):

    def __init__(self, url, query, start, end):

        self.query = query
        self.data = []
        self.url = url
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

    def get_enb_sfn(self):
        enb_sfn_list = []
        for i in self.data['hits']['hits']:
            enb_sfn = i['_source']['mac_stats']['mac_stats']['dlCqiReport']['sfnSn']
            enb_sfn_list.append(enb_sfn)
        return enb_sfn_list

    def get_enb_pdcp_sfn(self):
        enb_pdcp_sfn_list = []
        for i in self.data['hits']['hits']:
            enb_pdcp_sfn = i['_source']['mac_stats']['mac_stats']['pdcpStats']['sfn']
            enb_pdcp_sfn_list.append(enb_pdcp_sfn)
        return enb_pdcp_sfn_list

    def get_ue_pdcp_pkt(self, dir):
        ue_pdcp_pkt_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRx']
                ue_pdcp_pkt_list.append(ue_pdcp_pkt)
            elif dir == 'dl':
                ue_pdcp_pkt = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTx']
                ue_pdcp_pkt_list.append(ue_pdcp_pkt)
        return ue_pdcp_pkt_list

    def get_ue_pdcp_pkt_bytes(self, dir):
        ue_pdcp_pkt_bytes_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt_bytes = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxBytes']
                ue_pdcp_pkt_bytes_list.append(ue_pdcp_pkt_bytes)
            elif dir == 'dl':
                ue_pdcp_pkt_bytes = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTxBytes']
                ue_pdcp_pkt_bytes_list.append(ue_pdcp_pkt_bytes)
        return ue_pdcp_pkt_bytes_list

    def get_ue_pdcp_pkt_sn(self, dir):
        ue_pdcp_pkt_sn_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt_sn = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxSn']
                ue_pdcp_pkt_sn_list.append(ue_pdcp_pkt_sn)
            elif dir == 'dl':
                ue_pdcp_pkt_sn = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTxSn']
                ue_pdcp_pkt_sn_list.append(ue_pdcp_pkt_sn)
        return ue_pdcp_pkt_sn_list

    def get_ue_pdcp_pkt_w(self, dir):
        ue_pdcp_pkt_w_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt_w = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxW']
                ue_pdcp_pkt_w_list.append(ue_pdcp_pkt_w)
            elif dir == 'dl':
                ue_pdcp_pkt_w = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTxW']
                ue_pdcp_pkt_w_list.append(ue_pdcp_pkt_w)
        return ue_pdcp_pkt_w_list

    def get_ue_pdcp_pkt_aiat(self, dir):
        ue_pdcp_pkt_aiat_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt_aiat = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxAiat']
                ue_pdcp_pkt_aiat_list.append(ue_pdcp_pkt_aiat)
            elif dir == 'dl':
                ue_pdcp_pkt_aiat = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTxAiat']
                ue_pdcp_pkt_aiat_list.append(ue_pdcp_pkt_aiat)
        return ue_pdcp_pkt_aiat_list

    def get_ue_pdcp_pkt_bytes_w(self, dir):
        ue_pdcp_pkt_bytes_w_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt_bytes_w = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxBytesW']
                ue_pdcp_pkt_bytes_w_list.append(ue_pdcp_pkt_bytes_w)
            elif dir == 'dl':
                ue_pdcp_pkt_bytes_w = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTxBytesW']
                ue_pdcp_pkt_bytes_w_list.append(ue_pdcp_pkt_bytes_w)
        return ue_pdcp_pkt_bytes_w_list

    def get_ue_pdcp_pkt_aiat_w(self, dir):
        ue_pdcp_pkt_aiat_w_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt_aiat_w = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxAiatW']
                ue_pdcp_pkt_aiat_w_list.append(ue_pdcp_pkt_aiat_w)
            elif dir == 'dl':
                ue_pdcp_pkt_aiat_w = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktTxAiatW']
                ue_pdcp_pkt_aiat_w_list.append(ue_pdcp_pkt_aiat_w)
        return ue_pdcp_pkt_aiat_w_list

    def get_ue_pdcp_pkt_oo(self, dir):
        ue_pdcp_pkt_oo_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                ue_pdcp_pkt_oo = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxOo']
                ue_pdcp_pkt_oo_list.append(ue_pdcp_pkt_oo)
            else:
                ue_pdcp_pkt_oo = i['_source']['mac_stats']['mac_stats']['pdcpStats']['pktRxOo']
                ue_pdcp_pkt_oo_list.append(ue_pdcp_pkt_oo)
        return ue_pdcp_pkt_oo_list


class get_enb_config(object):

    def __init__(self, url, query, start, end):

        self.query = query
        self.data = []
        self.url = url
        self.result = {}
        self.start = start
        self.end = end

        if (self.query == 'interval') or (self.query == 'average'):
            requestbody = {"query": {"constant_score": {"filter": {"bool": {
                "must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field": "eNB_config"}}],
                "must_not": {"term": {"eNB_config": ""}}}}}}, "sort": {"date_time": {"order": "asc"}}}
            requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'gte'] = "now" + "-" + self.start
            requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'lt'] = "now" + "-" + self.end

        elif self.query == 'latest':
            requestbody = {"size": 1, "query": {"constant_score": {"filter": {
                "bool": {"must": [{"exists": {"field": "eNB_config"}}], "must_not": {"term": {"eNB_config": ""}}}}}},
                           "sort": {"date_time": {"order": "desc"}}}

        try:
            response = requests.get(url_api.url_enb_config, headers={'Content-Type': 'application/json'},
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

    def get_num_enb(self):
        num_enb_list = []
        for i in self.data['hits']['hits']:
            num_enb = i['_source']['eNB_config']
            num_enb_list.append(len(num_enb))
        return num_enb_list

    def get_cell_rb(self, enb, cc, dir):
        rb_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                rb = i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['ulBandwidth']
                rb_list.append(rb)
            elif dir == 'dl':
                rb = i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['dlBandwidth']
                rb_list.append(rb)
        return rb_list

    def get_cell_bw(self, enb, cc, dir):
        rb = self.get_cell_rb(enb, cc, dir)
        bw_list = []
        for i in rb:
            if i == 6:
                bw = 1.4
                bw_list.append(bw)
            elif i == 25:
                bw = 5
                bw_list.append(bw)
            elif i == 50:
                bw = 10
                bw_list.append(bw)
            elif i == 75:
                bw = 15
                bw_list.append(bw)
            elif i == 100:
                bw = 20
                bw_list.append(bw)
        return bw_list

    def get_cell_rbg_size(self, enb, cc, dir):
        rb = self.get_cell_rb(enb, cc, dir)
        rbgsize_list = []
        print rb
        for i in rb:
            if i == 6:
                rbgsize = 1.4
                rbgsize_list.append(rbgsize)
            elif i == 25:
                rbgsize = 5
                rbgsize_list.append(rbgsize)
            elif i == 50:
                rbgsize = 10
                rbgsize_list.append(rbgsize)
            elif i == 75:
                rbgsize = 15
                rbgsize_list.append(rbgsize)
            elif i == 100:
                rbgsize = 20
                rbgsize_list.append(rbgsize)
        return rbgsize_list

    def get_cell_freq(self, enb, cc, dir):
        cell_freq_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                cell_freq = i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['ulFreq']
                cell_freq_list.append(cell_freq)
            elif dir == 'dl':
                cell_freq = i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['dlFreq']
                cell_freq_list.append(cell_freq)
        return cell_freq_list

    def get_cell_power(self, enb, cc, dir):
        cell_power_list = []
        for i in self.data['hits']['hits']:
            if dir == 'ul':
                cell_power = i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['ulPuschPower']
                cell_power_list.append(cell_power)
            elif dir == 'dl':
                cell_power = i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['dlPdschPower']
                cell_power_list.append(cell_power)
        return cell_power_list

    def get_cell_band(self, enb, cc):
        cell_band_list = []
        for i in self.data['hits']['hits']:
            cell_band = i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['eutraBand']
            cell_band_list.append(cell_band)
        return cell_band_list

    def get_cell_maxmcs(self, enb, cc, dir):
        cell_maxmcs_list = []
        for i in self.data['hits']['hits']:
            if dir == 'dl':
                cell_maxmcs = 28
                cell_maxmcs_list.append(cell_maxmcs)
            elif i['_source']['eNB_config'][enb]['eNB']['cellConfig'][cc]['enable64QAM'] == 0:
                cell_maxmcs = 16
                cell_maxmcs_list.append(cell_maxmcs)
            else:
                cell_maxmcs = 28
                cell_maxmcs_list.append(cell_maxmcs)
        return cell_maxmcs_list


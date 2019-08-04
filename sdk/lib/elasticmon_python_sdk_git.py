class url_api(object):

    url_mac_stats = 'http://192.168.12.98:9200/mac_stats/_search'
    url_enb_config = 'http://192.168.12.98:9200/enb_config/_search'

class mac_stats(object):

    def __init__(self, enb, ue, key, func, t_start, t_end, dir):
        self.enb = enb
        self.ue = ue
        self.key = key
        self.func = func
        self.t_start = t_start
        self.t_end = t_end
        self.dir = dir

        if self.func == 'average':
            requestbody = {"query": {"constant_score": {"filter": {
                "bool": {"must": [{"range": {"date_time": {"gte": "now", "lt": "now"}}}, {"exists": {"field": "mac_stats.mac_stats"}}],
                         "must_not": {"term": {"mac_stats.mac_stats": ""}}}}}},
                           "sort": {"date_time": {"order": "desc"}},
                           "aggs": {"average_in_range": {
                               "date_range": {"field": "date_time", "ranges": [{"gte": "now", "lt": "now"}]},
                               "aggs": {"average": {"avg": {"field": "mac_stats.mac_stats."}}}}}}
            requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'gte'] = "now" + "-" + self.t_start
            requestbody['query']['constant_score']['filter']['bool']['must'][0]['range']['date_time'][
                'lt'] = "now" + "-" + self.t_end
            requestbody['aggs']['average_in_range']['date_range']['ranges'][0]['gte'] = "now" + "-" + self.t_start
            requestbody['aggs']['average_in_range']['date_range']['ranges'][0]['lt'] = "now" + "-" + self.t_end
            requestbody['aggs']['average_in_range']['aggs']['average']['avg'][
                'field'] = "mac_stats.mac_stats." + self.key

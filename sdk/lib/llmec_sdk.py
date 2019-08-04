import requests
import json


class llmec_api(object):

    all_stats = '/stats'


class data_stats(object):

    def __init__(self, log, url='http://localhost', port='9999'):
        self.url = url + ':' + port
        self.stats_data = ''
        self.all_stats_api = llmec_api.all_stats
        self.status = 0
        self.log = log

    def stats_all(self, api):
        url = self.url+self.all_stats_api
        try:
            req = requests.get(url)
            if req.status_code == 200:
                self.stats_data = req.json()
                self.status = 'connected'
            else:
                self.status = 'disconnected'
                self.log.error = ('Request error code: ' + req.status_code)
        except:
            self.log.error('Request url ' + url + 'failed')

        if self.status == 'connected':
            self.log.debug('LL-MEC requested data')
            self.log.debug(json.dumps(self.stats_data, indent=2))

    def get_stats(self, id=0):
        return self.stats_data[id]

    def get_ul(self, id=0):
        return self.stats_data[id]['ul']

    def get_dl(self, id=0):
        return self.stats_data[id]['dl']

    def get_byte_count(self, dir='ul', id=0):
        return self.stats_data[id][dir]['byte_count']

    def get_duration_sec(self, dir='ul', id=0):
        return self.stats_data[id][dir]['duration_sec']

    def get_packet_count(self, dir='ul', id=0):
        return self.stats_data[id][dir]['packet_count']

    def get_priority(self, dir='ul', id=0):
        return self.stats_data[id][dir]['priority']

    def get_table_id(self, dir='ul', id=0):
        return self.stats_data[id][dir]['table_id']

    def get_enb_ip(self, id=0):
        return self.stats_data[id]['enb_ip']

    def get_eps_bearer_id(self, id=0):
        return self.stats_data[id]['eps_bearer_id']

    def get_id(self, id=0):
        return self.stats_data[id]['id']

    def get_imsi(self, id=0):
        return self.stats_data[id]['imsi']

    def get_s1_dl_teid(self, id=0):
        return self.stats_data[id]['s1_dl_teid']

    def get_s1_ul_teid(self, id=0):
        return self.stats_data[id]['s1_ul_teid']

    def get_slice_id(self, id=0):
        return self.stats_data[id]['slice_id']

    def get_ue_ip(self, id=0):
        return self.stats_data[id]['ue_ip']
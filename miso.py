import requests
import copy
from dateutil.parser import parse as dateutil_parse
import pytz


class MISOClient:
    def __init__(self):
        self.ba_name = 'MISO'
        
        self.base_url = 'https://www.misoenergy.org/ria/'
        
        self.fuels = {
            'Coal': 'coal',
            'Natural Gas': 'natgas',
            'Nuclear': 'nuclear',
            'Other': 'other',
            'Wind': 'wind',
        }

    def get_generation(self, latest=False, **kwargs):
        # process args
        request_urls = []
        if latest:
            request_urls.append('FuelMix.aspx?CSV=True')

        else:
            raise ValueError('Latest must be True.')
            
        # set up storage
        raw_data = []
        parsed_data = []

        # collect raw data
        for request_url in request_urls:
            # set up request
            url = copy.deepcopy(self.base_url)
            url += request_url
            
            # carry out request
            response = requests.get(url).text
            
            # preliminary parsing
            rows = response.split('\n')
            header = rows[0].split(',')
            for row in rows[1:]:
                raw_data.append(dict(zip(header, row.split(','))))
            
        # parse data
        for raw_dp in raw_data:
            # set up storage
            parsed_dp = {}
            
            naive_local_timestamp = dateutil_parse(raw_dp['INTERVALEST'])
            aware_local_timestamp = pytz.timezone('America/New_York').localize(naive_local_timestamp)
            aware_utc_timestamp = aware_local_timestamp.astimezone(pytz.utc)

            # add values
            try:
                parsed_dp['timestamp'] = aware_utc_timestamp
                parsed_dp['gen_MW'] = raw_dp['ACT']
                parsed_dp['fuel_name'] = self.fuels[raw_dp['CATEGORY']]
                parsed_dp['ba_name'] = self.ba_name
            except KeyError: # blank last line
                continue
            
            # add to full storage
            parsed_data.append(parsed_dp)
            
        return parsed_data
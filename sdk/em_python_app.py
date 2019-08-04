import argparse
from lib import elasticmon_web_sdk_git

parser = argparse.ArgumentParser()

parser.add_argument('--enb', metavar='enb', action='store', type=int, required=False, default='0')
parser.add_argument('--ue', metavar='ue', action='store', type=int, required=False, default='0')
parser.add_argument('--key', metavar='key', action='store', type=str, required=True)
parser.add_argument('--func', metavar='func', action='store', type=str, required=True)
parser.add_argument('--t_start', metavar='time_start', action='store', type=str, required=False, default='1d')
parser.add_argument('--t_end', metavar='time_end', action='store', type=str, required=False, default='0s')
parser.add_argument('--dir', metavar='direction', action='store', type=str, required=False, default='dl')

args = parser.parse_args()
# print(args.enb, args.key)

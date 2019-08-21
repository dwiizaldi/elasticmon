import argparse
from lib import elasticmon_sdk


parser = argparse.ArgumentParser()

parser.add_argument('--enb', metavar='enb', action='store', type=int, required=False, default='0')
parser.add_argument('--ue', metavar='ue', action='store', type=int, required=False, default='0')
parser.add_argument('--key', metavar='key', action='store', type=str, required=True)
parser.add_argument('--func', metavar='func', action='store', type=str, required=True)
parser.add_argument('--t_start', metavar='time_start', action='store', type=str, required=False, default='10s')
parser.add_argument('--t_end', metavar='time_end', action='store', type=str, required=False, default='0s')
parser.add_argument('--dir', metavar='direction', action='store', type=str, required=False, default='dl')
parser.add_argument('--lc', metavar='lc', action='store', type=int, required=False, default=0)

args = parser.parse_args()

try:
    init = elasticmon_sdk.mac_stats(enb=args.enb, ue=args.ue, key=args.key,
                                    t_start=args.t_start, t_end=args.t_end, dir=args.dir)
except:
    init = elasticmon_sdk.enb_config(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start, t_end=args.t_end, dir=args.dir)

if args.func == 'average':
    print args.func + " value of " + args.key + " is " + str(init.get_avg())
elif args.func == 'max':
    print args.func + " value of " + args.key + " is " + str(init.get_max())
elif args.func == 'min':
    print args.func + " value of " + args.key + " is " + str(init.get_min())
elif args.func == 'count':
    print args.func + " value of " + args.key + " is " + str(init.get_count())
elif args.func == 'sum':
    print args.func + " value of " + args.key + " is " + str(init.get_sum())
elif args.func == 'range':
    print args.func + " value of " + args.key + " is " + str(init.get_range(args.key))
elif args.func == 'txqsize':
    print args.func + " value of " + args.key + " is " + str(init.get_avg_txqueuesize(args.lc))

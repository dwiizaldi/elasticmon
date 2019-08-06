import argparse
from lib import elasticmon_python_sdk_git

result = {}
parser = argparse.ArgumentParser()

parser.add_argument('--enb', metavar='enb', action='store', type=int, required=False, default='0')
parser.add_argument('--ue', metavar='ue', action='store', type=int, required=False, default='0')
parser.add_argument('--key', metavar='key', action='store', type=str, required=True)
parser.add_argument('--func', metavar='func', action='store', type=str, required=True)
parser.add_argument('--t_start', metavar='time_start', action='store', type=str, required=False, default='7d')
parser.add_argument('--t_end', metavar='time_end', action='store', type=str, required=False, default='0s')
parser.add_argument('--dir', metavar='direction', action='store', type=str, required=False, default='dl')

args = parser.parse_args()

if args.func == 'average':
    try:
        value = elasticmon_python_sdk_git.mac_stats(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_avg()
    except:
        value = elasticmon_python_sdk_git.enb_config(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_avg()
    print args.func + " value is " + str(value)

elif args.func == 'max':
    try:
        value = elasticmon_python_sdk_git.mac_stats(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_max()
    except:
        value = elasticmon_python_sdk_git.enb_config(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_max()
    print args.func + " value is " + str(value)

elif args.func == 'min':
    try:
        value = elasticmon_python_sdk_git.mac_stats(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_min()
    except:
        value = elasticmon_python_sdk_git.enb_config(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_min()
    print args.func + " value is " + str(value)

elif args.func == 'count':
    try:
        value = elasticmon_python_sdk_git.mac_stats(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_count()
    except:
        value = elasticmon_python_sdk_git.enb_config(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_count()
    print args.func + " value is " + str(value)

elif args.func == 'sum':
    try:
        value = elasticmon_python_sdk_git.mac_stats(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_sum()
    except:
        value = elasticmon_python_sdk_git.enb_config(enb=args.enb, ue=args.ue, key=args.key, t_start=args.t_start,
                                            t_end=args.t_end, dir=args.dir).get_sum()
    print args.func + " value is " + str(value)
# cython: language_level=3, boundscheck=False, optimize.unpack_method_calls=False
from hyperopt import fmin, hp, tpe, STATUS_OK, Trials, space_eval
import os, sys, time, pprint, json, argparse, subprocess, tempfile

CONFIG = {}
TMPDIR = tempfile.gettempdir()
OS_LINUX="linux"
SEP = "/"

def array_to_str(jo,sep):
    return sep.join(str(e) for e in jo)

def add_param(cmd1,param):
    arr=cmd1.split(" ")
    arr2=[arr[0]]+arr
    arr2[1]=param
    s = array_to_str(arr2," ")
    return "\""+s+"\""

def gen_options(kv):
    jo = []
    for k, v in kv.items():
        if v in ['+','-']:
            if k == 'UseLargePages' and sys.platform[:5] == OS_LINUX:
                jo.append("-XX:+UseTransparentHugePages")
            else:
                jo.append("-XX:"+v+k)
        else:
            jo.append("-XX:"+k+"="+v)
    return jo

def change_1_settings(k, v):
    global CONFIG 
    variable = CONFIG["cmd"]
    cmd=variable.replace("KEY",k).replace("VALUE",v)
    #print(cmd)
    os.system(cmd)

def change_env(kv):
    for k, v in kv.items():
        change_1_settings(str(k), str(v))

def get_score(pid):
    fname = TMPDIR+SEP+str(pid)+".json"
    while os.path.getsize(fname) < 1:
        time.sleep(1)
    return float(read_kv_json(fname)["score"])

def start_benchmark(fname):
    pid = subprocess.Popen(['/bin/bash', '-c', "./"+fname]).pid
    open(TMPDIR+SEP+str(pid)+".json", 'w').close()
    return pid

def do_run(kv):
    global CONFIG
    cmd = CONFIG["benchmark"]
    if CONFIG["cmd"] == "join":
        opts=array_to_str(gen_options(kv),' ')
        cmd=add_param(cmd,opts)
    else:
        change_env(kv)
    score = get_score(start_benchmark(cmd))
    loss = score
    if CONFIG["score"]=="+":
        loss = -score
    ret = {'loss': loss, 'status': STATUS_OK}
    return ret

def read_key_values(path):
    if path[-4:] == ".txt":
        return read_kv_txt(path)
    elif path[-5:] == ".json":
        return read_kv_json(path)
    else:
        return None

def read_kv_json(path):
    with open(path, 'r') as f:
        jo: dict = json.load(f)
    return jo

def read_kv_txt(path):
    kv = {}
    with open(path, "rb") as f:
        for line in f:
            temp = line.split(b":")
            k = temp[0].strip(b" ")
            tv = temp[1]
            v = tv.strip(b'\r\n').lstrip(b' ')[1:-1]
            lv = v.split(b",")
            # print(k, ": " ,len(v)," ",v)
            kv[k] = lv
    return kv

def space_build(kv):
    #kv = read_key_values(f)
    space = {}
    max_evals = 0
    for k, v in kv.items():
        space[k] = hp.choice(k, v)
        max_evals += len(v)
    return space, max_evals

def opt(space, max_evals, fn):
    t = Trials()
    best = fmin(
        fn=fn,
        space=space,
        algo=tpe.suggest,
        max_evals=max_evals,
        trials=t)
    return best, t

def print_trial(tr):
    print("trials:")
    for t in tr.trials:
        k = t['misc']['vals']
        # v = space_eval(s,k)
        l: int = t['result']['loss']
        # print("v: ", v, "loss: ", l)
        print("key: ", k, "loss: ", l)
        # print(t)

def print_results(s, r):
    print("=================================")
    # print("best id:    ", R)
    # print("best value: ", space_eval(S,R))
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(space_eval(s, r))

def arg_file_exist(fname):
    if not os.path.exists(fname):
        raise argparse.ArgumentTypeError("File '%s' is not exist" % fname)
    return fname

def main():
    global CONFIG 
    parser = argparse.ArgumentParser(description='Find Best Options:')
    parser.add_argument('--config', type=arg_file_exist, default="", help='input the configuration')
    args = parser.parse_args()
    CONFIG = read_kv_json(args.config)
    space,loops = space_build(CONFIG["options"])
    best, trial = opt(space, loops, do_run)
    # print_trial(trial)
    print_results(space, best)
    os.system("rm $TMPDIR/*.json")

main()

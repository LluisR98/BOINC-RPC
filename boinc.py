'''
Original code for @maesoser in GitHub, a problem with importing StringIO libraries has been fixed. This is the full version of the code. The --output parameter prepares the code obtained from the RPC interface to an importable .txt file in node_exporter and Prometheus.
'''
from xml.etree import ElementTree
from io import StringIO
import socket
import hashlib
from tabulate import tabulate
import argparse

class RpcClient(object):

    def __init__(self):
        self.sock = -1
        self.timeout = 30
        self.addr = None

    def send_request(self, p):
        buf = \
            "<boinc_gui_rpc_request>\n"\
            "%s"\
            "</boinc_gui_rpc_request>\n\003"\
             % (p)
        try:
            self.sock.sendall(buf)
        except (socket.error, socket.herror, socket.gaierror, socket.timeout):
            raise

    def get_reply(self):
        mf = ""
        end = '\003'
        while True:
            buf = self.sock.recv(8192)
            if not buf:
                raise BoincException("ERR_READ")
            n = buf.find(end)
            if not n == -1: break
            mf += buf

        return mf + buf[:n]

    def auth(self, passwd):
        self.send_request("<auth1/>")
        reply = self.get_reply()
        nonce = reply.split("<nonce>")[1].split("</nonce>")[0]
        digest = hashlib.md5(nonce+passwd).hexdigest()
        self.send_request("<auth2><nonce_hash>" + digest + "</nonce_hash></auth2>")
        reply = self.get_reply()

    def todict(self, element_tree):
        def internal_iter(tree, accum):
            if tree is None:
                return accum
            if tree.getchildren():
                accum[tree.tag] = {}
                for each in tree.getchildren():
                    result = internal_iter(each, {})
                    if each.tag in accum[tree.tag]:
                        if not isinstance(accum[tree.tag][each.tag], list):
                            accum[tree.tag][each.tag] = [accum[tree.tag][each.tag]]
                        accum[tree.tag][each.tag].append(result[each.tag])
                    else:
                        accum[tree.tag].update(result)
            else:
                accum[tree.tag] = tree.text
            return accum
        return internal_iter(element_tree, {})

    def get_ip_addr(self, host, port):
        self.addr = socket.getaddrinfo(host or None,
                                       port or GUI_RPC_PORT,
                                       socket.AF_INET,
                                       socket.SOCK_STREAM,
                                       socket.IPPROTO_TCP)[0]
    def init(self, host, port=31416):
        self.get_ip_addr(host, port)
        socket.setdefaulttimeout(30)
        self.sock = socket.socket(*self.addr[:3])
        self.sock.connect(self.addr[-1])

    def close(self):
        if self.sock > -1:
            self.sock.close()
            self.sock = -1;

    def get_state(self):
        self.send_request("<get_state/>\n")
        reply = self.get_reply()
        return self.todict(ElementTree.fromstring(reply))['boinc_gui_rpc_reply']

class BoincException(Exception): pass

def strtime(data):
    data = int(float(data))
    if data < 120:
        return str(data) +" secs"
    else:
        data = data/60
        if data < 120:
            return str(data) +" mins"
        else:
            data = data/60
            return str(data) +" hrs"

def promexport(d):
    d = d['client_state']
    text = ""
    text += 'boinc_net_stats_bw_down{{addr=\"{0}\", hostname=\"{1}\"}} {2}\n'.format(d['host_info']['ip_addr'],d['host_info']['domain_name'], d['net_stats']['bwdown'])
    text += "boinc_net_stats_bw_up{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
        d['host_info']['ip_addr'], d['host_info']['domain_name'], d['net_stats']['bwup'])
    text += "boinc_net_stats_avg_down{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
        d['host_info']['ip_addr'], d['host_info']['domain_name'], d['net_stats']['avg_down'])
    text += "boinc_net_stats_avg_up{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
        d['host_info']['ip_addr'], d['host_info']['domain_name'], d['net_stats']['avg_up'])
    text += "boinc_net_stats_avg_time_down{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
        d['host_info']['ip_addr'], d['host_info']['domain_name'], d['net_stats']['avg_time_down'])
    text += "boinc_net_stats_avg_time_up{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
        d['host_info']['ip_addr'], d['host_info']['domain_name'], d['net_stats']['avg_time_up'])

    text += "boinc_workunits{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
        d['host_info']['ip_addr'], d['host_info']['domain_name'], len(d['workunit']))

    if isinstance(d['project'], list):
        for p in d['project']:
            text += "boinc_project_total_credit{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['host_total_credit'])
            text += "boinc_project_expavg_credit{{ addr=\"{0}\", hostname=\"{1}\",name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['host_expavg_credit'])
            text += "boinc_project_rec{{ addr=\"{0}\", hostname=\"{1}\",name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['rec'])
            text += "boinc_project_njobs_success{{ addr=\"{0}\", hostname=\"{1}\",name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['njobs_success'])
    else:
        p = d['project']
        text += "boinc_project_total_credit{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
            d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['host_total_credit'])
        text += "boinc_project_expavg_credit{{ addr=\"{0}\", hostname=\"{1}\",name=\"{2}\"}} {3}\n".format(
            d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['host_expavg_credit'])
        text += "boinc_project_rec{{ addr=\"{0}\", hostname=\"{1}\",name=\"{2}\"}} {3}\n".format(
            d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['rec'])
        text += "boinc_project_njobs_success{{ addr=\"{0}\", hostname=\"{1}\",name=\"{2}\"}} {3}\n".format(
            d['host_info']['ip_addr'], d['host_info']['domain_name'], p['project_name'], p['njobs_success'])

    text += "boinc_session_active_duration{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
      d['host_info']['ip_addr'], d['host_info']['domain_name'],
      d['time_stats']['session_active_duration'])
    text += "boinc_active_frac{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
      d['host_info']['ip_addr'], d['host_info']['domain_name'],
      d['time_stats']['active_frac'])

    text += "boinc_total_active_duration{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
      d['host_info']['ip_addr'], d['host_info']['domain_name'],
      d['time_stats']['total_active_duration'])
    text += "boinc_total_duration{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
      d['host_info']['ip_addr'], d['host_info']['domain_name'],
      d['time_stats']['total_duration'])
    text += "boinc_total_gpu_active_duration{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
      d['host_info']['ip_addr'], d['host_info']['domain_name'],
      d['time_stats']['total_gpu_active_duration'])
    text += "boinc_gpu_active_frac{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
      d['host_info']['ip_addr'], d['host_info']['domain_name'],
      d['time_stats']['gpu_active_frac'])
    text += "boinc_session_gpu_active_duration{{ addr=\"{0}\", hostname=\"{1}\"}} {2}\n".format(
      d['host_info']['ip_addr'], d['host_info']['domain_name'],
      d['time_stats']['session_gpu_active_duration'])

    for r in d['result']:
        text += "boinc_task_estimated_cpu_remaining{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['estimated_cpu_time_remaining'])
        text += "boinc_task_state{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
            d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['state'])

        if r.get('active_task') is not None:
            text += "boinc_task_fraction_done{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['active_task']['fraction_done'])
            text += "boinc_task_elapsed_time_{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['active_task']['elapsed_time'])
            text += "boinc_task_cpu_time{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['active_task']['current_cpu_time'])
            text += "boinc_task_swap_size{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['active_task']['swap_size'])
            text += "boinc_task_bytes_sent{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['active_task']['bytes_sent'])
            text += "boinc_task_bytes_recv{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['active_task']['bytes_received'])
            text += "task_set_size{{ addr=\"{0}\", hostname=\"{1}\", name=\"{2}\"}} {3}\n".format(
                d['host_info']['ip_addr'], d['host_info']['domain_name'], r['name'], r['active_task']['working_set_size'])
    return text

def get_args():
    parser = argparse.ArgumentParser(description="Tool to get information about boinc tasks")
    parser.add_argument('--nodes', required=False, help='Comma separated list of boinc nodes', default="192.168.32.101,192.168.32.102,192.168.32.103,192.168.32.104,192.168.32.105,192.168.32.106")
    parser.add_argument('--port', required=False, help='RPC Port', default="31416")
    parser.add_argument('--password', required=False, help='Password', default="admin")
    parser.add_argument('--output', required=False, help='File to export this data', default=None)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    promtext = ""
    data = []
    headers= ["NODE","ADDR","$","TASK","PCNT","ELAPSED"]
    for node in args.nodes.split(","):
        try:
            rpc = RpcClient()
            rpc.init(node, args.port)
            rpc.auth(args.password)
            state = rpc.get_state()
            if args.output != None:
                promtext += promexport(state)
            for task in state['client_state']['result']:
                if task.get('active_task') is not None:
                    if isinstance(state['client_state']['project'], list):
                        state['client_state']['project'] = state['client_state']['project'][0]
                    row = [
                        state['client_state']['host_info']['domain_name'],
                        state['client_state']['host_info']['ip_addr'],
                        state['client_state']['project']['host_total_credit'],
                        task["name"],
                        str(int(100*float(task['active_task']['fraction_done']))) + "%",
                        strtime(
                            task['active_task']['elapsed_time']) + " / " +
                            strtime(
                                float(task["estimated_cpu_time_remaining"]) +
                                float(task['active_task']["elapsed_time"])
                            )
                    ]
                    data.append(row)
            rpc.close()
        except Exception as e:
            print('Error receiving update from {0}: {1}'.format(node,e))
    if args.output != None:
        try:
            f = open(args.output, "w")
            f.write(promtext)
            f.close()
        except:
            print("Error saving statistics to file {0}".format(args.output))
    print(tabulate(data, headers=headers))
    print("\n{0} tasks".format(len(data)))

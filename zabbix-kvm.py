#!/usr/bin/python
from optparse import OptionParser
from xml.etree import ElementTree
import libvirt
import json
import time


def main():
    options = parse_args()
    if options.item == "discovery":
        uuid_list(options)
    elif options.item == "cpu":
        cpu(options)
    elif options.item == "mem":
        mem(options)
    elif options.item == "net_out":
        net_out(options)
    elif options.item == "net_in":
        net_in(options)
    elif options.item == "rd_bytes":
        rd_bytes(options)
    elif options.item == "wr_bytes":
        wr_bytes(options)
    elif options.item == "network":
        network(options)


def parse_args():
    parser = OptionParser()
    parser.add_option("", "--item", dest="item", help="", action="store", type="string", default=None)
    parser.add_option("", "--uuid", dest="uuid", help="", action="store", type="string", default=None)
    parser.add_option("", "--net", dest="net", help="", action="store", type="string", default=None)
    (options, args) = parser.parse_args()
    if not options.item:
        options.item = "discovery"
    return options


def kvm_connect():
    try:
        conn = libvirt.openReadOnly('qemu:///system')
        return conn
    except:
        exit(1)


def uuid_list(options):
    conn = kvm_connect()
    r = {"data": []}
    try:
        conn.listAllDomains(0)
    except:
        for dom_id in conn.listDomainsID():
            r['data'].append({"{#DOMAINUUID}": conn.lookupByID(dom_id).UUIDString()})
    else:
        for domain in conn.listAllDomains(0):
            r["data"].append({"{#DOMAINUUID}": domain.UUIDString()})
    conn.close()
    print json.dumps(r)


def cpu(options):
    conn = kvm_connect()
    dom = conn.lookupByUUIDString(options.uuid)
    t1 = time.time()
    c1 = int(dom.info()[4])
    time.sleep(1)
    t2 = time.time()
    c2 = int(dom.info()[4])
    c_nums = int(dom.info()[3])
    usage = (c2 - c1) * 100 / ((t2 - t1) * c_nums * 1e9)
    conn.close()
    print float(usage)


def mem(options):
    conn = kvm_connect()
    host = conn.lookupByUUIDString(options.uuid)
    meminfo = host.memoryStats()
    free_mem = float(meminfo['unused'])
    total_mem = float(meminfo['available'])
    util_mem = ((total_mem - free_mem) / total_mem) * 100
    conn.close()
    print float(util_mem)


def net_out(options):
    conn = kvm_connect()
    host = conn.lookupByUUIDString(options.uuid)
    # location = host.XMLDesc().find("<target dev=\'tap")
    tree = ElementTree.fromstring(host.XMLDesc())
    for tmp_net in tree.findall('devices/interface/target'):
        net_dev = tmp_net.get('dev')
        if options.net == net_dev:
            network_info1 = host.interfaceStats(net_dev)
            net_read_bytes1 = network_info1[0]
            # tapname = host.XMLDesc()[location + 13:location + 27]
            time.sleep(1)
            network_info2 = host.interfaceStats(net_dev)
            net_read_bytes2 = network_info2[0]
            print net_read_bytes2 - net_read_bytes1
            conn.close()
            return
    conn.close()
    print 0


def net_in(options):
    conn = kvm_connect()
    host = conn.lookupByUUIDString(options.uuid)
    # location = host.XMLDesc().find("<target dev=\'tap")
    tree = ElementTree.fromstring(host.XMLDesc())
    for tmp_net in tree.findall('devices/interface/target'):
        net_dev = tmp_net.get('dev')
        if options.net == net_dev:
            network_info1 = host.interfaceStats(net_dev)
            net_read_bytes1 = network_info1[4]
            # tapname = host.XMLDesc()[location + 13:location + 27]
            time.sleep(1)
            network_info2 = host.interfaceStats(net_dev)
            net_read_bytes2 = network_info2[4]
            print net_read_bytes2 - net_read_bytes1
            conn.close()
            return
    conn.close()
    print 0


def rd_bytes(options):
    conn = kvm_connect()
    host = conn.lookupByUUIDString(options.uuid)
    r1 = host.blockStatsFlags("vda")['rd_bytes']
    time.sleep(1)
    r2 = host.blockStatsFlags("vda")['rd_bytes']
    conn.close()
    print r2 - r1


def wr_bytes(options):
    conn = kvm_connect()
    host = conn.lookupByUUIDString(options.uuid)
    r1 = host.blockStatsFlags("vda")['wr_bytes']
    time.sleep(1)
    r2 = host.blockStatsFlags("vda")['wr_bytes']
    conn.close()
    print r2 - r1


def network(options):
    r = {"data": []}
    conn = kvm_connect()
    host = conn.lookupByUUIDString(options.uuid)
    tree = ElementTree.fromstring(host.XMLDesc())
    for tmp_net in tree.findall('devices/interface/target'):
        net_dev = tmp_net.get('dev')
        r["data"].append({"{#VS_NAME}": options.uuid, "{#VS_NIC}": net_dev})
    conn.close()
    print json.dumps(r)


if __name__ == "__main__":
    main()

from __future__ import absolute_import
from __future__ import print_function
import sys
import resource
#import sys
import xml.dom.minidom
#from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
import usage
import utils
import re
import glob
import os

def stonith_cmd(argv):
    if len(argv) == 0:
        argv = ["show"]

    sub_cmd = argv.pop(0)
    if (sub_cmd == "help"):
        usage.stonith(argv)
    elif (sub_cmd == "list"):
        stonith_list_available(argv)
    elif (sub_cmd == "describe"):
        if len(argv) == 1:
            stonith_list_options(argv[0])
        else:
            usage.stonith()
            sys.exit(1)
    elif (sub_cmd == "create"):
        if len(argv) < 2:
            usage.stonith()
            sys.exit(1)
        stn_id = argv.pop(0)
        stn_type = "stonith:"+argv.pop(0)
        st_values, op_values, meta_values = resource.parse_resource_options(
            argv, with_clone=False
        )
        resource.resource_create(stn_id, stn_type, st_values, op_values, meta_values)
    elif (sub_cmd == "update"):
        stn_id = argv.pop(0)
        resource.resource_update(stn_id,argv)
    elif (sub_cmd == "delete"):
        if len(argv) == 1:
            stn_id = argv.pop(0)
            utils.replace_cib_configuration(
                stonith_level_rm_device(utils.get_cib_dom(), stn_id)
            )
            resource.resource_remove(stn_id)
        else:
            usage.stonith(["delete"])
            sys.exit(1)
    elif (sub_cmd == "show"):
        resource.resource_show(argv, True)
        stonith_level([])
    elif (sub_cmd == "level"):
        stonith_level(argv)
    elif (sub_cmd == "fence"):
        stonith_fence(argv)
    elif (sub_cmd == "cleanup"):
        if len(argv) == 0:
            resource.resource_cleanup_all()
        else:
            res_id = argv.pop(0)
            resource.resource_cleanup(res_id)
    elif (sub_cmd == "confirm"):
        stonith_confirm(argv)
    else:
        usage.stonith()
        sys.exit(1)

def stonith_list_available(argv):
    if len(argv) != 0:
        filter_string = argv[0]
    else:
        filter_string = ""

    bad_fence_devices = ["kdump_send", "legacy", "na", "nss_wrapper",
            "pcmk", "vmware_helper", "ack_manual", "virtd", "sanlockd",
            "check", "tool", "node"]
    fence_devices = sorted(glob.glob(utils.fence_bin + "fence_*"))
    for bfd in bad_fence_devices:
        try:
            fence_devices.remove(utils.fence_bin + "fence_"+bfd)
        except ValueError:
            continue

    if not fence_devices:
        utils.err(
            "No stonith agents available. Do you have fence agents installed?"
        )
    fence_devices_filtered = [fd for fd in fence_devices if filter_string in fd]
    if not fence_devices_filtered:
        utils.err("No stonith agents matching the filter.")

    for fd in fence_devices_filtered:
        sd = ""
        fd_name = fd[10:]
        if not "--nodesc" in utils.pcs_options:
            metadata = utils.get_stonith_metadata(fd)
            if metadata == False:
                print("Error: no metadata for %s" % fd, file=sys.stderr)
                continue
            try:
                dom = parseString(metadata)
            except Exception:
                print("Error: unable to parse metadata for fence agent: %s" % (fd_name), file=sys.stderr)
                continue
            ra = dom.documentElement
            shortdesc = ra.getAttribute("shortdesc")

            if len(shortdesc) > 0:
                sd = " - " +  resource.format_desc(fd_name.__len__() + 3, shortdesc)
        print(fd_name + sd)

def stonith_list_options(stonith_agent):
    metadata = utils.get_stonith_metadata(utils.fence_bin + stonith_agent)
    if not metadata:
        utils.err("unable to get metadata for %s" % stonith_agent)
    try:
        dom = parseString(metadata)
    except xml.parsers.expat.ExpatError as e:
        utils.err("Unable to parse xml for '%s': %s" % (stonith_agent, e))

    title = dom.documentElement.getAttribute("name") or stonith_agent
    short_desc = dom.documentElement.getAttribute("shortdesc")
    if not short_desc:
        for sd in dom.documentElement.getElementsByTagName("shortdesc"):
            if sd.parentNode.tagName == "resource-agent" and sd.firstChild:
                short_desc = sd.firstChild.data.strip()
                break
    long_desc = ""
    for ld in dom.documentElement.getElementsByTagName("longdesc"):
        if ld.parentNode.tagName == "resource-agent" and ld.firstChild:
            long_desc = ld.firstChild.data.strip()
            break

    if short_desc:
        title += " - " + resource.format_desc(len(title + " - "), short_desc)
    print(title)
    print()
    if long_desc:
        print(long_desc)
        print()
    print("Stonith options:")

    params = dom.documentElement.getElementsByTagName("parameter")
    for param in params:
        name = param.getAttribute("name")
        if param.getAttribute("required") == "1":
            name += " (required)"
        desc = ""
        shortdesc_els = param.getElementsByTagName("shortdesc")
        if shortdesc_els and shortdesc_els[0].firstChild:
            desc = shortdesc_els[0].firstChild.nodeValue.strip().replace("\n", " ")
        if not desc:
            desc = "No description available"
        indent = name.__len__() + 4
        desc = resource.format_desc(indent, desc)
        print("  " + name + ": " + desc)

    default_stonith_options = utils.get_default_stonith_options()
    for do in default_stonith_options:
        name = do.attrib["name"]
        desc = ""
        if len(do.findall("shortdesc")) > 0:
            if do.findall("shortdesc")[0].text:
                desc = do.findall("shortdesc")[0].text.strip()
        if not desc:
            desc = "No description available"
        indent = len(name) + 4
        desc = resource.format_desc(indent, desc)
        print("  " + name + ": " + desc)

def stonith_level(argv):
    if len(argv) == 0:
        stonith_level_show()
        return

    subcmd = argv.pop(0)

    if subcmd == "add":
        if len(argv) < 3:
            usage.stonith(["level add"])
            sys.exit(1)
        stonith_level_add(argv[0], argv[1], ",".join(argv[2:]))
    elif subcmd in ["remove","delete"]:
        if len(argv) < 1:
            usage.stonith(["level remove"])
            sys.exit(1)
        
        node = ""
        devices = ""
        if len(argv) == 2:
            node = argv[1]
        elif len(argv) > 2:
            node = argv[1]
            devices = ",".join(argv[2:])

        stonith_level_rm(argv[0], node, devices)
    elif subcmd == "clear":
        if len(argv) == 0:
            stonith_level_clear()
        else:
            stonith_level_clear(argv[0])
    elif subcmd == "verify":
        stonith_level_verify()
    else:
        print("pcs stonith level: invalid option -- '%s'" % subcmd)
        usage.stonith(["level"])
        sys.exit(1)

def stonith_level_add(level, node, devices):
    dom = utils.get_cib_dom()

    if not re.search(r'^\d+$', level) or re.search(r'^0+$', level):
        utils.err("invalid level '{0}', use a positive integer".format(level))
    level = level.lstrip('0')
    if not "--force" in utils.pcs_options:
        for dev in devices.split(","):
            if not utils.is_stonith_resource(dev):
                utils.err("%s is not a stonith id (use --force to override)" % dev)
        if not utils.is_pacemaker_node(node) and not utils.is_corosync_node(node):
            utils.err("%s is not currently a node (use --force to override)" % node)

    ft = dom.getElementsByTagName("fencing-topology")
    if len(ft) == 0:
        conf = dom.getElementsByTagName("configuration")[0]
        ft = dom.createElement("fencing-topology")
        conf.appendChild(ft)
    else:
        ft = ft[0]

    fls = ft.getElementsByTagName("fencing-level")
    for fl in fls:
        if fl.getAttribute("target") == node and fl.getAttribute("index") == level and fl.getAttribute("devices") == devices:
            utils.err("unable to add fencing level, fencing level for node: %s, at level: %s, with device: %s already exists" % (node,level,devices))

    new_fl = dom.createElement("fencing-level")
    ft.appendChild(new_fl)
    new_fl.setAttribute("target", node)
    new_fl.setAttribute("index", level)
    new_fl.setAttribute("devices", devices)
    new_fl.setAttribute("id", utils.find_unique_id(dom, "fl-" + node +"-" + level))

    utils.replace_cib_configuration(dom)

def stonith_level_rm(level, node, devices):
    dom = utils.get_cib_dom()

    if devices != "":
        node_devices_combo  = node + "," + devices
    else:
        node_devices_combo = node

    ft = dom.getElementsByTagName("fencing-topology")
    if len(ft) == 0:
        utils.err("unable to remove fencing level, fencing level for node: %s, at level: %s, with device: %s doesn't exist" % (node,level,devices))
    else:
        ft = ft[0]

    fls = ft.getElementsByTagName("fencing-level")
    fls_to_remove = []

    if node != "":
        if devices != "":
            found = False
            for fl in fls:
                if fl.getAttribute("target") == node and fl.getAttribute("index") == level and fl.getAttribute("devices") == devices:
                    found = True
                    break

                if fl.getAttribute("index") == level and fl.getAttribute("devices") == node_devices_combo:
                    found = True
                    break

            if found == False:
                utils.err("unable to remove fencing level, fencing level for node: %s, at level: %s, with device: %s doesn't exist" % (node,level,devices))

            fl.parentNode.removeChild(fl)
        else:
            for fl in fls:
                if fl.getAttribute("index") == level and (fl.getAttribute("target") == node or fl.getAttribute("devices") == node):
                    fl.parentNode.removeChild(fl)
    else:
        for fl in fls:
            if fl.getAttribute("index") == level:
                parent = fl.parentNode
                parent.removeChild(fl)
                if len(parent.getElementsByTagName("fencing-level")) == 0:
                    parent.parentNode.removeChild(parent)
                    break

    utils.replace_cib_configuration(dom)

def stonith_level_rm_device(cib_dom, stn_id):
    topology_el_list = cib_dom.getElementsByTagName("fencing-topology")
    if not topology_el_list:
        return cib_dom
    topology_el = topology_el_list[0]
    for level_el in topology_el.getElementsByTagName("fencing-level"):
        device_list = level_el.getAttribute("devices").split(",")
        if stn_id in device_list:
            new_device_list = [dev for dev in device_list if dev != stn_id]
            if new_device_list:
                level_el.setAttribute("devices", ",".join(new_device_list))
            else:
                level_el.parentNode.removeChild(level_el)
    if not topology_el.getElementsByTagName("fencing-level"):
        topology_el.parentNode.removeChild(topology_el)
    return cib_dom

def stonith_level_clear(node = None):
    dom = utils.get_cib_dom()
    ft = dom.getElementsByTagName("fencing-topology")

    if len(ft) == 0:
        return

    if node == None:
        ft = ft[0]
        childNodes = ft.childNodes[:]
        for node in childNodes:
            node.parentNode.removeChild(node)
    else:
        fls = dom.getElementsByTagName("fencing-level")
        if len(fls) == 0:
            return
        for fl in fls:
            if fl.getAttribute("target") == node or fl.getAttribute("devices") == node:
                fl.parentNode.removeChild(fl)

    utils.replace_cib_configuration(dom)

def stonith_level_verify():
    dom = utils.get_cib_dom()

    fls = dom.getElementsByTagName("fencing-level")
    for fl in fls:
        node = fl.getAttribute("target")
        level = fl.getAttribute("index")
        devices = fl.getAttribute("devices")
        for dev in devices.split(","):
            if not utils.is_stonith_resource(dev):
                utils.err("%s is not a stonith id" % dev)
        if not utils.is_corosync_node(node) and not utils.is_pacemaker_node(node):
            utils.err("%s is not currently a node" % node)

def stonith_level_show():
    dom = utils.get_cib_dom()

    node_levels = {}
    fls = dom.getElementsByTagName("fencing-level")
    for fl in fls:
        node = fl.getAttribute("target")
        level = fl.getAttribute("index")
        devices = fl.getAttribute("devices")

        if node in node_levels:
            node_levels[node].append((level,devices))
        else:
            node_levels[node] = [(level,devices)]

    if len(list(node_levels.keys())) == 0:
        return

    nodes = list(node_levels.keys())
    nodes.sort()

    for node in nodes:
        print(" Node: " + node)
        for level in sorted(node_levels[node], key=lambda x: int(x[0])):
            print("  Level " + level[0] + " - " + level[1])


def stonith_fence(argv):
    if len(argv) != 1:
        utils.err("must specify one (and only one) node to fence")

    node = argv.pop(0)
    if "--off" in utils.pcs_options:
        args = ["stonith_admin", "-F", node]
    else:
        args = ["stonith_admin", "-B", node]
    output, retval = utils.run(args)

    if retval != 0:
        utils.err("unable to fence '%s'\n" % node + output)
    else:
        print("Node: %s fenced" % node)

def stonith_confirm(argv):
    if len(argv) != 1:
        utils.err("must specify one (and only one) node to confirm fenced")

    node = argv.pop(0)
    args = ["stonith_admin", "-C", node]
    output, retval = utils.run(args)

    if retval != 0:
        utils.err("unable to confirm fencing of node '%s'\n" % node + output)
    else:
        print("Node: %s confirmed fenced" % node)

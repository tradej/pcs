from __future__ import absolute_import
import os
import sys
import shutil
import unittest
import xml.dom.minidom
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pcs_test_functions import pcs, ac
import utils

empty_cib = os.path.join(currentdir, "empty.xml")
temp_cib = os.path.join(currentdir, "temp.xml")

class UtilsTest(unittest.TestCase):

    def get_cib_empty(self):
        return xml.dom.minidom.parse(empty_cib)

    def get_cib_resources(self):
        cib_dom = self.get_cib_empty()
        new_resources = xml.dom.minidom.parseString("""
            <resources>
                  <primitive id="myResource"
                        class="ocf" provider="heartbeat" type="Dummy">
                  </primitive>
                  <clone id="myClone">
                      <primitive id="myClonedResource"
                          class="ocf" provider="heartbeat" type="Dummy">
                      </primitive>
                  </clone>
                  <master id="myMaster">
                      <primitive id="myMasteredResource"
                            class="ocf" provider="heartbeat" type="Dummy">
                      </primitive>
                  </master>
                  <group id="myGroup">
                      <primitive id="myGroupedResource"
                            class="ocf" provider="heartbeat" type="Dummy">
                      </primitive>
                  </group>
                  <clone id="myGroupClone">
                      <group id="myClonedGroup">
                          <primitive id="myClonedGroupedResource"
                                class="ocf" provider="heartbeat" type="Dummy">
                          </primitive>
                      </group>
                  </clone>
                  <master id="myGroupMaster">
                      <group id="myMasteredGroup">
                          <primitive id="myMasteredGroupedResource"
                                class="ocf" provider="heartbeat" type="Dummy">
                          </primitive>
                      </group>
                  </master>
            </resources>
        """).documentElement
        resources = cib_dom.getElementsByTagName("resources")[0]
        resources.parentNode.replaceChild(new_resources, resources)
        return cib_dom

    def testDomGetResources(self):
        def test_dom_get(method, dom, ok_ids, bad_ids):
            for element_id in ok_ids:
                self.assert_element_id(method(dom, element_id), element_id)
            for element_id in bad_ids:
                self.assertFalse(method(dom, element_id))

        cib_dom = self.get_cib_empty()
        self.assertFalse(utils.dom_get_resource(cib_dom, "myResource"))
        self.assertFalse(
            utils.dom_get_resource_clone(cib_dom, "myClonedResource")
        )
        self.assertFalse(
            utils.dom_get_resource_masterslave(cib_dom, "myMasteredResource")
        )
        self.assertFalse(utils.dom_get_group(cib_dom, "myGroup"))
        self.assertFalse(utils.dom_get_group_clone(cib_dom, "myClonedGroup"))
        self.assertFalse(
            utils.dom_get_group_masterslave(cib_dom, "myMasteredGroup")
        )
        self.assertFalse(utils.dom_get_clone(cib_dom, "myClone"))
        self.assertFalse(utils.dom_get_master(cib_dom, "myMaster"))
        self.assertFalse(utils.dom_get_clone_ms_resource(cib_dom, "myClone"))
        self.assertFalse(utils.dom_get_clone_ms_resource(cib_dom, "myMaster"))
        self.assertFalse(
            utils.dom_get_resource_clone_ms_parent(cib_dom, "myClonedResource")
        )
        self.assertFalse(
            utils.dom_get_resource_clone_ms_parent(cib_dom, "myMasteredResource")
        )

        cib_dom = self.get_cib_resources()
        all_ids = set([
            "none", "myResource",
            "myClone", "myClonedResource",
            "myMaster", "myMasteredResource",
            "myGroup", "myGroupedResource",
            "myGroupClone", "myClonedGroup", "myClonedGroupedResource",
            "myGroupMaster", "myMasteredGroup", "myMasteredGroupedResource",
        ])

        resource_ids = set([
            "myResource",
            "myClonedResource", "myGroupedResource", "myMasteredResource",
            "myClonedGroupedResource", "myMasteredGroupedResource"
        ])
        test_dom_get(
            utils.dom_get_resource, cib_dom,
            resource_ids, all_ids - resource_ids
        )

        cloned_ids = set(["myClonedResource", "myClonedGroupedResource"])
        test_dom_get(
            utils.dom_get_resource_clone, cib_dom,
            cloned_ids, all_ids - cloned_ids
        )

        mastered_ids = set(["myMasteredResource", "myMasteredGroupedResource"])
        test_dom_get(
            utils.dom_get_resource_masterslave, cib_dom,
            mastered_ids, all_ids - mastered_ids
        )

        group_ids = set(["myGroup", "myClonedGroup", "myMasteredGroup"])
        test_dom_get(
            utils.dom_get_group, cib_dom, group_ids, all_ids - group_ids
        )

        cloned_group_ids = set(["myClonedGroup"])
        test_dom_get(
            utils.dom_get_group_clone, cib_dom,
            cloned_group_ids, all_ids - cloned_group_ids
        )

        clone_ids = set(["myClone", "myGroupClone"])
        test_dom_get(
            utils.dom_get_clone, cib_dom,
            clone_ids, all_ids - clone_ids
        )

        mastered_group_ids = set(["myMasteredGroup"])
        test_dom_get(
            utils.dom_get_group_masterslave, cib_dom,
            mastered_group_ids, all_ids - mastered_group_ids
        )

        master_ids = set(["myMaster", "myGroupMaster"])
        test_dom_get(
            utils.dom_get_master, cib_dom,
            master_ids, all_ids - master_ids
        )


        self.assert_element_id(
            utils.dom_get_clone_ms_resource(cib_dom, "myClone"),
            "myClonedResource"
        )
        self.assert_element_id(
            utils.dom_get_clone_ms_resource(cib_dom, "myGroupClone"),
            "myClonedGroup"
        )
        self.assert_element_id(
            utils.dom_get_clone_ms_resource(cib_dom, "myMaster"),
            "myMasteredResource"
        )
        self.assert_element_id(
            utils.dom_get_clone_ms_resource(cib_dom, "myGroupMaster"),
            "myMasteredGroup"
        )

        self.assert_element_id(
            utils.dom_get_resource_clone_ms_parent(cib_dom, "myClonedResource"),
            "myClone"
        )
        self.assert_element_id(
            utils.dom_get_resource_clone_ms_parent(cib_dom, "myClonedGroup"),
            "myGroupClone"
        )
        self.assert_element_id(
            utils.dom_get_resource_clone_ms_parent(
                cib_dom, "myClonedGroupedResource"
            ),
            "myGroupClone"
        )
        self.assert_element_id(
            utils.dom_get_resource_clone_ms_parent(
                cib_dom, "myMasteredResource"
            ),
            "myMaster"
        )
        self.assert_element_id(
            utils.dom_get_resource_clone_ms_parent(
                cib_dom, "myMasteredGroup"
            ),
            "myGroupMaster"
        )
        self.assert_element_id(
            utils.dom_get_resource_clone_ms_parent(
                cib_dom, "myMasteredGroupedResource"
            ),
            "myGroupMaster"
        )
        self.assertEqual(
            None,
            utils.dom_get_resource_clone_ms_parent(cib_dom, "myResource")
        )
        self.assertEqual(
            None,
            utils.dom_get_resource_clone_ms_parent(cib_dom, "myGroup")
        )
        self.assertEqual(
            None,
            utils.dom_get_resource_clone_ms_parent(cib_dom, "myGroupedResource")
        )

    def testDomGetResourceRemoteNodeName(self):
        dom = self.get_cib_empty()
        new_resources = xml.dom.minidom.parseString("""
            <resources>
                <primitive id="dummy1"
                        class="ocf" provider="heartbeat" type="Dummy">
                </primitive>
                <primitive class="ocf" id="vm-guest1" provider="heartbeat"
                        type="VirtualDomain">
                    <instance_attributes id="vm-guest1-instance_attributes">
                        <nvpair id="vm-guest1-instance_attributes-hypervisor"
                            name="hypervisor" value="qemu:///system"/>
                        <nvpair id="vm-guest1-instance_attributes-config"
                            name="config" value="/root/guest1.xml"/>
                    </instance_attributes>
                    <meta_attributes id="vm-guest1-meta_attributes">
                        <nvpair id="vm-guest1-meta_attributes-remote-node"
                            name="remote-node" value="guest1"/>
                    </meta_attributes>
                </primitive>
                <primitive id="dummy2"
                        class="ocf" provider="heartbeat" type="Dummy">
                    <instance_attributes id="vm-guest1-meta_attributes">
                        <nvpair id="dummy2-remote-node"
                            name="remote-node" value="guest2"/>
                    </instance_attributes>
                </primitive>
            </resources>
        """).documentElement
        resources = dom.getElementsByTagName("resources")[0]
        resources.parentNode.replaceChild(new_resources, resources)

        self.assertEqual(
            None,
            utils.dom_get_resource_remote_node_name(
                utils.dom_get_resource(dom, "dummy1")
            )
        )
        self.assertEqual(
            None,
            utils.dom_get_resource_remote_node_name(
                utils.dom_get_resource(dom, "dummy2")
            )
        )
        self.assertEqual(
            "guest1",
            utils.dom_get_resource_remote_node_name(
                utils.dom_get_resource(dom, "vm-guest1")
            )
        )

    def test_dom_get_meta_attr_value(self):
        dom = self.get_cib_empty()
        new_resources = xml.dom.minidom.parseString("""
            <resources>
                <primitive id="dummy1"
                        class="ocf" provider="heartbeat" type="Dummy">
                </primitive>
                <primitive class="ocf" id="vm-guest1" provider="heartbeat"
                        type="VirtualDomain">
                    <instance_attributes id="vm-guest1-instance_attributes">
                        <nvpair id="vm-guest1-instance_attributes-hypervisor"
                            name="hypervisor" value="qemu:///system"/>
                        <nvpair id="vm-guest1-instance_attributes-config"
                            name="config" value="/root/guest1.xml"/>
                    </instance_attributes>
                    <meta_attributes id="vm-guest1-meta_attributes">
                        <nvpair id="vm-guest1-meta_attributes-remote-node"
                            name="remote-node" value="guest1"/>
                    </meta_attributes>
                </primitive>
                <primitive id="dummy2"
                        class="ocf" provider="heartbeat" type="Dummy">
                    <instance_attributes id="vm-guest1-meta_attributes">
                        <nvpair id="dummy2-remote-node"
                            name="remote-node" value="guest2"/>
                    </instance_attributes>
                </primitive>
            </resources>
        """).documentElement
        resources = dom.getElementsByTagName("resources")[0]
        resources.parentNode.replaceChild(new_resources, resources)

        self.assertEqual(
            None,
            utils.dom_get_meta_attr_value(
                utils.dom_get_resource(dom, "dummy1"), "foo"
            )
        )
        self.assertEqual(
            None,
            utils.dom_get_meta_attr_value(
                utils.dom_get_resource(dom, "dummy2"), "remote-node"
            )
        )
        self.assertEqual(
            "guest1",
            utils.dom_get_meta_attr_value(
                utils.dom_get_resource(dom, "vm-guest1"), "remote-node"
            )
        )
        self.assertEqual(
            None,
            utils.dom_get_meta_attr_value(
                utils.dom_get_resource(dom, "vm-guest1"), "foo"
            )
        )

    def testGetElementWithId(self):
        dom = xml.dom.minidom.parseString("""
            <aa>
                <bb id="bb1"/>
                <bb/>
                <bb id="bb2">
                    <cc id="cc1"/>
                </bb>
                <bb id="bb3">
                    <cc id="cc2"/>
                </bb>
            </aa>
        """).documentElement

        self.assert_element_id(
            utils.dom_get_element_with_id(dom, "bb", "bb1"), "bb1"
        )
        self.assert_element_id(
            utils.dom_get_element_with_id(dom, "bb", "bb2"), "bb2"
        )
        self.assert_element_id(
            utils.dom_get_element_with_id(dom, "cc", "cc1"), "cc1"
        )
        self.assert_element_id(
            utils.dom_get_element_with_id(
                utils.dom_get_element_with_id(dom, "bb", "bb2"),
                "cc",
                "cc1"
            ),
            "cc1"
        )
        self.assertEqual(None, utils.dom_get_element_with_id(dom, "dd", "bb1"))
        self.assertEqual(None, utils.dom_get_element_with_id(dom, "bb", "bb4"))
        self.assertEqual(None, utils.dom_get_element_with_id(dom, "bb", "cc1"))
        self.assertEqual(
            None,
            utils.dom_get_element_with_id(
                utils.dom_get_element_with_id(dom, "bb", "bb2"),
                "cc",
                "cc2"
            )
        )

    def test_dom_get_parent_by_tag_name(self):
        dom = xml.dom.minidom.parseString("""
            <aa id="aa1">
                <bb id="bb1"/>
                <bb id="bb2">
                    <cc id="cc1"/>
                </bb>
                <bb id="bb3">
                    <cc id="cc2"/>
                </bb>
                <dd id="dd1" />
            </aa>
        """).documentElement
        bb1 = utils.dom_get_element_with_id(dom, "bb", "bb1")
        cc1 = utils.dom_get_element_with_id(dom, "cc", "cc1")

        self.assert_element_id(
            utils.dom_get_parent_by_tag_name(bb1, "aa"),
            "aa1"
        )
        self.assert_element_id(
            utils.dom_get_parent_by_tag_name(cc1, "aa"),
            "aa1"
        )
        self.assert_element_id(
            utils.dom_get_parent_by_tag_name(cc1, "bb"),
            "bb2"
        )

        self.assertEqual(None, utils.dom_get_parent_by_tag_name(bb1, "cc"))
        self.assertEqual(None, utils.dom_get_parent_by_tag_name(cc1, "dd"))
        self.assertEqual(None, utils.dom_get_parent_by_tag_name(cc1, "ee"))

    def testValidateConstraintResource(self):
        dom = self.get_cib_resources()
        self.assertEqual(
            (True, "", "myClone"),
            utils.validate_constraint_resource(dom, "myClone")
        )
        self.assertEqual(
            (True, "", "myGroupClone"),
            utils.validate_constraint_resource(dom, "myGroupClone")
        )
        self.assertEqual(
            (True, "", "myMaster"),
            utils.validate_constraint_resource(dom, "myMaster")
        )
        self.assertEqual(
            (True, "", "myGroupMaster"),
            utils.validate_constraint_resource(dom, "myGroupMaster")
        )
        self.assertEqual(
            (True, "", "myResource"),
            utils.validate_constraint_resource(dom, "myResource")
        )
        self.assertEqual(
            (True, "", "myGroup"),
            utils.validate_constraint_resource(dom, "myGroup")
        )
        self.assertEqual(
            (True, "", "myGroupedResource"),
            utils.validate_constraint_resource(dom, "myGroupedResource")
        )

        self.assertEqual(
            (False, "Resource 'myNonexistent' does not exist", None),
            utils.validate_constraint_resource(dom, "myNonexistent")
        )

        message = (
            "%s is a clone resource, you should use the clone id: "
            "%s when adding constraints. Use --force to override."
        )
        self.assertEqual(
            (
                False,
                message % ("myClonedResource", "myClone"),
                "myClone"
            ),
            utils.validate_constraint_resource(dom, "myClonedResource")
        )
        self.assertEqual(
            (
                False,
                message % ("myClonedGroup", "myGroupClone"),
                "myGroupClone"
            ),
            utils.validate_constraint_resource(dom, "myClonedGroup")
        )
        self.assertEqual(
            (
                False,
                message % ("myClonedGroupedResource", "myGroupClone"),
                "myGroupClone"
            ),
            utils.validate_constraint_resource(dom, "myClonedGroupedResource")
        )

        message = (
            "%s is a master/slave resource, you should use the master id: "
            "%s when adding constraints. Use --force to override."
        )
        self.assertEqual(
            (
                False,
                message % ("myMasteredResource", "myMaster"),
                "myMaster"
            ),
            utils.validate_constraint_resource(dom, "myMasteredResource")
        )
        self.assertEqual(
            (
                False,
                message % ("myMasteredGroup", "myGroupMaster"),
                "myGroupMaster"
            ),
            utils.validate_constraint_resource(dom, "myMasteredGroup")
        )
        self.assertEqual(
            (
                False,
                message % ("myMasteredGroupedResource", "myGroupMaster"),
                "myGroupMaster"
            ),
            utils.validate_constraint_resource(dom, "myMasteredGroupedResource")
        )

        utils.pcs_options["--force"] = True
        self.assertEqual(
            (True, "", "myClone"),
            utils.validate_constraint_resource(dom, "myClonedResource")
        )
        self.assertEqual(
            (True, "", "myGroupClone"),
            utils.validate_constraint_resource(dom, "myClonedGroup")
        )
        self.assertEqual(
            (True, "", "myGroupClone"),
            utils.validate_constraint_resource(dom, "myClonedGroupedResource")
        )
        self.assertEqual(
            (True, "", "myMaster"),
            utils.validate_constraint_resource(dom, "myMasteredResource")
        )
        self.assertEqual(
            (True, "", "myGroupMaster"),
            utils.validate_constraint_resource(dom, "myMasteredGroup")
        )
        self.assertEqual(
            (True, "", "myGroupMaster"),
            utils.validate_constraint_resource(dom, "myMasteredGroupedResource")
        )

    def testValidateXmlId(self):
        self.assertEqual((True, ""), utils.validate_xml_id("dummy"))
        self.assertEqual((True, ""), utils.validate_xml_id("DUMMY"))
        self.assertEqual((True, ""), utils.validate_xml_id("dUmMy"))
        self.assertEqual((True, ""), utils.validate_xml_id("dummy0"))
        self.assertEqual((True, ""), utils.validate_xml_id("dum0my"))
        self.assertEqual((True, ""), utils.validate_xml_id("dummy-"))
        self.assertEqual((True, ""), utils.validate_xml_id("dum-my"))
        self.assertEqual((True, ""), utils.validate_xml_id("dummy."))
        self.assertEqual((True, ""), utils.validate_xml_id("dum.my"))
        self.assertEqual((True, ""), utils.validate_xml_id("_dummy"))
        self.assertEqual((True, ""), utils.validate_xml_id("dummy_"))
        self.assertEqual((True, ""), utils.validate_xml_id("dum_my"))

        self.assertEqual(
            (False, "test id cannot be empty"),
            utils.validate_xml_id("", "test id")
        )

        msg = "invalid test id '%s', '%s' is not a valid first character for a test id"
        self.assertEqual(
            (False, msg % ("0", "0")),
            utils.validate_xml_id("0", "test id")
        )
        self.assertEqual(
            (False, msg % ("-", "-")),
            utils.validate_xml_id("-", "test id")
        )
        self.assertEqual(
            (False, msg % (".", ".")),
            utils.validate_xml_id(".", "test id")
        )
        self.assertEqual(
            (False, msg % (":", ":")),
            utils.validate_xml_id(":", "test id")
        )
        self.assertEqual(
            (False, msg % ("0dummy", "0")),
            utils.validate_xml_id("0dummy", "test id")
        )
        self.assertEqual(
            (False, msg % ("-dummy", "-")),
            utils.validate_xml_id("-dummy", "test id")
        )
        self.assertEqual(
            (False, msg % (".dummy", ".")),
            utils.validate_xml_id(".dummy", "test id")
        )
        self.assertEqual(
            (False, msg % (":dummy", ":")),
            utils.validate_xml_id(":dummy", "test id")
        )

        msg = "invalid test id '%s', '%s' is not a valid character for a test id"
        self.assertEqual(
            (False, msg % ("dum:my", ":")),
            utils.validate_xml_id("dum:my", "test id")
        )
        self.assertEqual(
            (False, msg % ("dummy:", ":")),
            utils.validate_xml_id("dummy:", "test id")
        )
        self.assertEqual(
            (False, msg % ("dum?my", "?")),
            utils.validate_xml_id("dum?my", "test id")
        )
        self.assertEqual(
            (False, msg % ("dummy?", "?")),
            utils.validate_xml_id("dummy?", "test id")
        )

    def testIsIso8601Date(self):
        self.assertTrue(utils.is_iso8601_date("2014-07-03"))
        self.assertTrue(utils.is_iso8601_date("2014-07-03T11:35:14"))
        self.assertTrue(utils.is_iso8601_date("20140703"))
        self.assertTrue(utils.is_iso8601_date("2014-W27-4"))
        self.assertTrue(utils.is_iso8601_date("2014-184"))

        self.assertFalse(utils.is_iso8601_date(""))
        self.assertFalse(utils.is_iso8601_date("foo"))
        self.assertFalse(utils.is_iso8601_date("2014-07-32"))
        self.assertFalse(utils.is_iso8601_date("2014-13-03"))
        self.assertFalse(utils.is_iso8601_date("2014-W27-8"))
        self.assertFalse(utils.is_iso8601_date("2014-367"))

    def test_is_score(self):
        self.assertTrue(utils.is_score("INFINITY"))
        self.assertTrue(utils.is_score("+INFINITY"))
        self.assertTrue(utils.is_score("-INFINITY"))
        self.assertTrue(utils.is_score("0"))
        self.assertTrue(utils.is_score("+0"))
        self.assertTrue(utils.is_score("-0"))
        self.assertTrue(utils.is_score("123"))
        self.assertTrue(utils.is_score("-123"))
        self.assertTrue(utils.is_score("+123"))

        self.assertFalse(utils.is_score(""))
        self.assertFalse(utils.is_score("abc"))
        self.assertFalse(utils.is_score("+abc"))
        self.assertFalse(utils.is_score("-abc"))
        self.assertFalse(utils.is_score("10a"))
        self.assertFalse(utils.is_score("+10a"))
        self.assertFalse(utils.is_score("-10a"))
        self.assertFalse(utils.is_score("a10"))
        self.assertFalse(utils.is_score("+a10"))
        self.assertFalse(utils.is_score("a-10"))
        self.assertFalse(utils.is_score("infinity"))
        self.assertFalse(utils.is_score("+infinity"))
        self.assertFalse(utils.is_score("-infinity"))
        self.assertFalse(utils.is_score("+InFiNiTy"))
        self.assertFalse(utils.is_score("INFINITY10"))
        self.assertFalse(utils.is_score("INFINITY+10"))
        self.assertFalse(utils.is_score("-INFINITY10"))
        self.assertFalse(utils.is_score("+INFINITY+10"))
        self.assertFalse(utils.is_score("10INFINITY"))
        self.assertFalse(utils.is_score("+10+INFINITY"))

    def test_get_timeout_seconds(self):
        self.assertEqual(utils.get_timeout_seconds("10"), 10)
        self.assertEqual(utils.get_timeout_seconds("10s"), 10)
        self.assertEqual(utils.get_timeout_seconds("10sec"), 10)
        self.assertEqual(utils.get_timeout_seconds("10m"), 600)
        self.assertEqual(utils.get_timeout_seconds("10min"), 600)
        self.assertEqual(utils.get_timeout_seconds("10h"), 36000)
        self.assertEqual(utils.get_timeout_seconds("10hr"), 36000)

        self.assertEqual(utils.get_timeout_seconds("1a1s"), None)
        self.assertEqual(utils.get_timeout_seconds("10mm"), None)
        self.assertEqual(utils.get_timeout_seconds("10mim"), None)
        self.assertEqual(utils.get_timeout_seconds("aaa"), None)
        self.assertEqual(utils.get_timeout_seconds(""), None)

        self.assertEqual(utils.get_timeout_seconds("1a1s", True), "1a1s")
        self.assertEqual(utils.get_timeout_seconds("10mm", True), "10mm")
        self.assertEqual(utils.get_timeout_seconds("10mim", True), "10mim")
        self.assertEqual(utils.get_timeout_seconds("aaa", True), "aaa")
        self.assertEqual(utils.get_timeout_seconds("", True), "")

    def get_cib_status_lrm(self):
        cib_dom = self.get_cib_empty()
        new_status = xml.dom.minidom.parseString("""
<status>
  <node_state id="1" uname="rh70-node1">
    <lrm id="1">
      <lrm_resources>
        <lrm_resource id="dummy" type="Dummy" class="ocf" provider="heartbeat">
          <lrm_rsc_op id="dummy_monitor_30000" operation="monitor" call-id="34"
            rc-code="1" on_node="Xrh70-node1X" exit-reason="test" />
          <lrm_rsc_op id="dummy_stop_0" operation="stop" call-id="32"
            rc-code="0" />
          <lrm_rsc_op id="dummy_start_0" operation="start" call-id="33"
            rc-code="0" />
        </lrm_resource>
      </lrm_resources>
    </lrm>
  </node_state>
  <node_state id="2" uname="rh70-node2">
    <lrm id="2">
      <lrm_resources>
        <lrm_resource id="dummy" type="Dummy" class="ocf" provider="heartbeat">
          <lrm_rsc_op id="dummy_monitor_0" operation="monitor" call-id="5"
            rc-code="1" />
        </lrm_resource>
        <lrm_resource id="dummy1" type="Dummy" class="ocf" provider="heartbeat">
          <lrm_rsc_op id="dummy1_monitor_0" operation="monitor" call-id="3"
            rc-code="0" />
        </lrm_resource>
      </lrm_resources>
    </lrm>
  </node_state>
</status>
        """).documentElement
        status = cib_dom.getElementsByTagName("status")[0]
        status.parentNode.replaceChild(new_status, status)
        return cib_dom

    def test_resource_running_on(self):
        status = xml.dom.minidom.parseString("""
<crm_mon>
    <summary />
    <nodes />
    <resources>
        <resource id="myResource" role="Started">
            <node name="rh70-node1" />
        </resource>
        <clone id="myClone">
            <resource id="myClonedResource" role="Started">
                <node name="rh70-node1" />
            </resource>
            <resource id="myClonedResource" role="Started">
                <node name="rh70-node2" />
            </resource>
            <resource id="myClonedResource" role="Started">
                <node name="rh70-node3" />
            </resource>
        </clone>
        <clone id="myMaster">
            <resource id="myMasteredResource:1" role="Slave">
                <node name="rh70-node2" />
            </resource>
            <resource id="myMasteredResource" role="Slave">
                <node name="rh70-node3" />
            </resource>
            <resource id="myMasteredResource" role="Master">
                <node name="rh70-node1" />
            </resource>
        </clone>
        <group id="myGroup">
             <resource id="myGroupedResource" role="Started">
                 <node name="rh70-node2" />
             </resource>
        </group>
        <clone id="myGroupClone">
            <group id="myClonedGroup:0">
                 <resource id="myClonedGroupedResource" role="Started">
                     <node name="rh70-node1" />
                 </resource>
            </group>
            <group id="myClonedGroup:1">
                 <resource id="myClonedGroupedResource" role="Started">
                     <node name="rh70-node2" />
                 </resource>
            </group>
            <group id="myClonedGroup:2">
                 <resource id="myClonedGroupedResource" role="Started">
                     <node name="rh70-node3" />
                 </resource>
            </group>
            <group id="myClonedGroup:3">
                 <resource id="myClonedGroupedResource" role="Started">
                     <node name="rh70-node3" />
                 </resource>
            </group>
        </clone>
        <clone id="myGroupMaster">
            <group id="myMasteredGroup:0">
                 <resource id="myMasteredGroupedResource" role="Slave">
                     <node name="rh70-node1" />
                 </resource>
            </group>
            <group id="myMasteredGroup:1">
                 <resource id="myMasteredGroupedResource" role="Master">
                     <node name="rh70-node2" />
                 </resource>
            </group>
            <group id="myMasteredGroup:2">
                 <resource id="myMasteredGroupedResource" role="Slave">
                     <node name="rh70-node3" />
                 </resource>
            </group>
        </clone>
        <resource id="myStoppedResource" role="Stopped">
        </resource>
    </resources>
</crm_mon>
        """).documentElement

        self.assertEqual(
            utils.resource_running_on("myResource", status),
            {
                'message':
                    "Resource 'myResource' is running on node rh70-node1.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node1"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myClonedResource", status),
            {
                'message':
                    "Resource 'myClonedResource' is running on nodes "
                        "rh70-node1, rh70-node2, rh70-node3.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node1", "rh70-node2", "rh70-node3"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myClone", status),
            {
                'message':
                    "Resource 'myClone' is running on nodes "
                        "rh70-node1, rh70-node2, rh70-node3.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node1", "rh70-node2", "rh70-node3"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myMasteredResource", status),
            {
                'message':
                    "Resource 'myMasteredResource' is master on node "
                        "rh70-node1; slave on nodes rh70-node2, rh70-node3.",
                'is_running': True,
                'nodes_master': ["rh70-node1"],
                'nodes_slave': ["rh70-node2", "rh70-node3"],
                'nodes_started': [],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myMaster", status),
            {
                'message':
                    "Resource 'myMaster' is master on node "
                        "rh70-node1; slave on nodes rh70-node2, rh70-node3.",
                'is_running': True,
                'nodes_master': ["rh70-node1"],
                'nodes_slave': ["rh70-node2", "rh70-node3"],
                'nodes_started': [],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myGroupedResource", status),
            {
                'message':
                    "Resource 'myGroupedResource' is running on node "
                        "rh70-node2.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node2"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myGroup", status),
            {
                'message':
                    "Resource 'myGroup' is running on node "
                        "rh70-node2.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node2"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myClonedGroupedResource", status),
            {
                'message':
                    "Resource 'myClonedGroupedResource' is running on nodes "
                        "rh70-node1, rh70-node2, rh70-node3, rh70-node3.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node1", "rh70-node2", "rh70-node3",
                    "rh70-node3"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myClonedGroup", status),
            {
                'message':
                    "Resource 'myClonedGroup' is running on nodes "
                        "rh70-node1, rh70-node2, rh70-node3, rh70-node3.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node1", "rh70-node2", "rh70-node3",
                    "rh70-node3"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myGroupClone", status),
            {
                'message':
                    "Resource 'myGroupClone' is running on nodes "
                        "rh70-node1, rh70-node2, rh70-node3, rh70-node3.",
                'is_running': True,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': ["rh70-node1", "rh70-node2", "rh70-node3",
                    "rh70-node3"],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myMasteredGroupedResource", status),
            {
                'message':
                    "Resource 'myMasteredGroupedResource' is master on node "
                        "rh70-node2; slave on nodes rh70-node1, rh70-node3.",
                'is_running': True,
                'nodes_master': ["rh70-node2"],
                'nodes_slave': ["rh70-node1", "rh70-node3"],
                'nodes_started': [],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myMasteredGroup", status),
            {
                'message':
                    "Resource 'myMasteredGroup' is master on node "
                        "rh70-node2; slave on nodes rh70-node1, rh70-node3.",
                'is_running': True,
                'nodes_master': ["rh70-node2"],
                'nodes_slave': ["rh70-node1", "rh70-node3"],
                'nodes_started': [],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myGroupMaster", status),
            {
                'message':
                    "Resource 'myGroupMaster' is master on node "
                        "rh70-node2; slave on nodes rh70-node1, rh70-node3.",
                'is_running': True,
                'nodes_master': ["rh70-node2"],
                'nodes_slave': ["rh70-node1", "rh70-node3"],
                'nodes_started': [],
            }
        )
        self.assertEqual(
            utils.resource_running_on("notMyResource", status),
            {
                'message':
                    "Resource 'notMyResource' is not running on any node",
                'is_running': False,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': [],
            }
        )
        self.assertEqual(
            utils.resource_running_on("myStoppedResource", status),
            {
                'message':
                    "Resource 'myStoppedResource' is not running on any node",
                'is_running': False,
                'nodes_master': [],
                'nodes_slave': [],
                'nodes_started': [],
            }
        )

    def test_parse_cman_quorum_info(self):
        parsed = utils.parse_cman_quorum_info("""\
Version: 6.2.0
Config Version: 23
Cluster Name: cluster66
Cluster Id: 22265
Cluster Member: Yes
Cluster Generation: 3612
Membership state: Cluster-Member
Nodes: 3
Expected votes: 3
Total votes: 3
Node votes: 1
Quorum: 2 
Active subsystems: 8
Flags: 
Ports Bound: 0 
Node name: rh66-node2
Node ID: 2
Multicast addresses: 239.192.86.80
Node addresses: 192.168.122.61
---Votes---
1 M 3 rh66-node1
2 M 2 rh66-node2
3 M 1 rh66-node3
""")
        self.assertEqual(True, parsed["quorate"])
        self.assertEqual(2, parsed["quorum"])
        self.assertEqual(
            [
                {"name": "rh66-node1", "votes": 3, "local": False},
                {"name": "rh66-node2", "votes": 2, "local": True},
                {"name": "rh66-node3", "votes": 1, "local": False},
            ],
            parsed["node_list"]
        )

        parsed = utils.parse_cman_quorum_info("""\
Version: 6.2.0
Config Version: 23
Cluster Name: cluster66
Cluster Id: 22265
Cluster Member: Yes
Cluster Generation: 3612
Membership state: Cluster-Member
Nodes: 3
Expected votes: 3
Total votes: 3
Node votes: 1
Quorum: 2 Activity blocked
Active subsystems: 8
Flags: 
Ports Bound: 0 
Node name: rh66-node1
Node ID: 1
Multicast addresses: 239.192.86.80
Node addresses: 192.168.122.61
---Votes---
1 M 3 rh66-node1
2 X 2 rh66-node2
3 X 1 rh66-node3
""")
        self.assertEqual(False, parsed["quorate"])
        self.assertEqual(2, parsed["quorum"])
        self.assertEqual(
            [
                {"name": "rh66-node1", "votes": 3, "local": True},
            ],
            parsed["node_list"]
        )

        parsed = utils.parse_cman_quorum_info("")
        self.assertEqual(None, parsed)

        parsed = utils.parse_cman_quorum_info("""\
Version: 6.2.0
Config Version: 23
Cluster Name: cluster66
Cluster Id: 22265
Cluster Member: Yes
Cluster Generation: 3612
Membership state: Cluster-Member
Nodes: 3
Expected votes: 3
Total votes: 3
Node votes: 1
Quorum: 
Active subsystems: 8
Flags: 
Ports Bound: 0 
Node name: rh66-node2
Node ID: 2
Multicast addresses: 239.192.86.80
Node addresses: 192.168.122.61
---Votes---
1 M 3 rh66-node1
2 M 2 rh66-node2
3 M 1 rh66-node3
""")
        self.assertEqual(None, parsed)

        parsed = utils.parse_cman_quorum_info("""\
Version: 6.2.0
Config Version: 23
Cluster Name: cluster66
Cluster Id: 22265
Cluster Member: Yes
Cluster Generation: 3612
Membership state: Cluster-Member
Nodes: 3
Expected votes: 3
Total votes: 3
Node votes: 1
Quorum: Foo
Active subsystems: 8
Flags: 
Ports Bound: 0 
Node name: rh66-node2
Node ID: 2
Multicast addresses: 239.192.86.80
Node addresses: 192.168.122.61
---Votes---
1 M 3 rh66-node1
2 M 2 rh66-node2
3 M 1 rh66-node3
""")
        self.assertEqual(None, parsed)

        parsed = utils.parse_cman_quorum_info("""\
Version: 6.2.0
Config Version: 23
Cluster Name: cluster66
Cluster Id: 22265
Cluster Member: Yes
Cluster Generation: 3612
Membership state: Cluster-Member
Nodes: 3
Expected votes: 3
Total votes: 3
Node votes: 1
Quorum: 4
Active subsystems: 8
Flags: 
Ports Bound: 0 
Node name: rh66-node2
Node ID: 2
Multicast addresses: 239.192.86.80
Node addresses: 192.168.122.61
---Votes---
1 M 3 rh66-node1
2 M Foo rh66-node2
3 M 1 rh66-node3
""")
        self.assertEqual(None, parsed)

    def test_parse_quorumtool_output(self):
        parsed = utils.parse_quorumtool_output("""\
Quorum information
------------------
Date:             Fri Jan 16 13:03:28 2015
Quorum provider:  corosync_votequorum
Nodes:            3
Node ID:          1
Ring ID:          19860
Quorate:          Yes

Votequorum information
----------------------
Expected votes:   3
Highest expected: 3
Total votes:      3
Quorum:           2
Flags:            Quorate

Membership information
----------------------
    Nodeid      Votes    Qdevice Name
         1          3         NR rh70-node1
         2          2         NR rh70-node2 (local)
         3          1         NR rh70-node3
""")
        self.assertEqual(True, parsed["quorate"])
        self.assertEqual(2, parsed["quorum"])
        self.assertEqual(
            [
                {"name": "rh70-node1", "votes": 3, "local": False},
                {"name": "rh70-node2", "votes": 2, "local": True},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
            parsed["node_list"]
        )

        parsed = utils.parse_quorumtool_output("""\
Quorum information
------------------
Date:             Fri Jan 16 13:03:35 2015
Quorum provider:  corosync_votequorum
Nodes:            1
Node ID:          1
Ring ID:          19868
Quorate:          No

Votequorum information
----------------------
Expected votes:   3
Highest expected: 3
Total votes:      1
Quorum:           2 Activity blocked
Flags:            

Membership information
----------------------
    Nodeid      Votes    Qdevice Name
             1          1         NR rh70-node1 (local)
""")
        self.assertEqual(False, parsed["quorate"])
        self.assertEqual(2, parsed["quorum"])
        self.assertEqual(
            [
                {"name": "rh70-node1", "votes": 1, "local": True},
            ],
            parsed["node_list"]
        )

        parsed = utils.parse_quorumtool_output("")
        self.assertEqual(None, parsed)

        parsed = utils.parse_quorumtool_output("""\
Quorum information
------------------
Date:             Fri Jan 16 13:03:28 2015
Quorum provider:  corosync_votequorum
Nodes:            3
Node ID:          1
Ring ID:          19860
Quorate:          Yes

Votequorum information
----------------------
Expected votes:   3
Highest expected: 3
Total votes:      3
Quorum:           
Flags:            Quorate

Membership information
----------------------
    Nodeid      Votes    Qdevice Name
         1          1         NR rh70-node1 (local)
         2          1         NR rh70-node2
         3          1         NR rh70-node3
""")
        self.assertEqual(None, parsed)

        parsed = utils.parse_quorumtool_output("""\
Quorum information
------------------
Date:             Fri Jan 16 13:03:28 2015
Quorum provider:  corosync_votequorum
Nodes:            3
Node ID:          1
Ring ID:          19860
Quorate:          Yes

Votequorum information
----------------------
Expected votes:   3
Highest expected: 3
Total votes:      3
Quorum:           Foo
Flags:            Quorate

Membership information
----------------------
    Nodeid      Votes    Qdevice Name
         1          1         NR rh70-node1 (local)
         2          1         NR rh70-node2
         3          1         NR rh70-node3
""")
        self.assertEqual(None, parsed)

        parsed = utils.parse_quorumtool_output("""\
Quorum information
------------------
Date:             Fri Jan 16 13:03:28 2015
Quorum provider:  corosync_votequorum
Nodes:            3
Node ID:          1
Ring ID:          19860
Quorate:          Yes

Votequorum information
----------------------
Expected votes:   3
Highest expected: 3
Total votes:      3
Quorum:           2
Flags:            Quorate

Membership information
----------------------
    Nodeid      Votes    Qdevice Name
         1          1         NR rh70-node1 (local)
         2        foo         NR rh70-node2
         3          1         NR rh70-node3
""")
        self.assertEqual(None, parsed)

    def test_is_node_stop_cause_quorum_loss(self):
        quorum_info = {
            "quorate": False,
        }
        self.assertEqual(
            False,
            utils.is_node_stop_cause_quorum_loss(quorum_info, True)
        )

        quorum_info = {
            "quorate": True,
            "quorum": 1,
            "node_list": [
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            False,
            utils.is_node_stop_cause_quorum_loss(quorum_info, True)
        )

        quorum_info = {
            "quorate": True,
            "quorum": 1,
            "node_list": [
                {"name": "rh70-node3", "votes": 1, "local": True},
            ],
        }
        self.assertEqual(
            True,
            utils.is_node_stop_cause_quorum_loss(quorum_info, True)
        )

        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 3, "local": False},
                {"name": "rh70-node2", "votes": 2, "local": False},
                {"name": "rh70-node3", "votes": 1, "local": True},
            ],
        }
        self.assertEqual(
            False,
            utils.is_node_stop_cause_quorum_loss(quorum_info, True)
        )

        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 3, "local": False},
                {"name": "rh70-node2", "votes": 2, "local": True},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            False,
            utils.is_node_stop_cause_quorum_loss(quorum_info, True)
        )

        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 3, "local": True},
                {"name": "rh70-node2", "votes": 2, "local": False},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            True,
            utils.is_node_stop_cause_quorum_loss(quorum_info, True)
        )


        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 3, "local": True},
                {"name": "rh70-node2", "votes": 2, "local": False},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            False,
            utils.is_node_stop_cause_quorum_loss(
                quorum_info, False, ["rh70-node3"]
            )
        )

        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 3, "local": True},
                {"name": "rh70-node2", "votes": 2, "local": False},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            False,
            utils.is_node_stop_cause_quorum_loss(
                quorum_info, False, ["rh70-node2"]
            )
        )

        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 3, "local": True},
                {"name": "rh70-node2", "votes": 2, "local": False},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            True,
            utils.is_node_stop_cause_quorum_loss(
                quorum_info, False, ["rh70-node1"]
            )
        )

        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 4, "local": True},
                {"name": "rh70-node2", "votes": 1, "local": False},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            False,
            utils.is_node_stop_cause_quorum_loss(
                quorum_info, False, ["rh70-node2", "rh70-node3"]
            )
        )

        quorum_info = {
            "quorate": True,
            "quorum": 4,
            "node_list": [
                {"name": "rh70-node1", "votes": 3, "local": True},
                {"name": "rh70-node2", "votes": 2, "local": False},
                {"name": "rh70-node3", "votes": 1, "local": False},
            ],
        }
        self.assertEqual(
            True,
            utils.is_node_stop_cause_quorum_loss(
                quorum_info, False, ["rh70-node2", "rh70-node3"]
            )
        )

    def test_get_operations_from_transitions(self):
        transitions = utils.parse(os.path.join(currentdir, "transitions01.xml"))
        self.assertEqual(
            [
                {
                    'id': 'dummy',
                    'long_id': 'dummy',
                    'operation': 'stop',
                    'on_node': 'rh7-3',
                },
                {
                    'id': 'dummy',
                    'long_id': 'dummy',
                    'operation': 'start',
                    'on_node': 'rh7-2',
                },
                {
                    'id': 'd0',
                    'long_id': 'd0:1',
                    'operation': 'stop',
                    'on_node': 'rh7-1',
                },
                {
                    'id': 'd0',
                    'long_id': 'd0:1',
                    'operation': 'start',
                    'on_node': 'rh7-2',
                },
                {
                    'id': 'state',
                    'long_id': 'state:0',
                    'operation': 'stop',
                    'on_node': 'rh7-3',
                },
                {
                    'id': 'state',
                    'long_id': 'state:0',
                    'operation': 'start',
                    'on_node': 'rh7-2',
                },
            ],
            utils.get_operations_from_transitions(transitions)
        )

    def test_get_resources_location_from_operations(self):
        cib_dom = self.get_cib_resources()

        operations = []
        self.assertEqual(
            {},
            utils.get_resources_location_from_operations(cib_dom, operations)
        )

        operations = [
            {
                "id": "myResource",
                "long_id": "myResource",
                "operation": "start",
                "on_node": "rh7-1",
            },
        ]
        self.assertEqual(
            {
                'myResource': {
                    'id': 'myResource',
                    'id_for_constraint': 'myResource',
                    'long_id': 'myResource',
                    'start_on_node': 'rh7-1',
                 },
            },
            utils.get_resources_location_from_operations(cib_dom, operations)
        )

        operations = [
            {
                "id": "myResource",
                "long_id": "myResource",
                "operation": "start",
                "on_node": "rh7-1",
            },
            {
                "id": "myResource",
                "long_id": "myResource",
                "operation": "start",
                "on_node": "rh7-2",
            },
            {
                "id": "myResource",
                "long_id": "myResource",
                "operation": "monitor",
                "on_node": "rh7-3",
            },
            {
                "id": "myResource",
                "long_id": "myResource",
                "operation": "stop",
                "on_node": "rh7-3",
            },
        ]
        self.assertEqual(
            {
                'myResource': {
                    'id': 'myResource',
                    'id_for_constraint': 'myResource',
                    'long_id': 'myResource',
                    'start_on_node': 'rh7-2',
                 },
            },
            utils.get_resources_location_from_operations(cib_dom, operations)
        )

        operations = [
            {
                "id": "myResource",
                "long_id": "myResource",
                "operation": "start",
                "on_node": "rh7-1",
            },
            {
                "id": "myClonedResource",
                "long_id": "myClonedResource:0",
                "operation": "start",
                "on_node": "rh7-1",
            },
            {
                "id": "myClonedResource",
                "long_id": "myClonedResource:0",
                "operation": "start",
                "on_node": "rh7-2",
            },
            {
                "id": "myClonedResource",
                "long_id": "myClonedResource:1",
                "operation": "start",
                "on_node": "rh7-3",
            },
        ]
        self.assertEqual(
            {
                'myResource': {
                    'id': 'myResource',
                    'id_for_constraint': 'myResource',
                    'long_id': 'myResource',
                    'start_on_node': 'rh7-1',
                 },
                'myClonedResource:0': {
                    'id': 'myClonedResource',
                    'id_for_constraint': 'myClone',
                    'long_id': 'myClonedResource:0',
                    'start_on_node': 'rh7-2',
                 },
                'myClonedResource:1': {
                    'id': 'myClonedResource',
                    'id_for_constraint': 'myClone',
                    'long_id': 'myClonedResource:1',
                    'start_on_node': 'rh7-3',
                 },
            },
            utils.get_resources_location_from_operations(cib_dom, operations)
        )

        operations = [
            {
                "id": "myMasteredGroupedResource",
                "long_id": "myMasteredGroupedResource:0",
                "operation": "start",
                "on_node": "rh7-1",
            },
            {
                "id": "myMasteredGroupedResource",
                "long_id": "myMasteredGroupedResource:1",
                "operation": "demote",
                "on_node": "rh7-2",
            },
            {
                "id": "myMasteredGroupedResource",
                "long_id": "myMasteredGroupedResource:1",
                "operation": "promote",
                "on_node": "rh7-3",
            },
        ]
        self.assertEqual(
            {
                'myMasteredGroupedResource:0': {
                    'id': 'myMasteredGroupedResource',
                    'id_for_constraint': 'myGroupMaster',
                    'long_id': 'myMasteredGroupedResource:0',
                    'start_on_node': 'rh7-1',
                 },
                'myMasteredGroupedResource:1': {
                    'id': 'myMasteredGroupedResource',
                    'id_for_constraint': 'myGroupMaster',
                    'long_id': 'myMasteredGroupedResource:1',
                    'promote_on_node': 'rh7-3',
                 },
            },
            utils.get_resources_location_from_operations(cib_dom, operations)
        )

    def assert_element_id(self, node, node_id):
        self.assertTrue(
            isinstance(node, xml.dom.minidom.Element),
            "element with id '%s' not found" % node_id
        )
        self.assertEqual(node.getAttribute("id"), node_id)


if __name__ == "__main__":
    unittest.main()

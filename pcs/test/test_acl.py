from __future__ import absolute_import
from __future__ import print_function
import os,sys
import shutil
import unittest
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
import utils
from pcs_test_functions import pcs,ac,isMinimumPacemakerVersion

old_cib = "empty.xml"
empty_cib = "empty-1.2.xml"
temp_cib = "temp.xml"

class ACLTest(unittest.TestCase):
    def setUp(self):
        shutil.copy(empty_cib, temp_cib)
        shutil.copy("corosync.conf.orig", "corosync.conf")

    def testAutoUpgradeofCIB(self):
        old_temp_cib = temp_cib + "-old"
        shutil.copy(old_cib, old_temp_cib)

        o,r = pcs(old_temp_cib, "acl show")
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\n")
        assert r == 0

        with open(old_temp_cib) as myfile:
            data = myfile.read()
            assert data.find("pacemaker-1.2") != -1
            assert data.find("pacemaker-2.") == -1

        o,r = pcs(old_temp_cib, "acl role create test_role read xpath my_xpath")
        ac(o,"Cluster CIB has been upgraded to latest version\n")
        assert r == 0

        with open(old_temp_cib) as myfile:
            data = myfile.read()
            assert data.find("pacemaker-1.2") == -1
            assert data.find("pacemaker-2.") != -1

    def testEnableDisable(self):
        o,r = pcs("acl disable")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\n")

        o,r = pcs("acl enable")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are enabled\n\n")

        o,r = pcs("acl disable")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\n")

    def testUserGroupCreateDeleteWithRoles(self):
        o,r = pcs("acl role create role1 read xpath /xpath1/ write xpath /xpath2/")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl role create role2 deny xpath /xpath3/ deny xpath /xpath4/")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl role create role3 read xpath /xpath5/ read xpath /xpath6/")
        assert r == 0
        ac(o,"")

        o, r = pcs("acl user create user1 roleX")
        ac(o, "Error: cannot find acl role: roleX\n")
        self.assertEquals(1, r)

        o, r = pcs("acl user create user1 role1 roleX")
        ac(o, "Error: cannot find acl role: roleX\n")
        self.assertEquals(1, r)

        o, r = pcs("acl group create group1 roleX")
        ac(o, "Error: cannot find acl role: roleX\n")
        self.assertEquals(1, r)

        o, r = pcs("acl group create group1 role1 roleX")
        ac(o, "Error: cannot find acl role: roleX\n")
        self.assertEquals(1, r)

        o, r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

Role: role1
  Permission: read xpath /xpath1/ (role1-read)
  Permission: write xpath /xpath2/ (role1-write)
Role: role2
  Permission: deny xpath /xpath3/ (role2-deny)
  Permission: deny xpath /xpath4/ (role2-deny-1)
Role: role3
  Permission: read xpath /xpath5/ (role3-read)
  Permission: read xpath /xpath6/ (role3-read-1)
""")
        self.assertEquals(0, r)

        o,r = pcs("acl user create user1 role1 role2")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl group create group1 role1 role3")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: role1 role2\nGroup: group1\n  Roles: role1 role3\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\nRole: role2\n  Permission: deny xpath /xpath3/ (role2-deny)\n  Permission: deny xpath /xpath4/ (role2-deny-1)\nRole: role3\n  Permission: read xpath /xpath5/ (role3-read)\n  Permission: read xpath /xpath6/ (role3-read-1)\n")

        o,r = pcs("acl role create user1")
        assert r == 1
        ac(o,"Error: user1 already exists\n")

        o,r = pcs("acl role create group1")
        assert r == 1
        ac(o,"Error: group1 already exists\n")

        o,r = pcs("acl role create role1")
        assert r == 1
        ac(o,"Error: role role1 already exists\n")

        o,r = pcs("acl user create user1")
        assert r == 1
        ac(o,"Error: user user1 already exists\n")

        o,r = pcs("acl user create group1")
        assert r == 1
        ac(o,"Error: group1 already exists\n")

        o,r = pcs("acl user create role1")
        assert r == 1
        ac(o,"Error: role1 already exists\n")

        o,r = pcs("acl group create user1")
        assert r == 1
        ac(o,"Error: user1 already exists\n")

        o,r = pcs("acl group create group1")
        assert r == 1
        ac(o,"Error: group group1 already exists\n")

        o,r = pcs("acl group create role1")
        assert r == 1
        ac(o,"Error: role1 already exists\n")

        o,r = pcs("acl role assign role1 to noexist")
        assert r == 1
        ac(o,"Error: cannot find user or group: noexist\n")

        o,r = pcs("acl role assign noexist to user1")
        assert r == 1
        ac(o,"Error: cannot find role: noexist\n")

        o,r = pcs("acl role assign role3 to user1")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: role1 role2 role3\nGroup: group1\n  Roles: role1 role3\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\nRole: role2\n  Permission: deny xpath /xpath3/ (role2-deny)\n  Permission: deny xpath /xpath4/ (role2-deny-1)\nRole: role3\n  Permission: read xpath /xpath5/ (role3-read)\n  Permission: read xpath /xpath6/ (role3-read-1)\n")

        o,r = pcs("acl role unassign noexist from user1")
        assert r == 1
        ac(o,"Error: cannot find role: noexist, assigned to user/group: user1\n")

        o,r = pcs("acl role unassign role3 from noexist")
        assert r == 1
        ac(o,"Error: cannot find user or group: noexist\n")

        o,r = pcs("acl role unassign role3 from user1")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: role1 role2\nGroup: group1\n  Roles: role1 role3\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\nRole: role2\n  Permission: deny xpath /xpath3/ (role2-deny)\n  Permission: deny xpath /xpath4/ (role2-deny-1)\nRole: role3\n  Permission: read xpath /xpath5/ (role3-read)\n  Permission: read xpath /xpath6/ (role3-read-1)\n")

        o,r = pcs("acl role unassign role2 from user1")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl role unassign role1 from user1")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: \nGroup: group1\n  Roles: role1 role3\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\nRole: role2\n  Permission: deny xpath /xpath3/ (role2-deny)\n  Permission: deny xpath /xpath4/ (role2-deny-1)\nRole: role3\n  Permission: read xpath /xpath5/ (role3-read)\n  Permission: read xpath /xpath6/ (role3-read-1)\n")

        o,r = pcs("acl role delete role3")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: \nGroup: group1\n  Roles: role1\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\nRole: role2\n  Permission: deny xpath /xpath3/ (role2-deny)\n  Permission: deny xpath /xpath4/ (role2-deny-1)\n")

        o,r = pcs("acl role assign role2 to user1")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: role2\nGroup: group1\n  Roles: role1\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\nRole: role2\n  Permission: deny xpath /xpath3/ (role2-deny)\n  Permission: deny xpath /xpath4/ (role2-deny-1)\n")

        o,r = pcs("acl role assign role1 user1")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

User: user1
  Roles: role2 role1
Group: group1
  Roles: role1
Role: role1
  Permission: read xpath /xpath1/ (role1-read)
  Permission: write xpath /xpath2/ (role1-write)
Role: role2
  Permission: deny xpath /xpath3/ (role2-deny)
  Permission: deny xpath /xpath4/ (role2-deny-1)
""")
        assert r == 0

        o,r = pcs("acl role unassign role2 from user1 --autodelete")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

User: user1
  Roles: role1
Group: group1
  Roles: role1
Role: role1
  Permission: read xpath /xpath1/ (role1-read)
  Permission: write xpath /xpath2/ (role1-write)
Role: role2
  Permission: deny xpath /xpath3/ (role2-deny)
  Permission: deny xpath /xpath4/ (role2-deny-1)
""")
        assert r == 0

        o,r = pcs("acl role unassign role1 from user1 --autodelete")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

Group: group1
  Roles: role1
Role: role1
  Permission: read xpath /xpath1/ (role1-read)
  Permission: write xpath /xpath2/ (role1-write)
Role: role2
  Permission: deny xpath /xpath3/ (role2-deny)
  Permission: deny xpath /xpath4/ (role2-deny-1)
""")
        assert r == 0

        o,r = pcs("acl user create user1 role1 role2")
        ac(o, "")
        assert r == 0

        o,r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

User: user1
  Roles: role1 role2
Group: group1
  Roles: role1
Role: role1
  Permission: read xpath /xpath1/ (role1-read)
  Permission: write xpath /xpath2/ (role1-write)
Role: role2
  Permission: deny xpath /xpath3/ (role2-deny)
  Permission: deny xpath /xpath4/ (role2-deny-1)
""")
        assert r == 0

        o,r = pcs("acl role delete role1 --autodelete")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

User: user1
  Roles: role2
Role: role2
  Permission: deny xpath /xpath3/ (role2-deny)
  Permission: deny xpath /xpath4/ (role2-deny-1)
""")
        assert r == 0

    def testUserGroupCreateDelete(self):
        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\n")

        o,r = pcs("acl user create user1")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl user create user2")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl user create user1")
        assert r == 1
        ac(o,"Error: user user1 already exists\n")

        o,r = pcs("acl group create group1")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl group create group2")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl group create group1")
        assert r == 1
        ac(o,"Error: group group1 already exists\n")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: \nUser: user2\n  Roles: \nGroup: group1\n  Roles: \nGroup: group2\n  Roles: \n")

        o,r = pcs("acl group delete user1")
        assert r == 1
        ac(o,"Error: unable to find acl group: user1\n")

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: \nUser: user2\n  Roles: \nGroup: group1\n  Roles: \nGroup: group2\n  Roles: \n")

        o,r = pcs("acl group delete group2")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: \nUser: user2\n  Roles: \nGroup: group1\n  Roles: \n")

        o,r = pcs("acl group delete group1")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user1\n  Roles: \nUser: user2\n  Roles: \n")

        o,r = pcs("acl user delete user1")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nUser: user2\n  Roles: \n")

        o,r = pcs("acl user delete user2")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\n")

    def testRoleCreateDelete(self):
        o, r = pcs("acl role create role0 read")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 read //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 read xpath")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 read id")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 readX xpath //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 read xpathX //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 description=test read")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 description=test read //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 description=test read xpath")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 description=test read id")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs(
            "acl role create role0 description=test readX xpath //resources"
        )
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs(
            "acl role create role0 description=test read xpathX //resources"
        )
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 desc=test read")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 desc=test read //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 desc=test read xpath")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 desc=test read id")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 desc=test readX xpath //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o, r = pcs("acl role create role0 desc=test read xpathX //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl role create..."))
        self.assertEquals(1, r)

        o,r = pcs("acl")
        ac(o, "ACLs are disabled, run 'pcs acl enable' to enable\n\n")
        self.assertEquals(0, r)

        o,r = pcs("acl role create role0")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl role create role0")
        ac(o,"Error: role role0 already exists\n")
        assert r == 1

        o,r = pcs("acl role create role0d description='empty role'")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl role create role1 read xpath /xpath/")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl role create role2 description='with description' READ XPATH /xpath/")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl role create role3 Read XPath /xpath_query/ wRiTe xpATH /xpath_query2/ deny xpath /xpath_query3/")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nRole: role0\nRole: role0d\n  Description: empty role\nRole: role1\n  Permission: read xpath /xpath/ (role1-read)\nRole: role2\n  Description: with description\n  Permission: read xpath /xpath/ (role2-read)\nRole: role3\n  Permission: read xpath /xpath_query/ (role3-read)\n  Permission: write xpath /xpath_query2/ (role3-write)\n  Permission: deny xpath /xpath_query3/ (role3-deny)\n")
        assert r == 0

        o,r = pcs("acl role delete role2")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nRole: role0\nRole: role0d\n  Description: empty role\nRole: role1\n  Permission: read xpath /xpath/ (role1-read)\nRole: role3\n  Permission: read xpath /xpath_query/ (role3-read)\n  Permission: write xpath /xpath_query2/ (role3-write)\n  Permission: deny xpath /xpath_query3/ (role3-deny)\n")
        assert r == 0

        o,r = pcs("acl role delete role2")
        assert r == 1
        ac(o,"Error: unable to find acl role: role2\n")

        o,r = pcs("acl role delete role1")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl role delete role3")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl role delete role0")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl role delete role0d")
        assert r == 0
        ac(o,"")

        o,r = pcs("acl")
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\n")
        assert r == 0

    def testPermissionAddDelete(self):
        o,r = pcs("acl role create role1 read xpath /xpath1/ write xpath /xpath2/")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl role create role2 read xpath /xpath3/ write xpath /xpath4/")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl role create role3 read xpath /xpath5/ write xpath /xpath6/")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl show")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\nRole: role2\n  Permission: read xpath /xpath3/ (role2-read)\n  Permission: write xpath /xpath4/ (role2-write)\nRole: role3\n  Permission: read xpath /xpath5/ (role3-read)\n  Permission: write xpath /xpath6/ (role3-write)\n")

        o,r = pcs("acl permission add role1 deny xpath /myxpath1/")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl permission add role4 deny xpath /myxpath2/")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl show")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\n  Permission: deny xpath /myxpath1/ (role1-deny)\nRole: role2\n  Permission: read xpath /xpath3/ (role2-read)\n  Permission: write xpath /xpath4/ (role2-write)\nRole: role3\n  Permission: read xpath /xpath5/ (role3-read)\n  Permission: write xpath /xpath6/ (role3-write)\nRole: role4\n  Permission: deny xpath /myxpath2/ (role4-deny)\n")

        o,r = pcs("acl permission delete role4-deny")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl permission delete role4-deny")
        ac(o,"Error: Unable to find permission with id: role4-deny\n")
        assert r == 1

        o,r = pcs("acl show")
        assert r == 0
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\n  Permission: deny xpath /myxpath1/ (role1-deny)\nRole: role2\n  Permission: read xpath /xpath3/ (role2-read)\n  Permission: write xpath /xpath4/ (role2-write)\nRole: role3\n  Permission: read xpath /xpath5/ (role3-read)\n  Permission: write xpath /xpath6/ (role3-write)\nRole: role4\n")

        o,r = pcs("acl permission delete role3-read")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl permission delete role3-write")
        ac(o,"")
        assert r == 0

        o,r = pcs("acl")
        ac(o,"ACLs are disabled, run 'pcs acl enable' to enable\n\nRole: role1\n  Permission: read xpath /xpath1/ (role1-read)\n  Permission: write xpath /xpath2/ (role1-write)\n  Permission: deny xpath /myxpath1/ (role1-deny)\nRole: role2\n  Permission: read xpath /xpath3/ (role2-read)\n  Permission: write xpath /xpath4/ (role2-write)\nRole: role3\nRole: role4\n")
        assert r == 0

        o, r = pcs("acl permission delete role1-read")
        ac(o, "")
        self.assertEquals(0, r)

        o, r = pcs("acl permission delete role1-write")
        ac(o, "")
        self.assertEquals(0, r)

        o, r = pcs("acl permission delete role1-deny")
        ac(o, "")
        self.assertEquals(0, r)

        o, r = pcs("acl permission delete role2-read")
        ac(o, "")
        self.assertEquals(0, r)

        o, r = pcs("acl permission delete role2-write")
        ac(o, "")
        self.assertEquals(0, r)

        o, r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

Role: role1
Role: role2
Role: role3
Role: role4
""")
        self.assertEquals(0, r)

        o, r = pcs("acl permission add role1 read")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read xpath")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read id")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 readX xpath //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read xpathX //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read id dummy read")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read id dummy read //resources")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read id dummy read xpath")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl permission add role1 read id dummy read id")
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs(
            "acl permission add role1 read id dummy readX xpath //resources"
        )
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs(
            "acl permission add role1 read id dummy read xpathX //resources"
        )
        self.assertTrue(o.startswith("\nUsage: pcs acl permission add..."))
        self.assertEquals(1, r)

        o, r = pcs("acl")
        ac(o, """\
ACLs are disabled, run 'pcs acl enable' to enable

Role: role1
Role: role2
Role: role3
Role: role4
""")
        self.assertEquals(0, r)


if __name__ == "__main__":
    if isMinimumPacemakerVersion(1,1,11):
        unittest.main()
    else:
        print("WARNING: Pacemaker version is too old (must be >= 1.1.11) to test acls")

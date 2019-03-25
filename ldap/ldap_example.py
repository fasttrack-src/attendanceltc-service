import ldap
import pprint
pp = pprint.PrettyPrinter(indent=2)
pprint = pp.pprint
l = ldap.initialize("ldap://localhost")
l.simple_bind_s("uid=adamk,ou=PeopleOU,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk", "hi")
result = l.search_s("ou=PeopleOU,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk", ldap.SCOPE_SUBTREE, "uid=*dam*")
pprint(result)

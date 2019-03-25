import ldap
import pprint
pp = pprint.PrettyPrinter(indent=2)
pprint = pp.pprint
l = ldap.initialize("ldap://spitfire.campus.gla.ac.uk")
l.simple_bind_s("2333134p@campus.gla.ac.uk", "<Marcell's password>")
result = l.search_s("CN=Person,CN=Schema,CN=Configuration,DC=campus,DC=gla,DC=ac,DC=uk", ldap.SCOPE_SUBTREE, "(cn=2333134P)")
print(result)


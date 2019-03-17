First, I've installed ldap using [the following tutorial](https://www.linuxbabe.com/ubuntu/install-configure-openldap-server-ubuntu-16-04).

When configuring the ldap account, use `ad.dcs.gla.ac.uk`.

After that, one can create a single user account (adamk) and a single OU (PeopleOU) using:

`ldapadd -x -W -D "cn=admin,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk" -f ldap-adamk.ldif`
and
`ldapadd -x -W -D "cn=admin,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk" -f ldap-base.ldif`

After that initial setup, one can use `ldappasswd` to change the password of the newly created user to `hi`

`ldappasswd -s hi -W -D "cn=admin,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk" -x "uid=adamk,ou=PeopleOU,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk"`

Then, both the sh and py scripts should work, in the sense that they should search and authenticate the user respectively.
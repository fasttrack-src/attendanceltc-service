python3 ../populate.py
curl -b /tmp/cookie_import -c /tmp/cookie_import -X put --data '{"username":"admin", "password":"p"}' localhost:8000/rest-login
time curl -b /tmp/cookie_import -c /tmp/cookie_import -H "Content-Type: text/csv" --data-binary "@../anonymize/anonymized.csv" localhost:8000/students?uploadType=MATHS_STATS_CSV_1
curl -b /tmp/cookie_import -c /tmp/cookie_import localhost:8000/logout
rm /tmp/cookie_import
curl --data-binary "@anonymized.csv" -H "Content-Type: text/csv" "localhost:8000/students?uploadType=bulk"
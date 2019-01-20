#curl -v -X POST -d @1810292ho.txt localhost:5000
curl -v -F file=@1810292ho.txt --output result.zip localhost:5000

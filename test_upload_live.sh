URL="https://europe-west1-playingaround.cloudfunctions.net/csv_upload_europe"
OUTPUT=result.zip
return "$OUTPUT"
curl -v -F file=@1810292ho.txt --output "$OUTPUT" $URL
ls -l "$OUTPUT"

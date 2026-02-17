#!/bin/bash
# Fix recursive safe_datetime_now() calls
for file in $(grep -l "return safe_datetime_now()" --include="*.py" -r . | grep "def safe_datetime_now"); do
    sed -i.bak 's/return safe_datetime_now()/return datetime.now()/g' "$file"
    rm -f "$file.bak"
    echo "Fixed: $file"
done

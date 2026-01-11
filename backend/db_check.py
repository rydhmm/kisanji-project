from pymongo import MongoClient
from urllib.parse import quote_plus
import certifi

# ===============================
# 1️⃣ YOUR CREDENTIALS
# ===============================
USERNAME = "khushi_user"
PASSWORD = "Khushi@123"      # raw password
CLUSTER  = "echoharvest-cluster.hiegbsk.mongodb.net"
DB_NAME  = "echoharvest_db"  # change if needed

# ===============================
# 2️⃣ BUILD SAFE URI
# ===============================
uri = (
    "mongodb+srv://"
    f"{USERNAME}:{quote_plus(PASSWORD)}@{CLUSTER}/"
    "?retryWrites=true&w=majority"
)

# ===============================
# 3️⃣ CONNECT (TLS FIX)
# ===============================
client = MongoClient(
    uri,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client[DB_NAME]

print("Connected successfully\n")

# ===============================
# 4️⃣ SHOW ALL TABLES (COLLECTIONS)
# ===============================
collections = db.list_collection_names()

if not collections:
    print("No tables (collections) found in database.")
else:
    print("TABLES FOUND:\n")
    for col in collections:
        print(f"  - {col}")

# ===============================
# 5️⃣ SHOW STRUCTURE OF EACH TABLE
# ===============================
print("\n\nTABLE STRUCTURES:\n")

for col_name in collections:
    col = db[col_name]
    sample = col.find_one()
    count = col.count_documents({})

    print(f"Table: {col_name} (Documents: {count})")

    if sample:
        for field, value in sample.items():
            print(f"   - {field}: {type(value).__name__} = {repr(value)[:100]}")
    else:
        print("   (empty table)")

    print()

# ===============================
# 6️⃣ CLOSE
# ===============================
client.close()
print("Connection closed")

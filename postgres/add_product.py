import os
from supabase import create_client, Client #pip install supabase
from dotenv import load_dotenv # pip install python-dotenv
 
load_dotenv()
 
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb: Client = create_client(url, key)
 
def add_product(name, email, join_dates):
    payload = {"name": name, "email":email, "join_date":join_date}
    resp = sb.table("members").insert(payload).execute()
    return resp.data
 
if __name__ == "__main__":
    name = input("Enter product name: ").strip()
    email =input("Enter price: ").strip()
    join_date = input("Enter stock: ").strip()
 
    created = add_product(name,email, join_date)
    print("Inserted:", created)
 

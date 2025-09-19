import os
from supabase import create_client, Client   
from dotenv import load_dotenv        
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb: Client = create_client(url, key)


def add_member(name, email):
    payload = {"name": name, "email": email}
    resp = sb.table("members").insert(payload).execute()
    return resp.data

def add_book(title, author, category, stock):
    payload = {"title": title, "author": author, "category": category, "stock": stock}
    resp = sb.table("books").insert(payload).execute()
    return resp.data

def list_books():
    resp = sb.table("books").select("*").execute()
    return resp.data

def search_books(keyword):
    resp = sb.table("books").select("*").ilike("title", f"%{keyword}%").execute()
    return resp.data

def member_details(member_id):
    member = sb.table("members").select("*").eq("member_id", member_id).execute().data
    borrowed = sb.table("borrow_records")\
        .select("*, books(title,author)")\
        .eq("member_id", member_id)\
        .is_("return_date", None)\
        .execute().data
    return {"member": member, "borrowed_books": borrowed}

def update_member(member_id, name=None, email=None):
    payload = {}
    if name: payload["name"] = name
    if email: payload["email"] = email
    if not payload:
        return {"error": "Nothing to update"}
    resp = sb.table("members").update(payload).eq("member_id", member_id).execute()
    return resp.data

def update_book_stock(book_id, new_stock):
    resp = sb.table("books").update({"stock": new_stock}).eq("book_id", book_id).execute()
    return resp.data

def delete_member(member_id):
    borrowed = sb.table("borrow_records").select("*").eq("member_id", member_id).is_("return_date", None).execute().data
    if borrowed:
        return {"error": "Member still has borrowed books"}
    resp = sb.table("members").delete().eq("member_id", member_id).execute()
    return resp.data

def delete_book(book_id):
    borrowed = sb.table("borrow_records").select("*").eq("book_id", book_id).is_("return_date", None).execute().data
    if borrowed:
        return {"error": "Book is still borrowed"}
    resp = sb.table("books").delete().eq("book_id", book_id).execute()
    return resp.data


def borrow_book(member_id, book_id):

    book = sb.table("books").select("*").eq("book_id", book_id).execute().data
    if not book or book[0]["stock"] <= 0:
        return {"error": "Book not available"}

    sb.table("books").update({"stock": book[0]["stock"] - 1}).eq("book_id", book_id).execute()
    resp = sb.table("borrow_records").insert({"member_id": member_id, "book_id": book_id}).execute()
    return resp.data

def return_book(record_id):
    record = sb.table("borrow_records").select("*").eq("record_id", record_id).execute().data
    if not record or record[0]["return_date"] is not None:
        return {"error": "Invalid record"}

    book_id = record[0]["book_id"]


    book = sb.table("books").select("*").eq("book_id", book_id).execute().data
    sb.table("books").update({"stock": book[0]["stock"] + 1}).eq("book_id", book_id).execute()
    return {"success": True}

def top_borrowed_books():
    query = sb.rpc("top_borrowed_books").execute() 
    return query.data

def overdue_books():
    query = sb.rpc("overdue_books").execute()  
    return query.data

def borrowed_count_per_member():
    query = sb.rpc("borrowed_count_per_member").execute()
    return query.data


def main():
    while True:
        print("\n=== Online Library Management ===")
        print("1. Register Member")
        print("2. Add Book")
        print("3. List Books")
        print("4. Search Books")
        print("5. Member Details")
        print("6. Update Member")
        print("7. Update Book Stock")
        print("8. Delete Member")
        print("9. Delete Book")
        print("10. Borrow Book")
        print("11. Return Book")
        print("12. Reports")
        print("0. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Name: "); email = input("Email: ")
            print(add_member(name, email))

        elif choice == "2":
            title = input("Title: "); author = input("Author: ")
            category = input("Category: "); stock = int(input("Stock: "))
            print(add_book(title, author, category, stock))

        elif choice == "3":
            print(list_books())

        elif choice == "4":
            kw = input("Keyword: ")
            print(search_books(kw))

        elif choice == "5":
            mid = int(input("Member ID: "))
            print(member_details(mid))

        elif choice == "6":
            mid = int(input("Member ID: "))
            email = input("New Email (leave blank if none): ")
            name = input("New Name (leave blank if none): ")
            print(update_member(mid, name or None, email or None))

        elif choice == "7":
            bid = int(input("Book ID: "))
            stock = int(input("New Stock: "))
            print(update_book_stock(bid, stock))

        elif choice == "8":
            mid = int(input("Member ID: "))
            print(delete_member(mid))

        elif choice == "9":
            bid = int(input("Book ID: "))
            print(delete_book(bid))

        elif choice == "10":
            mid = int(input("Member ID: "))
            bid = int(input("Book ID: "))
            print(borrow_book(mid, bid))

        elif choice == "11":
            rid = int(input("Record ID: "))
            print(return_book(rid))

        elif choice == "12":
            print("Reports Menu (requires SQL functions in Supabase):")
            print("a) Top Borrowed Books")
            print("b) Overdue Books")
            print("c) Borrowed Count per Member")
            sub = input("Choose: ")
            if sub == "a": print(top_borrowed_books())
            elif sub == "b": print(overdue_books())
            elif sub == "c": print(borrowed_count_per_member())

        elif choice == "0":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()

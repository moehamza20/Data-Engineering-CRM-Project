from pymongo import MongoClient

#connect to mongo 
client = MongoClient("mongodb://localhost:27017/")
db = client["crm"]

users = db["users"]
posts = db["posts"]



# Insert user 
user = { 
        "name" : "Thomas" ,
        "email" : "thomas@raiseup.com" ,
        "age" : 25  
    }

result = users.insert_one(user)
print("User Added Successfull")




#insert many users 
new_users = [
    {
        "name" : "Esraa Kamel Hamdy" ,
        "email" : "esraa_kamel_hamdy@raiseup.com",
        "age" : 35 
    } ,
    {
        "name" : "Esraa Galal Elmasry" ,
        "email" : "esraa_galal_elmasry@raiseup.com",
        "age" : 18
    }
]

result  = users.insert_many(new_users)
print(f"the insert users is {len(result.inserted_ids)}")

#get all users 
for user in users.find({} , {"name" : 1 , "_id" : 0}):
    print(user["name"])




#update one  user 
for user in users.find({"name" : "Thomas"} , {"name" : 1 , "_id" : 0}):
    print(user["name"])

result = users.update_one({"name" : "Thomas"} , {"$set" : {"age" : 20} })
print("the user updated successfully")
print(f"Modified:{result.modified_count}")


#Delete user
result= users.delete_one({"name" : "Thomas"})

print("User Deleted Sucessfully")
print(f"Deleted: {result.deleted_count}")
# print("Connected ")

#get posts related by users
for post in posts.find():
    user = users.find_one({"_id" : post['user_id']})
    print(f"title : {post["title"]}")
    print(f"content : {post["content"]}")
    print(f"added by : {user["name"]}")
    print("------------------------------")
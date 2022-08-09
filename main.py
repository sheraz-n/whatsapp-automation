from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime 

cluster = MongoClient("mongodb+srv://imsheraz:19821982@cluster0.ujwntnr.mongodb.net/?retryWrites=true&w=majority")
#db = cluster["bakery"]
db = cluster.bakery
users= db["users"]
orders= db["orders"]
app = Flask(__name__)

@app.route("/", methods = ["get","post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    
    user = users.find_one({"number":number})
    if bool(user) == False:
        res.message("Hi, Thanks for contacting *The Red Velvet*.\n You can choose from the options below:"
                         + "\n\n *Type* \n\n 1️⃣ To *contact* us \n 2️⃣ To *order* Snacks \n 3️⃣ To know our *working* hours\n 4️⃣"
                         + " To get our *address*")
        users.insert_one({"number":number, "status":"main", "messages": []})
    elif user["status"]=="main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if (option == 1):
            res.message("Please contact us through phone or email.\n\n*Phone*: 9921 3456\n*Email*:you@yourself.com")
        elif (option == 2):
            res.message("You have entered *Order* Menu:")
            users.update_one({"number":number},{"$set":{"status": "order"}})
            res.message("You can select on of the following:\n\n1️⃣ Red Velvet\n2️⃣ Sponge Cake\n3️⃣ Genoise Cake\n4️⃣ Carrot Cake\n5️⃣ Plum Cake\n0️⃣ Main Menu")
        elif (option == 3):
            res.message("We work everyday from *9 AM to 9 PM*")
        elif (option == 4):
            res.message("Our main Center is at *25A, PGECHS, Lahore*")
        else:
            res.message("Please enter a valid response i.e.[ 1 2 3 4 ]")
            return str(res)
    elif user["status"]=="order":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if (option == 0):
            users.update_one({"number":number},{"$set": {"status": "main"}})
            res.message("You can choose from the options below:"
                         + "\n\n *Type* \n\n 1️⃣ To *contact* us \n 2️⃣ To *order* Snacks \n 3️⃣ To know our *working* hours\n 4️⃣"
                         + " To get our *address*")
        elif ( 1 <= option <= 5):
            cake_list = ["Red_Velvet","Sponge Cake", "Genoise Cake", "Carrot Cake", "Plum Cake"]
            selected = cake_list[option-1]
            users.update_one({"number":number},{"$set": {"status": "address"}})
            users.update_one({"number":number},{"$set": {"item": selected}})
            res.message("Excellent choice 😉")
            res.message("Please enter address for confirmation")
        else:
            res.message("Please enter a valid response")
            #return str(res)
    elif user["status"]=="address":
        selected = user["item"]
        res.message("Thanks for shopping with us!")
        res.message(f"Your order for {selected} is received successfully. The delivery will be made shortly")
        orders.insert_one({"number":number, "item":selected, "address":text, "order_time":datetime.now()})
        users.update_one({"number":number},{"$set": {"status": "ordered"}})
    elif user["status"]=="ordered":
        res.message("Thanks for ordering again from *The Red Velvet*.\n You can choose from the options below:"
                         + "\n\n *Type* \n\n 1️⃣ To *contact* us \n 2️⃣ To *order* Snacks \n 3️⃣ To know our *working* hours\n 4️⃣"
                         + " To get our *address*")
        users.update_one({"number":number},{"$set": {"status": "main"}}) 
    users.update_one({"number":number}, {"$push":{"messages": {"text":text, "date":datetime.now()}}})    
    return str(res)


if __name__ == "__main__":
    app.run(port=5000)
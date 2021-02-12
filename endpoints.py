import json
from flask import request,jsonify
from flask_restful import Resource
import pymongo
from datetime import datetime
from bson.objectid import ObjectId
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.qyhus.mongodb.net/comexdb?retryWrites=true&w=majority&authSource=admin")
db = client.comexdb

def getUser(r):
    return jsonify(code=11,
        id=str(r["_id"]),
        firebase_id=r["firebase_id"],
        name=r["name"],
        email=r["email"],
        phone=r["phone"],
        date_joined=r["date_joined"],
        fence_id=r["fence_id"],
        updated=r["updated"],
        coins=r["coins"],
        listings=r["listings"],
        exchanges=r["exchanges"])
        

class GetUser(Resource):
    '''
    method: POST
    params: firebase_id
    return: code10: New user
            code11: Existing user
            code12: Incomplete details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            res = db.users.find({"firebase_id":data["firebase_id"]})
            if res.count()==0:
                return jsonify(code=10)
            else:
                for r in res:
                    return getUser(r)
        except KeyError:
            return jsonify(msg="Incomplete details",code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown Error",code=13)

class AddUser(Resource):
    '''
    method: POST
    params: name,email,firebase_id,dob,fence_id
    return: code11: Inserted user
            code14: Error inserting to db/Already exists
            code12: Incomplete details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        print(data["phone"])
        updated = data["phone"]==None or data["phone"]=="" or data["phone"]=="+91"
        try:
            r = db.users.insert_one({
                "name":data["name"],
                "firebase_id":data["firebase_id"],
                "email":data["email"],
                "date_joined":datetime.now().strftime("%d/%m/%Y %H:%M"),
                "fence_id":data["fence_id"],
                "phone":data["phone"],
                "updated":not updated,
                "coins":500,
                "listings":0,
                "exchanges":0
            })
            if r.acknowledged:
                res = db.users.find_one({"_id":r.inserted_id})
                return getUser(res)          
            else:
                return jsonify(msg="Couldn't add to db",code=14) 
        except pymongo.errors.DuplicateKeyError:
            return jsonify(code=14,msg="Already exists")           
        except KeyError as e:
            return jsonify(msg=str(e),code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=13)

class AddBook(Resource):
    '''
    method: POST
    params: name,authors,pages,description,avg_rating,thumb_link,google_link,price,uploaded_by
    return: code20: Added
            code21: Insertion failed
            code22: Incomplete data
            code23: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            r = db.books.insert_one({
                "etag":data["etag"],
                "title":data["title"],
                "authors":data["authors"],
                "pages":data["pages"],
                "uploaded_on":datetime.now().strftime("%d/%m/%Y"),
                "description":data["description"],
                "avg_rating":data["avg_rating"],
                "thumb_link":data["thumb_link"],
                "google_link":data["google_link"],
                "price":data["price"],
                "uploaded_by":data["uploaded_by"],
                "taken":False
            })
            if r.acknowledged:
                x = db.users.update_one({"firebase_id":data["uploaded_by"]},{"$inc":{"listings":1}})
                if x.acknowledged:
                    return jsonify(code=20)
            return jsonify(msg="Couldn't add to db",code=21)            
        except KeyError as e:
            print(e)
            return jsonify(msg="Incomplete details",code=23)
        except pymongo.errors.DuplicateKeyError as e:
            print(e)
            return jsonify(msg="Already exists",code=25)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=24)

class AddFence(Resource):
    '''
    method: POST
    params: id,name,lat1,lon1,lat2,lon2
    return: code50: success
            code12: failed.keyerror
            code13: failed.unknown
            code14: failed.duplicatekey
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            r = db.fences.insert_one({
                "id":data["id"],
                "name":data["name"],
                "coordinates":{
                    "point1":{
                        "latitude":data["lat1"],
                        "longitude":data["lon1"]
                    },
                    "point2":{
                        "latitude":data["lat2"],
                        "longitude":data["lon2"]
                    }
                }
            })
            if r.acknowledged:
                return jsonify(code=50,msg="Added successfully",id=str(r.inserted_id))
            else:
                return jsonify(msg="Couldn't add to db",code=13) 
        except pymongo.errors.DuplicateKeyError:
            return jsonify(code=14,msg="Already exists")           
        except KeyError as e:
            return jsonify(msg=str(e),code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=13)

class CheckFence(Resource):
    '''
    method: POST
    params: latitude,longitude
    return: code60: fence_id
            code61: doesn't exists
            code62: failed
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            res = db.fences.find({},{"coordinates":1,"id":1})
            if res.count()==0:
                return jsonify(code=62,msg="Failed.")
            else:
                for r in res:
                    lat1 = r["coordinates"]["point1"]["latitude"]
                    lon1 = r["coordinates"]["point1"]["longitude"]
                    lat2 = r["coordinates"]["point2"]["latitude"]
                    lon2 = r["coordinates"]["point2"]["longitude"]
                    if data["latitude"] >= min(lat1,lat2) and data["latitude"] <= max(lat1,lat2) and data["longtiude"] >= min(lon1,lon2) and data["longtiude"] <= max(lon1,lon2):
                        return jsonify(code=60,fence_id=r["id"])
                return jsonify(code=61)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=62)

class GetBooksInFence(Resource):
    '''
    method: POST
    params: fence_id
    return: code30: No books in fence
            code31: books
            code12: Incomplete/Invalid details
            code13: Unknown error 
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            res = db.books.find({"taken":False,"uploaded_by":{"$ne":data["firebase_id"]}})
            if res.count()==0:
                return jsonify(code=30,msg="No Books")
            else:
                books = []
                for r in res:
                    user = db.users.find_one({"firebase_id":r["uploaded_by"]})
                    if(user["fence_id"]==data["fence_id"]):
                        books.append({
                            "id":str(r["_id"]),
                            "authors":r["authors"],
                            "title":r["title"],
                            "price":r["price"],
                            "uploaded_on":r["uploaded_on"],
                            "pages":r["pages"],
                            "rating":r["avg_rating"],
                            "infoLink":r["google_link"],
                            "image":r["thumb_link"],
                            "uploaded_by":r["uploaded_by"],
                            "description":r["description"],
                            "taken":r["taken"],
                            "etag":r["etag"]
                        })
                return jsonify(code=31,books=books)
        except KeyError as e:
            return jsonify(msg=f"Incomplete details: {e}",code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=13)

class GetBooksByUser(Resource):
    '''
    method: POST
    params: firebase_id
    return: code30: No books
            code31: books
            code12: Incomplete/Invalid details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            res = db.books.find({"uploaded_by":data["firebase_id"]})
            if res.count()==0:
                return jsonify(code=30,msg="No Books")
            else:
                books = []
                for r in res:
                    books.append({
                        "id":str(r["_id"]),
                        "title":r["title"],
                        "authors":r["authors"],
                        "pages":r["pages"],
                        "uploaded_on":r["uploaded_on"],
                        "description":r["description"],
                        "avg_rating":r["avg_rating"],
                        "image":r["thumb_link"],
                        "google_link":r["google_link"],
                        "price":r["price"],
                        "uploaded_by":r["uploaded_by"],
                        "taken":r["taken"]})
                return jsonify(code=31,books=books)
        except KeyError as e:
            print(e)
            return jsonify(msg="Incomplete details",code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=13)

class GetListings(Resource):
    '''
    method: POST
    params: firebase_id
    return: code30: No books
            code31: books
            code12: Incomplete/Invalid details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            res = db.books.find({"uploaded_by":data["firebase_id"],"taken":False})
            if res.count()==0:
                return jsonify(code=30,msg="No Books")
            else:
                books = []
                for r in res:
                    books.append({
                        "id":str(r["_id"]),
                        "title":r["title"],
                        "authors":r["authors"],
                        "pages":r["pages"],
                        "uploaded_on":r["uploaded_on"],
                        "description":r["description"],
                        "avg_rating":r["avg_rating"],
                        "image":r["thumb_link"],
                        "google_link":r["google_link"],
                        "price":r["price"],
                        "uploaded_by":r["uploaded_by"],
                        "taken":r["taken"]})
                return jsonify(code=31,books=books)
        except KeyError as e:
            print(e)
            return jsonify(msg="Incomplete details",code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=13)

class GetExchanges(Resource):
    '''
    method: POST
    params: firebase_id
    return: code30: No books
            code31: books
            code12: Incomplete/Invalid details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            res = db.books.find({"uploaded_by":data["firebase_id"],"taken":True})
            if res.count()==0:
                return jsonify(code=30,msg="No Books")
            else:
                books = []
                for r in res:
                    books.append({
                        "id":str(r["_id"]),
                        "title":r["title"],
                        "authors":r["authors"],
                        "pages":r["pages"],
                        "uploaded_on":r["uploaded_on"],
                        "description":r["description"],
                        "avg_rating":r["avg_rating"],
                        "image":r["thumb_link"],
                        "google_link":r["google_link"],
                        "price":r["price"],
                        "uploaded_by":r["uploaded_by"],
                        "taken":r["taken"]})
                return jsonify(code=31,books=books)
        except KeyError as e:
            print(e)
            return jsonify(msg="Incomplete details",code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=13)

class Exchange(Resource):
    '''
    method: POST
    params: firebase_id, book_id
    return: code40: Successful
            code41: Failed
            code12: Incomplete/Invalid details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            book = db.books.find_one({f"_id":ObjectId(data["book_id"]),"taken":False})
            if book is not None:
                db.users.update_one({"firebase_id":data["firebase_id"]},{"$inc":{"exchanges":1,"coins":-book["price"]}})
                db.users.update_one({"firebase_id":book["uploaded_by"]},{"$inc":{"listings":-1,"exchanges":1,"coins":book["price"]}})
                db.books.update_one({f"_id":ObjectId(data["book_id"])},{"$set":{"taken":True}})
                return jsonify(code=40,msg="Successful!")
            else:
                return jsonify(code=41,msg="Book not found")
        except KeyError as e:
            return jsonify(code=12,msg=str(e))
        except Exception as e:
            return jsonify(code=13,msg=str(e))

class UpdatePhone(Resource):
    '''
    method: POST
    params: firebaseId,phone
    return: code70: successful
            code71: failed
            code12: Incomplete/Invalid details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            phn = data["phone"]
            res = db.users.update_one({"firebase_id":data["firebase_id"]},{"$set":{"phone":phn,"updated":True}})
            if res.acknowledged:
                return jsonify(code=70,msg="Done")
            else:
                return jsonify(code=71,msg="Failed")
        except KeyError as e:
            return jsonify(code=12,msg=str(e))
        except Exception as e:
            return jsonify(code=13,msg=str(e))






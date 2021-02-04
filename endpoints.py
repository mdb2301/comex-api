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
        try:
            r = db.users.insert_one({
                "name":data["name"],
                "firebase_id":data["firebase_id"],
                "email":data["email"],
                "date_joined":datetime.now().strftime("%d/%m/%Y %H:%M"),
                "fence_id":data["fence_id"],
                "updated":False,
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


import json
from flask import request,jsonify
from flask_restful import Resource
import pymongo
from datetime import datetime

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
        updated=r["updated"])
        

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
                "date_joined":datetime.now().timestamp(),
                "fence_id":data["fence_id"],
                "updated":False
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
                "name":data["name"],
                "authors":data["authors"],
                "pages":data["pages"],
                "description":data["description"],
                "avg_rating":data["avg_rating"],
                "thumb_link":data["thumb_link"],
                "google_link":data["google_link"],
                "price":data["price"],
                "uploaded_by":data["uploaded_by"],
                "taken":False
            })
            if r.acknowledged:
                print("Added")
                return jsonify(code=20)
            else:
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
            res = db.books.find({"taken":False})
            if res.count()==0:
                return jsonify(code=30,msg="No Books")
            else:
                books = []
                for r in res:
                    user = db.users.find_one({"firebase_id":r["uploaded_by"]})
                    if(user["fence_id"]==data["fence_id"]):
                        books.append(jsonify(
                            id=str(r["_id"]),
                            name=r["name"],
                            authors=r["authors"],
                            pages=r["pages"],
                            description=r["description"],
                            avg_rating=r["avg_rating"],
                            thumb_link=r["thumb_link"],
                            google_link=r["google_link"],
                            price=r["price"],
                            uploaded_by=r["uploaded_by"]))
                return jsonify(code=31,books=books)
        except KeyError:
            return jsonify(msg="Incomplete details",code=12)
        except Exception as e:
            print(e)
            return jsonify(msg="Unknown error",code=13)

class GetBooksByUser(Resource):
    '''
    method: POST
    params: fence_id
    return: code30: No books
            code31: books
            code12: Incomplete/Invalid details
            code13: Unknown error
    '''
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        try:
            res = db.users.find({"firebase_id":data["firebase_id"]})
            if res.count()==0:
                return jsonify(code=30,msg="No Books")
            else:
                books = []
                for r in res:
                    books.append({
                        "name":r["name"],
                        "authors":r["authors"],
                        "pages":r["pages"],
                        "description":r["description"],
                        "avg_rating":r["avg_rating"],
                        "thumb_link":r["thumb_link"],
                        "google_link":r["google_link"],
                        "price":r["price"],
                        "uploaded_by":r["uploaded_by"],
                        "taken":r["taken"]})
                return jsonify(code=31,books=books)
        except KeyError:
            return jsonify(msg="Incomplete details",code=12)
        except:
            return jsonify(msg="Unknown error",code=13)

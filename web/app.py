from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy 


app = Flask(__name__)
api = Api(app)


client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]

def userExist(username):
    
    if users.find({"Username":username}).count() == 0 :
        return False
    
    return True


def verifyPw(username, password):
    if not userExist(username):
        return False
    
    hashed_pw = users.find({"Username":username})[0]["Password"]

    if bcrypt.checkpw(password.encode("utf8"), hashed_pw):
        return True
    return False


def countTokens(username):
    num_tokens = users.find({"Username":username})[0]["Tokens"]
    return num_tokens


class Register(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData["username"]
        password = postedData["password"]

        if userExist(username):
            retJson = {
                "status":301,
                "msg":"Invalid Username"
            }
            return retJson

        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signedup to the API"
        }

        return jsonify(retJson)


class Detect(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData["username"]
        password = postedData["password"]

        text1 = postedData["text1"]

        text2 = postedData["text2"]

        if not userExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)

        correct_pw = verifyPw(username,password)

        if not correct_pw:
            retJson = {
                "status": 301,
                "msg": "Invalid Password"
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)

        if 0 >= num_tokens:
            retJson = {
                "status": 303,
                "msg": "You're out of tokens, please refill!"
            }
            return jsonify(retJson)
        
        #calculate the edit distance
        nlp = spacy.load("en_core_web_sm")

        text1 = nlp(text1)
        text2 = nlp(text2)

        #ratio is a number between 0 and 1 to check the similarity between 2 strings
        ratio = text1.similarity(text2)

        retJson = {
            "status": 200,
            "similarity": ratio,
            "msg": "Similarity Score calculated successfully!"
        }

        current_tokens = countTokens(username)

        users.update({
            "Username":username
        },{
            "$set":{
                "Tokens": current_tokens - 1
            }
        })

        return jsonify(retJson)

class Refil(Resource):
    def post(self):
        postedData = requests.get_json()

        username = postedData["username"]
        password = postedData["admin_pw"]
        refil_amount = postedData["refil"]


        if not userExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)

        #just for testing
        correct_pw = "asdjajs124sda"
        if not password == correct_pw:
            retJson = {
                "status": 304,
                "msg": "Invalid admin password !"
            }
            return jsonify(retJson)

        tokens = countTokens(username)

        users.update({
            "Username":username
        },{
            "$set":{
                "Tokens": tokens + refil_amount
            }
        })

        retJson = {
            "status": 200,
            "msg": "Refilled successfully!"
        }
        return jsonify(retJson)

api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")
api.add_resource(Refil, "/refil")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
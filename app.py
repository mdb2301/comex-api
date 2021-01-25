from flask import Flask
from flask_restful import Api
import endpoints

app = Flask(__name__)
app.config['SECRET_KEY']="secretkey"
api = Api(app)

api.add_resource(endpoints.GetUser,"/getuser")
api.add_resource(endpoints.AddUser,"/adduser")
api.add_resource(endpoints.AddBook,"/addbook")
api.add_resource(endpoints.GetBooksInFence,"/booksinfence")
api.add_resource(endpoints.GetBooksByUser,"/booksbyuser")

@app.route('/')
def index():
    return "<h1>Working</h1>"

if __name__ == "__main__":
    app.run(debug=True)
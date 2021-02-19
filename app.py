from flask import Flask,render_template
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
api.add_resource(endpoints.GetListings,"/listings")
api.add_resource(endpoints.GetExchanges,"/exchanges")
api.add_resource(endpoints.Exchange,"/exchange")
api.add_resource(endpoints.AddFence,"/addfence")
api.add_resource(endpoints.CheckFence,"/checkfence")
api.add_resource(endpoints.UpdatePhone,"/updatephone")
api.add_resource(endpoints.FetchFences,"/fetchfences")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
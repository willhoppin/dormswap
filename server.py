import logging
from datetime import date
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


DATABASEURI = "postgresql://dy2471:9989@34.75.94.195/proj1part2"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
 
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
  

  print(request.args)


  cursor = g.conn.execute("SELECT * FROM Items")
  items = []
  for result in cursor:
    items.append(result)
  cursor.close()

  context = dict(items = items)

  
  return render_template("index.html", **context, userName="")



@app.route('/createAccount')
def createAccount():
  return render_template("createAccount.html")

@app.route('/logIn')
def logIn():
  return redirect("/")

@app.route('/sortLikes/<user_id>')
def sortLikes(user_id):
  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    current_user = result
  nameCursor.close()

  cursor = g.conn.execute("SELECT * FROM Items ORDER BY likes DESC")
  items = []
  for result in cursor:
    items.append(result)
  cursor.close()
  context = dict(items = items)
  return render_template("index.html", **context, current_user=current_user, user_logged_in=True)

@app.route('/sortViews/<user_id>')
def sortViews(user_id):
  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    current_user = result
  nameCursor.close()

  cursor = g.conn.execute("SELECT * FROM Items ORDER BY views DESC")
  items = []
  for result in cursor:
    items.append(result)
  cursor.close()
  context = dict(items = items)
  return render_template("index.html", **context, current_user=current_user, user_logged_in=True)

@app.route('/sortReviews/<user_id>')
def sortReviews(user_id):
  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    current_user = result
  nameCursor.close()

  cursor = g.conn.execute("SELECT * FROM Items i, Deal d, Users u where i.item_id = d.item_id AND d.seller_id = u.user_id ORDER BY i.views DESC")
  items = []
  for result in cursor:
    items.append(result)
  cursor.close()
  context = dict(items = items)
  return render_template("index.html", **context, current_user=current_user, user_logged_in=True)

@app.route('/sortPrice/<user_id>')
def sortPrice(user_id):
  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    current_user = result
  nameCursor.close()

  items = []
  cursor = g.conn.execute("SELECT * FROM Items ORDER BY price DESC")
  for result in cursor:
    items.append(result)
  cursor.close()
  context = dict(items = items)
  return render_template("index.html", **context, current_user=current_user, user_logged_in=True)

@app.route('/sortSearch/<user_id>', methods=['POST'])
def sortSearch(user_id):
  name = request.form['name']
  namePercents = '%' + name + '%'

  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    current_user = result
  nameCursor.close()

  items = []
  cursor = g.conn.execute("SELECT * FROM Items WHERE item_name LIKE (%s)", namePercents)
  for result in cursor:
    items.append(result)
  cursor.close()
  context = dict(items = items)
  return render_template("index.html", **context, current_user=current_user, user_logged_in=True)

@app.route('/emailUser/<user_id>')
def emailUser(user_id):
  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    target_user = result
  nameCursor.close()
  mailto_link = 'mailto:' + target_user.email;
  return redirect(mailto_link)

@app.route('/accountCreator', methods=['POST'])
def accountCreator():
    
    username = request.form['username']
    email = request.form['email']
    address = request.form['address']
    venmo = request.form['venmo']
    photo = request.form['photo']
    user_idCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (SELECT MAX(user_id) FROM Users)")
    for result in user_idCursor:
      highest_id = result.user_id
    user_idCursor.close()
    userid = str(int(highest_id) + 1)
    college = "Columbia University"
    
    sql = "INSERT INTO Users (user_id,user_name,email,college,photo,address,venmo) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    val = (
      userid,
      username,
      email,
      college,
      photo,
      address,
      venmo
    )
    
    #POST this new user
    current_user = g.conn.execute(sql, val)

    #pull items if successful
    items = []
    cursor = g.conn.execute("SELECT * FROM Items")
    for result in cursor:
      items.append(result)
    cursor.close()
    context = dict(items = items)

    return render_template("index.html", **context, current_user=current_user, user_logged_in=True)

@app.route('/logInWInput', methods=['POST'])
def logInWInput():
    name = request.form['name']
    nameCursor = g.conn.execute("SELECT * FROM Users WHERE email = (%s)", name)
    count = 0
    current_user = []
    for result in nameCursor:
      count = count + 1
      current_user = result
    nameCursor.close()

    if (count == 1):
      redirectURL = '/loggedIn/' + current_user.user_id
      return redirect(redirectURL)
    else:
      #insert message about user not being able to log in
      return redirect('/')

@app.route('/loggedIn/<user_id>')
def loggedIn(user_id):
    #handle if no user
    if (user_id == ""):
      return redirect('/')
    
    nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
    current_user = []
    for result in nameCursor:
      current_user = result
    nameCursor.close()

    #pull items
    items = []
    cursor = g.conn.execute("SELECT * FROM Items")
    for result in cursor:
      items.append(result)
    cursor.close()
    context = dict(items = items)
    return render_template("index.html", **context, current_user=current_user, user_logged_in=True)

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()


"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import logging
from datetime import date
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://dy2471:9989@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
'''
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
'''

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM Items")
  items = []
  for result in cursor:
    items.append(result)
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(items = items)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context, userName="")

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

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
    today = date.today()
    print("Today's date:", today)
    createdat = today
    fullUserStr = '(' + userid + ',' + username + ',' + email + ',' + college + ',' + createdat + ',' + photo + ',' + address + ',' + venmo + ',1' + ')' 
    goodstr = '\'will@hoppin.net\''
    

    #POST this new user
    g.conn.execute('INSERT INTO Users (email) VALUES (%s)', goodstr)
    #g.conn.execute('INSERT INTO Users (email) VALUES (\'will@hoppin.net\')')
    
    '''
    #GET the user
    nameCursor = g.conn.execute("SELECT * FROM Users WHERE email = (%s)", email)
    current_user = []
    for result in nameCursor:
      current_user = result
    nameCursor.close()

    #pull items if successful
    
    '''

    items = []
    cursor = g.conn.execute("SELECT * FROM Items")
    for result in cursor:
      items.append(result)
    cursor.close()
    context = dict(items = items)

    current_user = [];

    return render_template("index.html", **context, current_user=current_user, user_logged_in=False)

@app.route('/loggedIn', methods=['POST'])
def loggedIn():
    name = request.form['name']
    nameCursor = g.conn.execute("SELECT * FROM Users WHERE email = (%s)", name)
    count = 0
    current_user = []
    for result in nameCursor:
      count = count + 1
      current_user = result
    nameCursor.close()

    user_logged_in = False

    if (count == 1):
      user_logged_in = True

    #pull items if successful
    items = []
    cursor = g.conn.execute("SELECT * FROM Items")
    for result in cursor:
      items.append(result)
    cursor.close()
    context = dict(items = items)
    return render_template("index.html", **context, current_user=current_user, user_logged_in=user_logged_in)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()

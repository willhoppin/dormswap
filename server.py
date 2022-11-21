import logging
import math
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from datetime import date
from imgurpython import ImgurClient
import os
import pathlib
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, send_from_directory, url_for, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'This is your secret key to utilize session in Flask'
client = ImgurClient('4924e300f8a2d4d', '3784cf8b2d17a159caa28c4c90c2966228f73998')

UPLOAD_FOLDER = os.path.join('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

imgurConfig = {
  'album': None,
  'name': 'Nameless',
  'title': 'DormSwapUpload',
  'description': 'NoDesc'
}

class UploadFileForm(FlaskForm):
  file = FileField("File")
  submit = SubmitField("Upload File")

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
  
  cursor = g.conn.execute("SELECT * FROM Items")
  items = []
  for result in cursor:
    items.append(result)
  cursor.close()

  context = dict(items = items)

  return render_template("index.html", **context, userName="")

@app.route('/createAccount', methods=['GET','POST'])
def createAccount():
  form = UploadFileForm()
  if form.validate_on_submit():
    uploaded_img = request.files['file']
    img_filename = secure_filename(uploaded_img.filename)
    uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
    session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
    img_file_path = session.get('uploaded_img_file_path', None)
    image = client.upload_from_path(img_file_path, config=imgurConfig, anon=False) #upload file to Imgur
    os.remove(img_file_path)
    
    return "Grabbed the file " + img_filename + " and uploaded to " + image['link']
  return render_template("createAccount.html", form=form)

@app.route('/messengerClient/<user_id>/<chat_id>', methods=['GET','POST'])
def messengerClient(user_id, chat_id):
  selected_chat = []
  other_user = []
  all_chats = []
  
  #GET the current user
  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    current_user = result
  nameCursor.close()

  #GET all relevant chats (involving current_user)
  allChatsCursor = g.conn.execute("SELECT * FROM Communicate WHERE buyer_id = (%s) OR seller_id = (%s)", user_id, user_id)
  for result in allChatsCursor:
    temp = []
    temp.append(result)

    #FIND the other user's ID
    if (result.buyer_id == user_id):
      other_chat_user_id = result.seller_id
    else:
      other_chat_user_id = result.buyer_id
    
    #GET all the data from that ID
    chatUserCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", other_chat_user_id)
    for result in chatUserCursor:
      other_chat_user = result
    chatUserCursor.close()

    #PACKAGE that in the temp variable
    temp.append(other_chat_user)

    #INCLUDE that in the all_chats variable
    all_chats.append(temp)
  allChatsCursor.close()

  #GET the chat ID if route specifies one
  if (chat_id != 'none'):
    chatCursor = g.conn.execute("SELECT * FROM Communicate WHERE chat_id = (%s)", chat_id)
    for result in chatCursor:
      current_chat = result
    chatCursor.close()

    messages = []
    messageCursor = g.conn.execute("SELECT * FROM Mess_send WHERE chat_id = (%s)", chat_id)
    for result in messageCursor:
      messages.append(result)
    messageCursor.close()
    
    #find the appropriate other user ID
    if (current_chat.buyer_id == current_user.user_id):
      other_user_id = current_chat.seller_id
    else:
      other_user_id = current_chat.buyer_id
        
    #GET the other user
    otherCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", other_user_id)
    for result in otherCursor:
      other_user = result
    otherCursor.close()

  return render_template("messengerClient.html", current_user=current_user, other_user=other_user, all_chats=all_chats)

@app.route('/newListing/<user_id>', methods=['GET','POST'])
def newListing(user_id):
  form = UploadFileForm()
  if form.validate_on_submit():
    uploaded_img = request.files['file']
    img_filename = secure_filename(uploaded_img.filename)
    uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
    session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
    img_file_path = session.get('uploaded_img_file_path', None)
    image = client.upload_from_path(img_file_path, config=imgurConfig, anon=False) #upload file to Imgur
    os.remove(img_file_path)
    
    return "Grabbed the file " + img_filename + " and uploaded to " + image['link']
  return render_template("newListing.html", form=form, user_id=user_id)

@app.route('/logIn')
def logIn():
  return redirect("/")

@app.route('/logInFailed')
def logInFailed():
  return render_template("logInFailed.html")

@app.route('/viewItem/<user_id>/<item_id>')
def viewItem(user_id, item_id):
  nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", user_id)
  for result in nameCursor:
    current_user = result
  nameCursor.close()

  itemCursor = g.conn.execute("SELECT * FROM Items WHERE item_id = (%s)", item_id)
  for result in itemCursor:
    current_item = result
  itemCursor.close()

  sellerCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", current_item.seller_id)
  for result in sellerCursor:
    current_seller = result
  sellerCursor.close()

  seller_rank = 0
  review_count = 0

  #pull histories, average them, floor them
  historyCursor = g.conn.execute("SELECT * FROM his_recorded WHERE user_id = (%s)", current_item.seller_id)
  for result in historyCursor:
    if (review_count == 0):
      seller_rank = result.grade
    else:
      seller_rank = ((seller_rank * review_count) + result.grade)/(review_count + 1)
    review_count = review_count + 1
  seller_rank = math.floor(seller_rank)
  sellerCursor.close()

  return render_template("viewItem.html", current_user=current_user, user_logged_in=True, current_item=current_item, current_seller=current_seller, seller_rank=seller_rank)

@app.route('/likeItem/<user_id>/<item_id>')
def likeItem(user_id, item_id):

  #find the item with the ID, increment the like
  g.conn.execute("UPDATE Items SET likes = likes + 1 WHERE item_id = (%s)", item_id)

  redirectURL = '/viewItem/' + user_id + '/' + item_id

  return redirect(redirectURL)

@app.route('/tallyViewItem/<user_id>/<item_id>')
def tallyViewItem(user_id, item_id):

  #find the item with the ID, increment the like
  g.conn.execute("UPDATE Items SET views = views + 1 WHERE item_id = (%s)", item_id)

  redirectURL = '/viewItem/' + user_id + '/' + item_id

  return redirect(redirectURL)

@app.route('/deleteItem/<user_id>/<item_id>')
def deleteItem(user_id, item_id):

  #find the item with the ID, increment the like
  g.conn.execute("DELETE FROM Items WHERE item_id = (%s)", item_id)

  redirectURL = '/loggedIn/' + user_id

  return redirect(redirectURL)

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

  #this needs work: complicated query
  cursor = g.conn.execute ("select i.item_name, i.item_id, i.views, i.likes, i.price, i.item_photo, u.user_name, avg(h.grade) from items i, deal d, users u, his_recorded h where i.item_id = d.item_id and d.seller_id = u.user_id and u.user_id = h.user_id group by i.price, i.item_name, u.user_name, i.item_photo, i.views, i.likes, i.item_id order by avg(h.grade) desc")
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
  cursor = g.conn.execute("SELECT * FROM Items WHERE UPPER(item_name) LIKE UPPER((%s)) OR UPPER(description) LIKE UPPER((%s))", namePercents, namePercents)
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
  mailto_link = 'mailto:' + target_user.email
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
    createdat = date.today()
    
    #POST this new user
    g.conn.execute("INSERT INTO Users(user_id,user_name,email,created_at,photo,address,venmo,favorite) VALUES ((%s), (%s), (%s), (%s), (%s), (%s), (%s), 0);",userid,username,email,createdat,photo,address,venmo)
    
    #GET this user
    nameCursor = g.conn.execute("SELECT * FROM Users WHERE user_id = (%s)", userid)
    for result in nameCursor:
      current_user = result
    nameCursor.close()

    redirectURL = '/loggedIn/' + current_user.user_id
    return redirect(redirectURL)

@app.route('/listingCreator/<user_id>', methods=['POST'])
def listingCreator(user_id):
    
    title = request.form['title']
    description = request.form['description']
    price = int(request.form['price'])
    photo = request.form['photo']
    seller_id = user_id
    likes = 0
    views = 0

    item_idCursor = g.conn.execute("SELECT * FROM Items WHERE item_id = (SELECT MAX(item_id) FROM Items)")
    for result in item_idCursor:
      highest_id = result.item_id
    item_idCursor.close()

    itemid = str(int(highest_id) + 1)

    #POST this new item
    g.conn.execute("INSERT INTO Items(item_id,item_name,description,price,item_photo,seller_id,likes,views) VALUES ((%s), (%s), (%s), (%s), (%s), (%s),(%s), (%s));",itemid,title,description,price,photo,seller_id,likes,views)

    redirectURL = '/loggedIn/' + user_id
    return redirect(redirectURL)

@app.route('/logInWInput', methods=['POST'])
def logInWInput():
    username = request.form['username']
    email = request.form['email']

    nameCursor = g.conn.execute("SELECT * FROM Users WHERE email = (%s)", email)
    count = 0
    current_user = []
    for result in nameCursor:
      count = count + 1
      current_user = result
    nameCursor.close()

    if ((count == 1) and (username == current_user.user_name)):
      redirectURL = '/loggedIn/' + current_user.user_id
      return redirect(redirectURL)
    else:
      #insert message about user not being able to log in
      return redirect('/logInFailed')

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

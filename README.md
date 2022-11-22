## COMS4111 Proj1 part3 - DormSwap
 ### PostgreSQL
 - psql -U dy2471 -h 34.75.94.195 -d proj1part2
 - id: dy2471, pw: 9989
 - The 'univ_name' column of the Users table has some unknown space, so we added the real 'univ_name' at the end of the Users table
 ### Web URL
 - http://127.0.0.1:8111/

 ### Description
 - Logging in with your Username and Email:
  If the Username and Email entered by the user do not match a Username and Email combination in the DB, the login will not be successful, and the user will be directed to a "login failed" template/route on the front end. If it is the first time this user is signing in the can route themselves to a "Create Account" page, where they fill in a form that results in them getting INSERTed into the User table, then "signing them in." As authorization was a complicated process, we store the current_user.user_id in the URL of the website for this version. The downside of this is that users can "log in" to other accounts by changing the URL. In the future, we hope to learn to encrypt and secure this information. Lastly, we implemented photos as including links that are already hosted on the internet elsewhere. We experimented with the Imgur Python package and the Imgur API, but were unable to get the correct information off of local computers to be able to store images locally, before uploading them. This is another feature we hope to implement with more time, as uploading images from one's computer is far more ergonomic than hosting it elsewhere and providing our website with a link.

 - After you log in, users can see all the items on the market. The user can search for whether the item they need is in the market or not by entering the item name in the search box at the top. This performs a simple LIKE query to find text matches in the name and description of items. Moreover, users can sort the items by likes, views, price, or the reviews of seller (which is a more complex query than the previous). If this item is in the DB, the user can view the item, which displays the seller's and item's information, including an average of the seller's ratings over time, pulled from the His_recorded table. Users can check the description, photo, price, views and likes on the item, as well as make an offer below it. Sending an initial offer starts a chat if it does not exist yet, and sends a message in that chat. These chats can be viewed in the messengerClient portal. If a user is interested in a specific item, you they mark the item they are interested in by clicking the heart icon, which likes it.

 - Lastly, all members can put their items on the market as sellers via a "New Listing" form, which collects item fields then makes an API call to post the item. Items that a user owns can also be deleted via a "delete" button on the "view item" page.

### Interesting Query
- The first page that requires an interesting query is the homepage. The query in question sorts the items by average reviews from the seller. This was difficult, as DISTINCT did not help us much after we joined fields from all the tables we needed values from: Deal, Users, Items, and His_recorded. While the rows were distinct, they were full of mixed tuples which did not guarantee that the SUMS of the rows were distinct (ie one item was only appended then included to one row of the database.) We solved this by writing the following query: 

  cursor = g.conn.execute ("select i.item_name, i.item_id, i.views, i.likes, i.price, i.item_photo, u.user_name, avg(h.grade) from items i, deal d, users u, his_recorded h where i.item_id = d.item_id and d.seller_id = u.user_id and u.user_id = h.user_id group by i.price, i.item_name, u.user_name, i.item_photo, i.views, i.likes, i.item_id order by avg(h.grade) desc")

- The second page which includes a complex query is the messenger. Given that messages and chats were stored in separate entities, we had to manually link these datatypes in python before being able to display the required information. More context on this is available within the /messengerClient route: line 106 in server.py

## COMS4111 Proj2
 ### Define User Type(with array & text)
 - cus_serv_type : (cs_id integer, personal info varchar(20) array[3], description text)  
 - We made a customer service table so we can get any feedback from anyone.
 - cs_id is the PRIMARY KEY for this table
 - personal_info has 3 varchar such as name, gender, phone no
 ### Create a Table
 - TABLE 'customer_service' was created by cus_serv_type, so we can find any feedback using keyword(such as bug, report, etc.)

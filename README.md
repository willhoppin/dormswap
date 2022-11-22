## COMS4111 Proj1 part3 - DormSwap
 ### PostgreSQL
 - psql -U dy2471 -h 34.75.94.195 -d proj1part2
 - id: dy2471, pw: 9989
 - The ' univ_name' column of the Users table has some unknown space, so we added the real 'univ_name' at the end of the Users table
 ### Web URL

 ### Description
 - Log in with your Username and Email. However, if the Username and Email entered by the user do not match the Username and Email in the DB, login will not be successful. If it is first time, through signing up, related information is created in Usertable and you can sign in.

 - After you log in, you can see all the items on the market. You can check whether the item you need is in the market or not by entering the item name in the search box at the top. If this item is in the DB, you can check the seller, other people's evaluation of the seller based on previous transaction history, You can check the information about the product posted by the seller and the number of views and likes on the item.

 - If you are interested in a specific item, you can mark the item you are interested in as 'Like' based on the search, and there is a function to send a message or to propose a price to the seller who owns the item.

 - At the same time, all members can put their items on the market as sellers.

## COMS4111 Proj2
 ### Define User Type(with array & text)
 - cus_serv_type : (cs_id integer, personal info varchar(20) array[3], description text)  
 - We made a customer service table so we can get any feedback from anyone.
 - cs_id is the PRIMARY KEY for this table
 - personal_info has 3 varchar such as name, gender, phone no
 ### Create a Table
 - TABLE 'customer_service' was created by cus_serv_type, so we can find any feedback using keyword(such as bug, report, etc.)

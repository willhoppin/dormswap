# dormswap
DormSwap web app

Using mockups from this Google Drive folder:
https://drive.google.com/drive/folders/1qEZi5TBoigyHdwvAe_1PvgqtJT1IOtV7?usp=share_link

The ' univ_name' column of the Users table has some unknown space, so we added the real 'univ_name' at the end of the Users table 

# Proj3
1. Define User Type(with array & text) 
cus_serv_type : (cs_id integer, personal info varchar(20) array[3], description text)
We made a customer service table so we can get any feedback from anyone. 
 - cs_id is the PRIMARY KEY for this table 
 - personal_info has 3 varchar such as name, gender, phone no
2. Create a Table
customer_service created by cus_serv_type, so we can find any feedback using keyword(such as bug, report, etc.)
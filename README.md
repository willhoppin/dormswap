# COMS4111 Proj1 part3 - DormSwap
 - The ' univ_name' column of the Users table has some unknown space, so we added the real 'univ_name' at the end of the Users table

# COMS4111 Proj2
1. Define User Type(with array & text)
cus_serv_type : (cs_id integer, personal info varchar(20) array[3], description text)
We made a customer service table so we can get any feedback from anyone.
 - cs_id is the PRIMARY KEY for this table
 - personal_info has 3 varchar such as name, gender, phone no
2. Create a Table
TABLE 'customer_service' was created by cus_serv_type, so we can find any feedback using keyword(such as bug, report, etc.)

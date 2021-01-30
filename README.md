# Hexa's Login Brouteforse

This script will broteforce to login in a given range for username with the "main.py". And will get the exam result of a successfully logged in users using the brouteforced credentials.


## Requuirements
1. postgresql
    > For multithreaded database operation
2. psycopg2
    > To communicate with postgresql using python
3. python3
4. Create the Database and Table
    > If you've setup different username and password for postgres don't forget to update the credentials in "main.py" and "get_results.py"
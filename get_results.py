from requests import Session as session
import re
from queue import Queue
import psycopg2
import threading
# https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04

db = psycopg2.connect(
    user = "iftakhar",
    password = "iftakhar123",
    database = "iftakhar",
    host = 'localhost',
    port = 5432
)
cursor = db.cursor()
# cursor.executescript(open("./create_exams_table.sql", 'r').read())
insert_query = f"INSERT INTO exams VALUES(%s, %s, %s, %s, to_date(%s, 'dd/mm/yyyy'), %s, %s);"


class FetchExamResults:
    RESPONSE = b""
    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/5.0'
    }

    ENROLLED_TEST_REXP = re.compile(rb"Test Enrolled[\w\W]*?<label  class=\"form-control\" >(\d+)</label>")
    RESULT_REXP = re.compile(rb"<tr>[\s]*<td>(.*?)</td>[\s]*<td>(.*?)</td>[\s]*<td>(.*?)</td>[\s]*<td>(.*?)</td>[\s]*<td>(.*?)</td>[\s]*<td>(.*?)</td>[\s]*</tr>")

    RESULT_URL = "http://appsznd.hexaszindabazar.com/php_action/fetchresultpartial.php"
    LOGOUT_URL = "http://appsznd.hexaszindabazar.com/logout.php"
    LOGIN_URL = "http://appsznd.hexaszindabazar.com/index.php"
    LOGIN_DATA = {
        'user_name': 'HZ00000',
        'password': 'AS00'
    }

    ENROLLED_EXAMS = 0
    EXAMS = [(b'examid', b'version', b'date', b'type', b'module', b'score')]

    def __init__(self, user_id, password):
        self.LOGIN_DATA['user_name'] = user_id
        self.LOGIN_DATA['password'] = password
        self.BROWSER = session()
        self.login()
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.__class__.__name__}({self.LOGIN_DATA})"
    
    def __iter__(self):
        return self
    
    def __next__(self):
        for match in self.EXAMS:
            result = match.groups()
            result = {
                'examid': result[0].decode('utf-8'),
                'version': int(result[1].decode('utf-8')),
                'score': float(result[5].decode('utf-8')),
                'date': result[2].decode('utf-8'),
                'type': result[3].decode('utf-8'),
                'module': result[4].decode('utf-8'),
            }
            return result
        else:
            raise StopIteration
    
    def fetch_exam_results(self):
        self.RESPONSE = self.BROWSER.post(self.RESULT_URL)
        self.EXAMS = self.RESULT_REXP.finditer(self.RESPONSE.content)
    
    def get_enrolled_exam_number(self):
        return self.ENROLLED_EXAMS
    
    def login(self):
        self.RESPONSE = self.BROWSER.post(self.LOGIN_URL, headers=self.REQUEST_HEADERS, data=self.LOGIN_DATA)
        # response = self.BROWSER.post(self.LOGIN_URL, headers=self.REQUEST_HEADERS, data=self.LOGIN_DATA)
        enrolled = self.ENROLLED_TEST_REXP.search(self.RESPONSE.content)

        if enrolled:
            enrolled = int(enrolled.group(1))
        else:
            print(self.RESPONSE.content)
            enrolled = 0
        self.ENROLLED_EXAMS = enrolled
        
        if self.ENROLLED_EXAMS>0:
            self.fetch_exam_results()
        else:
            self.EXAMS = []
    
    def logout(self):
        self.BROWSER.get(self.LOGOUT_URL)


def save_result(user_id, password):
    browser = FetchExamResults(user_id, password)
    for exam in browser:
        data = (user_id, *exam.values())
        cursor.execute(insert_query, data)
        print(f"Done {user_id}")

def start_queue(queue: Queue):
    while not queue.empty():
        thread = queue.get()
        thread.start()
        thread.join()
    queue.task_done()

def main(max_threads=300):
    concurent_threads = max_threads
    queues_for_threads = [Queue() for i in range(concurent_threads)]

    # query the db to get credentials
    select_statement = "SELECT id, pass from credentials;"
    cursor.execute(select_statement)

    for credential in cursor:
        user_num = int(credential[0][2:])
        thread = threading.Thread(target=save_result, args=credential, daemon=True)
        queues_for_threads[user_num%concurent_threads].put(thread)
    
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

main(200)

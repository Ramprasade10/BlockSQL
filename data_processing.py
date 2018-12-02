from flask import Flask,g,render_template, request,redirect,url_for,flash,session
import sqlite3,datetime
import itertools
from time import sleep
import portal
from tabula import read_pdf
from passlib.hash import sha256_crypt
from datetime import datetime
app = Flask(__name__)
setup_table_sql='setup_table.sql'
DATABASE = 'portal.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query):
    cur = get_db()
    cur.execute(query)
    cur.commit()
    # cur.close()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(setup_table_sql, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
@app.route('/init')
def init_route():
    init_db()
    return 'DB Initialised'

@app.route('/wrangle', methods=['POST', 'GET'])
def wrangle_course_details():
    #finalized
    df_me=[]
    df_me.append(read_pdf("static\\course_data\\mechanical_odd.pdf",pages="1",area=(379.353,43.602,684.74,631.016),spreadsheet=True))
    df_me.append(read_pdf("static\\course_data\\mechanical_odd.pdf",pages="4",area=(391.458,74.4,634.117,631.827),spreadsheet=True))
    df_me.append(read_pdf("static\\course_data\\mechanical_odd.pdf",pages="7",area=(463.3,50.284,790.604,630.838),spreadsheet=True))
    # edit the area section
    df_first=read_pdf("static\\course_data\\first_year.pdf",pages="11",spreadsheet=True,multiple_tables=True)
# branch=['ME','EC','EE','CS','CV','IP']
    sub_code=[]
    sub_title=[]
    sub_credits=[]
    for frame in df_me:
        section=frame[['Sub Code',"Sub. Title","Credits"]].dropna()
        sub_code.append(list(section["Sub Code"]))
        sub_title.append(list(section["Sub. Title"]))
        sub_credits.append(list(section["Credits"]))
    section=df_first[1][[0,1,2]]
    sub_code.append(list(section[0][1:]))
    sub_title.append(list(section[1][1:]))
    sub_credits.append(list(section[2][1:]))
    sub_code=list(itertools.chain.from_iterable(sub_code))
    sub_title=list(itertools.chain.from_iterable(sub_title))
    sub_credits=list(itertools.chain.from_iterable(sub_credits))
        
    for course_code,course_name,credit in zip(sub_code,sub_title,sub_credits):
        query=query_db('select course_code from course where course_code="'+course_code+'"')
        if not query:
            course_query='insert into course values("'+str(course_code)+'","'+str(course_name)+'","'+str(credit)+'");'
            print("added row")
            execute_db(course_query)
    print("done")
def prevhash(table):
        # sql=query_db('select block_hash from '+session.get('oper_table')+' order by time_stamp desc limit 0,1')[0] if table=="" else query_db('select block_hash from '+table+' order by time_stamp desc limit 0,1')[0]
        # if occasion="processing":
        sql=query_db('select block_hash from '+table+' order by time_stamp desc limit 0,1')[0]
        print(sql)
        if(sql["block_hash"]):
            print(sql["block_hash"])
            return(sql["block_hash"])
        # if sql["block_hash"] is None:
        else:
            return("0")
#Done
def blockhash(values,prev_hash=""):
    concat=""
    for x in values:
        concat+=str(x)
    concat+=prev_hash+"SKj8UijHObbb77hbll78Hv"
    # print(concat)
    return(sha256_crypt.hash(concat))
    #for students add this is asc of usn number
    #for marks table order in asc of semesters and (asc order of usn nested)
@app.route('/add_blockchain_info/<table>', methods=['POST', 'GET'])
def add_blockchain_info(table=None):
    if table=="student_details":
        for usn in range(1,13):
            encr=str(usn)
            pwd=sha256_crypt.hash(encr)
            tst=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            prev_block_hash=prevhash("student_details")                     
            execute_db('update student_details set prev_block_hash="'+prev_block_hash+'", pwd="'+pwd+'" where usn="'+str(usn)+'"')
            execute_db('update student_details set time_stamp="'+tst+'" where usn="'+str(usn)+'"')
            data=query_db('select * from student_details where usn="'+str(usn)+'"')[0]
            block_hash=blockhash(data.values())
            execute_db('update student_details set block_hash="'+block_hash+'" where usn="'+str(usn)+'"')
        print("Updated student_details")
    if table=="marks":
        for sem in range(1,9):
            for usn in range(1,11):
                data=query_db('select * from marks where usn="'+str(usn)+'" and sem="'+str(sem)+'"')
                if data:
                    for course in data:
                        tst=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')            
                        prev_block_hash=prevhash("marks")      
                        course_code=course["course_code"]
                        result_type=course["result_type"]
                        execute_db('update marks set prev_block_hash="'+prev_block_hash+'" where usn="'+str(usn)+'" and sem="'+str(sem)+'" \
                        and course_code="'+course_code+'" and result_type="'+result_type+'"')
                        execute_db('update marks set time_stamp="'+tst+'" where usn="'+str(usn)+'" and sem="'+str(sem)+'" \
                        and course_code="'+course_code+'" and result_type="'+result_type+'"')                          
                        course_data=query_db('select * from marks where usn="'+str(usn)+'" and sem="'+str(sem)+'" and \
                        course_code="'+course_code+'" and result_type="'+result_type+'"')[0]                          
                        block_hash=blockhash(course_data.values())
                        execute_db('update marks set block_hash="'+block_hash+'" where usn="'+str(usn)+'" and sem="'+str(sem)+'" \
                        and course_code="'+course_code+'" and result_type="'+result_type+'"')
                        sleep(0.1)

@app.route('/check', methods=['POST', 'GET'])
def check():
    data=[]
    tst=query_db('select time_stamp from marks')
    print(tst)
    for row in tst:
        data.append(row["time_stamp"])
    sdata=list(set(data))
    print(list(item for item in sdata if item not in data))
    print(len(data))
    print(len(sdata))

@app.route('/pwd_database', methods=['POST', 'GET'])
def pwd_database():
        admin_details=query_db('select * from database_admin')
        for admin in admin_details:
            admin_id=admin["admin_id"]  
            pwd=sha256_crypt.hash(admin_id)
            execute_db('update database_admin set pwd="'+pwd+'" where admin_id="'+str(admin_id)+'"')
        
        teacher_details=query_db('select * from teacher_details')
        for teacher in teacher_details:
            teacher_id=teacher["teacher_id"] 
            pwd=sha256_crypt.hash(teacher_id)
            execute_db('update teacher_details set pwd="'+pwd+'" where teacher_id="'+str(teacher_id)+'"')
def radomize_marks():
    #randomize within a range
     for usn in range(1,11):
            for sem in range(1,9):
                marks=query_db('select int1,int2,int3,cie,see,total_marks from marks where usn="'+usn+'" and sem="'+sem+'"')
                for course in marks:
                    if len(course):
                        course_code=course["course_code"]
                        int1=course["int1"]
                        int2=course["int2"]
                        int3=course["int3"]
                        #logic to add random value and also remain in the same grade
                        #modify int1-3 iteslf
                        cie=course["cie"]
                        total_marks=course["total_marks"]
                        see=course["see"]
                        execute_db('update marks int1="'+int1+'" and int2="'+int2+'" and int3="'+int3+'" where course_code="'+course_code+'"')
                    else:
                        break

if __name__ == "__main__":
    # app.secret_key = 'qslkjJjhkNBkjhhJkUJjkjsds'
    app.config['SESSION_TYPE'] = 'filesystem'
    # setup_table()
    
    app.run(host='127.0.0.1', port=8000, debug=True,threaded=True)

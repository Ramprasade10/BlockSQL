from flask import Flask,g,render_template, request,redirect,url_for,flash,session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sqlite3,hashlib,os,smtplib,datetime,pdfkit,PyPDF2,os
from pathlib import Path
from werkzeug.utils import secure_filename
from shutil import move
from passlib.hash import sha256_crypt
from datetime import datetime
import provisional_html_generate,transcript_html_generate
from io import StringIO,BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import base64,matplotlib.pyplot as plt 
import numpy as np,pandas as pd
app = Flask(__name__)
UPLOAD_FOLDER_QUESTION = os.path.join(os.getcwd(),'Question papers')
ALLOWED_EXTENSIONS_QUESTION = set(['txt', 'pdf', 'png', 'jpg', 'jpeg','dox','docx'])
UPLOAD_FOLDER_STUDENT = os.path.join(os.getcwd(),'static','images')
ALLOWED_EXTENSIONS_STUDENT = set(['png', 'jpg', 'jpeg'])
DATABASE = 'portal.db'
FIRST_RUN = 'schema.sql'
block_part=' order by time_stamp desc limit 0,1'
latest_result=' group by course_code order by time_stamp desc limit 0,1'
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

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(FIRST_RUN, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    # print(rv)
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query):
    cur = get_db()
    cur.execute(query)
    cur.commit()
    cur.close()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.route('/init')
def init_route():
    init_db()
    return 'DB Initialised'
#Works
@app.route('/check_integrity', methods=['POST', 'GET'])
def check_integrity():
    if request.method=='POST':
        tables=["student_details","marks"]
        integrity={"student_details":[],"marks":[]}
        for table in tables:
            row_count=int(str((query_db('select count(*) from '+table)[0]['count(*)'])))
            data=query_db('select * from '+table+' order by time_stamp asc')
        # col=query_db('pragma table_info("student_details")')
            col_count=len(data[0])
            print(col_count)
            #change row count********
            for row in range(0,10):
                values=""
            #excludes hash column
            # for col in range(0,col_count-1):
                key_no=0
                for key,val in data[row].items():
                    key_no+=1
                    if key_no < col_count:
                        values+=str(val)
                    #  select strftime("%Y-%m-%d %H:%M:%f", "now") 
                values+="SKj8UijHObbb77hbll78Hv"
                # block_hash=sha256_crypt.encrypt(values)
                db_block_hash=data[row]["block_hash"]
                print(values)
                print(db_block_hash)
                if sha256_crypt.verify(values,db_block_hash):
                    print("verified0")
                else:
                    integrity[table].append(row+1)
                    print("not verified0")

            for row in range(0,row_count-1):
                db_cur_hash=data[row]["block_hash"]
                db_next_hash=data[row+1]["prev_block_hash"]
                print(db_cur_hash)
                print(db_next_hash)
                if db_cur_hash == db_next_hash:
                    print("verified1")
                else:
                    integrity[table].append(row+1)
                    print("notverified1")
        err="Database Integrity Lost\n"
        for hash_err_table in tables:
                err+='\nTable:'+hash_err_table+"\n Row:"
                for row in integrity[hash_err_table]:
                    err+=str(row)+", "
        print(err)
        if integrity["student_details"] or  integrity["marks"]:
            sendmail("portalnie@gmail.com","Data Integrity Lost",err,"")
            return render_template("check_integrity.html",integrity=err)
        else:
            return render_template("check_integrity.html",integrity="Database Integrity is Maintained")
    return render_template("check_integrity.html")

    print(err)
# Works
def index_view():
    
    with app.app_context():
        db = get_db()
        index_view_transaction='BEGIN TRANSACTION;'
        index_view_transaction+='create index if not exists student on student_details(usn);'
        index_view_transaction+='create index if not exists teacher on teacher_details(teacher_id);'
        index_view_transaction+='create index if not exists admin on database_admin (admin_id);'
        index_view_transaction+='create view if not exists ledger as select * from login_ledger order by log_in desc;'
        index_view_transaction+='COMMIT;'
        db.cursor().executescript(index_view_transaction)
        db.commit()
@app.route('/student_sgpa', methods=['POST', 'GET'])
def student_sgpa():
    img = BytesIO()
    label = ["sgpa1","sgpa2","sgpa3","sgpa4","sgpa5","sgpa6","sgpa7","sgpa8"]
    sql=query_db('select sgpa1,sgpa2,sgpa3,sgpa4,sgpa5,sgpa6,sgpa7,sgpa8 \
    from student_details where usn="'+session.get('usn')+'"'+block_part)[0]
    sgpa=sql.values()
    index = np.arange(1,9)
    plt.bar(index, sgpa)
    plt.xlabel('Semesters')
    plt.ylabel('SPGA')
    plt.xticks(index, label)
    plt.title('Semester Wise GPA')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue())
    plt.clf()
    return render_template('student_sgpa.html', plot_url=plot_url.decode('utf8'))

@app.route('/student_internal', methods=['POST', 'GET'])
def student_internal():
    if request.method == 'POST':
        img = BytesIO()
        t = [1,2,3]
        marks_only=query_db('select course_code,int1,int2,int3 from marks \
        where usn="'+session.get('usn')+'" and sem="'+request.form['sem']+'"')
        marks=combine_table_results(marks_only,"internal")
        for row in marks:
            sub_marks=[row["int1"],row["int2"],row["int3"]]
            plt.plot(t,sub_marks,marker='o',label=row["course_code"])
        plt.xlabel('Internal')
        plt.ylabel('Marks')
        plt.title('Course Wise Internals Marks Comparison')
        plt.legend()
        plt.grid(True)
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue())
        plt.clf()
        return render_template('student_internal.html', plot_url=plot_url.decode('utf8'))   
    return render_template('student_internal.html')

#Works   
@app.route('/', methods=['POST', 'GET'])
def login():
    index_view()
    if request.method == 'POST':
        table_sel={"student":"student_details","teacher":"teacher_details","admin":"database_admin"}
        table=table_sel[request.form["user"]]
        login_student=str(request.form['usn'])+'s'
        session['user_type']=request.form["user"]
        session['table']=table
        if table=="student_details":
            sql = 'select usn,pwd from '+table+' where usn="'+request.form["usn"]+'"'+block_part

            rows=query_db(sql)
            num_rows=len(rows)
            print("instudent")
            # print(session[request.form['usn']])
            '''print(request.form.items())
            for x in request.form.values():
                print(x)'''
            if num_rows>0 and rows[0]["usn"]==request.form['usn'] and sha256_crypt.verify(request.form['password'],rows[0]["pwd"]):
                print("verified")
                session['usn']=request.form['usn']
                if session.get(login_student) is not None:
                    session[login_student]=0
                return redirect(url_for("students_portal"))
            else:
                if session.get(login_student) is not None:
                    session[login_student]+=1
                    print(session[login_student])
                    if session[login_student]>=3:
                        now = datetime.now()
                        print("greater than 3 mail sent")
                        email=query_db('select email from student_details where usn="'+request.form['usn']+'"'+block_part)[0]["email"]
                        sendmail(email,"Failed attempts to login into students portal","Someone tried accessing your account at "+now.strftime("%Y-%m-%d %H:%M")+"\n Regards, \n Database Administrator","")
                else:
                    session[login_student]=1
                    print("first time %s" %session[login_student])
                        

                return render_template("login.html",verification="Enter a valid Username or Password")
        elif table=="teacher_details":
            sql='select teacher_id,pwd from '+table+' where teacher_id="'+request.form["usn"]+'"'
            login_teacher=str(request.form['usn'])+'t'
            rows=query_db(sql)
            num_rows=len(rows)
            print("inteacher")
            if num_rows>0 and rows[0]["teacher_id"]==request.form['usn'] and sha256_crypt.verify(request.form['password'],rows[0]["pwd"]):
                session['teacher_id']=request.form['usn']
                if session.get(login_teacher) is not None:
                    session[login_teacher]=0
                return redirect(url_for("teachers_portal"))
            else:
                if session.get(login_teacher) is not None:
                    session[login_teacher]+=1
                    print(session[login_teacher])
                    if session[login_teacher]>=3:
                        now = datetime.datetime.now()
                        print("greater than 3 mail sent")
                        email=query_db('select email from teacher_details where usn="'+request.form['usn']+'"')[0]["email"]
                        sendmail(email,"Failed attempts to login into students portal","Someone tried accessing your account at "+now.strftime("%Y-%m-%d %H:%M")+"\n Regards, \n Database Administrator","")
                else:
                    session[login_teacher]=1
                    print("first time %s" %session[login_teacher])
                return render_template("login.html",verification="Enter a valid Username or Password")

        elif table=="database_admin":
            sql='select admin_id,pwd from '+table+' where admin_id="'+request.form["usn"]+'"'
            login_admin=str(request.form['usn'])+'a'
            rows=query_db(sql)[0]
            num_rows=len(rows)
            if num_rows>0 and rows["admin_id"]==request.form['usn'] and sha256_crypt.verify(request.form['password'],rows["pwd"]):
                session['admin_id']=request.form['usn']
                time=' select strftime("%Y-%m-%d %H:%M:%f", "now") '
                log_in=query_db(time)[0]['strftime("%Y-%m-%d %H:%M:%f", "now")']
                print(log_in)
                session['log_in']=log_in
                ledger='insert into login_ledger values("'+request.form['usn']+'","'+session.get("user_type")+'","'+log_in+'",NULL);'                
                execute_db(ledger)
                return redirect(url_for("ledger"))       
            else:
                if session.get(login_admin) is not None:
                    session[login_admin]+=1
                    print(session[login_admin])
                    if session[login_admin]>=3:
                        now = datetime.datetime.now()
                        print("greater than 3 mail sent")
                        email=query_db('select email from database_admin where admin_id="'+request.form['usn']+'"')[0]["email"]
                        sendmail(email,"Failed attempts to login into students portal","Someone tried accessing your account at "+now.strftime("%Y-%m-%d %H:%M")+"\n Regards, \n Database Administrator","")
                else:
                    session[login_admin]=1
                    print("first time %s" %session[login_admin])
                return render_template("login.html",verification="Enter a valid Username or Password")
        else:
            return render_template("login.html")
    else:
        if session.get('usn'):
            sql='update login_ledger set log_out=( select strftime("%Y-%m-%d %H:%M:%f", "now") ) where usn="'+session.get('usn')+'" and user_type="'+session.get('user_type')+'"'
            execute_db(sql)
            session.pop('usn', None)
        elif session.get('teacher_id'):
            sql='update login_ledger set log_out=( select strftime("%Y-%m-%d %H:%M:%f", "now") ) where usn="'+session.get('teacher_id')+'" and user_type="'+session.get('user_type')+'"'
            execute_db(sql)
            session.pop('teacher_id', None)
        elif session.get('admin_id'):
            sql='update login_ledger set log_out=( select strftime("%Y-%m-%d %H:%M:%f", "now") ) where usn="'+session.get('admin_id')+'" and user_type="'+session.get('user_type')+'"'
            execute_db(sql)            
            session.pop('admin_id', None)
        else:
            pass
        return render_template("login.html")
# Works
@app.route('/students_portal', methods=['POST', 'GET'])
def students_portal():
    if session.get("usn"):    
        usn=session.get("usn")
        table=session.get('table')
        sql = query_db('select counselor_teacher_id,student_name,year_start,year_end,usn,sem,section,branch,phone_no,email from '+table+' where usn="'+usn+'"'+block_part)
        counselor_id=sql[0]["counselor_teacher_id"]
        counselor_name=query_db('select teacher_name from teacher_details where teacher_id in(select counselor_teacher_id from student_details where counselor_teacher_id="'+counselor_id+'")')[0]["teacher_name"]
        rows=sql
        time=' select strftime("%Y-%m-%d %H:%M:%f", "now") '
        log_in=query_db(time)[0]['strftime("%Y-%m-%d %H:%M:%f", "now")']
        session['log_in']=log_in
        ledger='insert into login_ledger values("'+usn+'","'+session.get("user_type")+'","'+log_in+'",NULL);'
        execute_db(ledger)
        return render_template("students_portal.html"\
        ,details=rows[0],counselor_name=counselor_name)
# Works
@app.route('/login_ledger', methods=['POST', 'GET'])
def login_ledger():
        sql='select * from ledger'
        rows=query_db(sql)
        return render_template("login_ledger.html",rows=rows)

# Works
@app.route('/execute_query', methods=['POST', 'GET'])
def execute_query():
        if request.method=='POST':
            sql = request.form['query']
            commands=set(['update','insert'])
            phrase=set(sql.lower().split())
            if commands.intersection(phrase):
                execute_db(sql)
                return render_template("execute_query.html")
            else: 
                rows=query_db(sql)
                return render_template("execute_query.html",rows=rows)
        return render_template("execute_query.html")

#Works, uncomment mailing
@app.route('/teachers_portal', methods=['POST', 'GET'])
def teachers_portal():
    if session.get("teacher_id"):
        teacher_id=session.get('teacher_id')
        table=session.get('table')
        sql = 'select teacher_id ,teacher_name,branch,designation,email,phone_no,doj from '+table+' where teacher_id="'+teacher_id+'"'
        rows=query_db(sql)[0]
        time=' select strftime("%Y-%m-%d %H:%M:%f", "now") '
        log_in=query_db(time)[0]['strftime("%Y-%m-%d %H:%M:%f", "now")']
        session['log_in']=log_in
        ledger='insert into login_ledger values("'+teacher_id+'","'+session.get("user_type")+'","'+log_in+'",NULL);'
        execute_db(ledger)        
        #uncomment below line with a email that belongs to the tester
        #sendmail(rows["email"],"Activity on Teachers Portal","Your account was last accessed at"+now.strftime("%Y-%m-%d %H:%M")+"\n Regards, \n Database Administrator","")

        return render_template('teachers_portal.html',details=rows)

@app.route('/update_student_details', methods=['POST', 'GET'])
def update_student_details():
        if request.method=='POST':
            form_val=(request.form.to_dict())
            old_row=query_db('select * from student_details where usn="'+str(session.get('usn'))+'"'+block_part)[0]
            print(old_row.items())
            print(form_val.items())
                     
            if old_row:
                for old_vals in old_row.items():
                    for new_vals in form_val.items():
                        if (old_vals[0] != 'prev_block_hash') and (old_vals[0] != 'block_hash') and (old_vals[0] != 'time_stamp') and (old_vals[0] != 'pwd') :
                            print(str(old_vals[0])+'old:'+str(old_vals[1]))
                            print(str(new_vals[0])+'new:'+str(new_vals[1]))
                            if old_vals[0] == new_vals[0]:
                                if new_vals[1]:    
                                    print("changed from"+old_vals[0])    
                                    old_row[old_vals[0]]=new_vals[1]
                                    print("changed to"+old_vals[0])          
            
                tst=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                prev_block_hash=prevhash("student_details")
                if request.form['pwd']:
                    old_row["pwd"]=sha256_crypt.hash(form_val["pwd"])
                old_row["time_stamp"]=tst
                old_row["prev_block_hash"]=prev_block_hash
                block_hash=blockhash(old_row.values())
                old_row["block_hash"]=block_hash        
                sql='insert into student_details values('            
                count=len(old_row)
                col=0
                for key,value in old_row.items():
                    col+=1
                    if col is not count:
                        sql+='"'+str(value)+'", '
                    else:
                        sql+='"'+str(value)+'") '
                execute_db(sql)

                return render_template("update_student_details.html",message="Updation Sucessful")
            else:
                return render_template("update_student_details.html",message="No record found with matching data to update, please re check")

        return render_template("update_student_details.html")


@app.route('/update_student_marks', methods=['POST', 'GET'])
def update_student_marks():
        if request.method=='POST':
            form_val=(request.form.to_dict())

            if not request.form['course_code'] or not request.form['usn'] or not request.form['sem']:
                return render_template("update_student_marks.html",message="Enter all required fields")  
            
            sem=request.form['sem']
            course_code=str(request.form['course_code'])
            result_type=str(request.form['result_type'])
            # result_year=request.form['result_year']
            usn=request.form['usn']   
            print(course_code)
            print(result_type)
            old_row=query_db('select * from marks where usn="'+str(usn)+'" and sem="'+sem+'" and course_code="'+course_code+'" and result_type="'+result_type+'"'+block_part)[0]
                     
            if old_row:
                for old_vals in old_row.items():
                    for new_vals in form_val.items():
                        if (old_vals[0] != 'prev_block_hash') and (old_vals[0] != 'block_hash') and (old_vals[0] != 'time_stamp'):
                            print(str(old_vals[0])+'old:'+str(old_vals[1]))
                            print(str(new_vals[0])+'new:'+str(new_vals[1]))
                            if old_vals[0] == new_vals[0]:
                                # if (str(value_form) is not str(value_old)):
                                if new_vals[1]:    
                                    print("changed from"+old_vals[0])    
                                    old_row[old_vals[0]]=new_vals[1]
                                    print("changed to"+old_vals[0])          
            
                tst=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                prev_block_hash=prevhash("marks")
                old_row["time_stamp"]=tst
                old_row["prev_block_hash"]=prev_block_hash
                block_hash=blockhash(old_row.values())
                old_row["block_hash"]=block_hash        
                # add_new_row=execute_db('insert into marks select * from marks where usn="'+str(usn)+' and course_code="'+course_code+'" and result_type="'+result_type+'"')
                sql='insert into marks values('            
                count=len(old_row)
                col=0
                for key,value in old_row.items():
                    col+=1
                    if col is not count:
                        sql+='"'+str(value)+'", '
                    else:
                        sql+='"'+str(value)+'") '
                execute_db(sql)

                return render_template("update_student_marks.html",message="Updation Sucessful")
            else:
                return render_template("update_student_marks.html",message="No record found with matching data to update, please re check")

        return render_template("update_student_marks.html")

#Works
@app.route('/insert_student_marks', methods=['POST', 'GET'])
def insert_student_marks():
    if request.method=="POST":
        form_val=(request.form.to_dict())
        if not request.form["sem"] or not request.form["course_code"] or not request.form["result_type"] or not request.form["result_year"] or not request.form["usn"]:
            return render_template("insert_student_details",message="Enter all fields")                
        grade_gradepoint_dict={"S":"10","A":"9","B":"8","C":"7","D":"5","E":"4","F":"0","PP":"1","NP":"0"}
        #Compulsory inputs
        sem=request.form['sem']
        course_code=request.form['course_code']
        result_type=request.form['result_type']
        result_year=request.form['result_year']
        usn=request.form['usn']
        branch=query_db('select branch from student_details where usn="'+usn+'"')[0]["branch"]
        section=query_db('select section from student_details where usn="'+usn+'"')[0]["section"]
        credit=query_db('select credits from course where course_code="'+request.form['course_code']+'"')[0]["credits"]
               
        grade_point=""
        grade=""
        see=""
        grade_point=""
        total_marks=""

        int1=int(request.form['int1']) 
        int2=int(request.form['int2']) 
        int3=int(request.form['int3']) 
        see=int(request.form["see"])
        
        marks=[int1,int2,int3]
        marks.sort()
        cie=marks[2]+marks[1]

        if course_code is not "HS0001" or course_code is not "HS0002":
                if cie<25:
                    grade="W"
                    grade_point=grade_gradepoint_dict[grade]
                    see=total_marks=0
                else:
                    see=int(request.form['see'])
                    total_marks=((see/2)+cie)
                    print(total_marks)
                    print(type(total_marks))
                    if total_marks>=90.0 and total_marks<=100.0:
                        grade="S"
                    elif total_marks>=75.0 and total_marks<=89.0:
                        grade="A"
                    elif total_marks>=60.0 and total_marks<=74.0:
                        grade="B"
                    elif total_marks>=50.0 and total_marks<=59.0:
                        grade="C"
                    elif total_marks>= 45.0 and total_marks<=49.0:
                        grade="D"
                    elif total_marks >= 40.0 and total_marks<=45.0:
                        grade="E"
                    else:
                        grade="F"
                    grade_point=grade_gradepoint_dict[grade]

        if (course_code is "HS0001") or (course_code is "HS0002"):
                if cie<25:
                    grade="NP"
                    grade_point=grade_gradepoint_dict[grade]
                else:
                    grade="PP"
                    grade_point=grade_gradepoint_dict[grade]


        time_stamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        prev_block_hash=prevhash("marks")
        values=result_year +result_type+branch+sem+section+request.form['usn']+course_code+grade+grade_point+str(credit)+str(int1)+str(int2)+str(int3)+str(cie)+str(see)+str(total_marks)+time_stamp+prev_block_hash
        block_hash=blockhash(values,prev_block_hash)
        execute_db('insert into marks values("'+result_year +'","'+result_type+'","'+branch+'","'+sem+'","'+section+'","'+usn+'","'+course_code+'","'+grade+'","'+grade_point+'","'+str(credit)+'","'+str(int1)+'","'+str(int2)+'","'+str(int3)+'","'+str(cie)+'","'+str(see)+'","'+str(total_marks)+'","'+time_stamp+'","'+prev_block_hash+'","'+block_hash+'")')
        
        return render_template("insert_student_marks.html",message="Marks Inserted Sucessfully")
    return render_template("insert_student_marks.html")

#Works
@app.route('/add_teacher', methods=['POST', 'GET'])
def add_teacher():
    if request.method=="POST":
        for value in request.form.values():
            if value is "":
                    return render_template('add_teacher.html',message="Please enter all fields")

        sql='insert into teacher_details values("'+request.form['teacher_id']+'","'+request.form['teacher_name']+'","'+sha256_crypt.hash(request.form['teacher_id'])+'","'+request.form['designation']+'","'+request.form['doj']+'","'+request.form['branch']+'","'+request.form['phone_no']+'","'+request.form['email']+'")'
        execute_db(sql)
        return render_template('add_teacher.html',message="Teacher Added Successfully")
    # if session.get("usn"):
    return render_template('add_teacher.html')

#Works
def prevhash(table):
        # sql=query_db('select block_hash from '+session.get('oper_table')+' order by time_stamp desc limit 0,1')[0] if table=="" else query_db('select block_hash from '+table+' order by time_stamp desc limit 0,1')[0]
        # if occasion="processing":
        sql=query_db('select block_hash from '+table+' order by time_stamp desc limit 0,1')[0]
        if(len(sql)):
            # print(sql["block_hash"])
            return(sql["block_hash"])
        else:
            return("0")
#Works
def blockhash(values,prev_hash=""):
    concat=""
    for x in values:
        concat+=str(x)
    concat+=prev_hash+"SKj8UijHObbb77hbll78Hv"
    print(concat)
    return(sha256_crypt.hash(concat))
#Works
@app.route('/student_admission', methods=['POST', 'GET'])
def student_admission():
    if request.method=="POST":
        for value in request.form.values():
            if value is "":
                return render_template('student_admission.html',message="Enter all the fields")           
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename,"student_image"):
            filename = secure_filename(file.filename)
            #filename deleted off below code
            file.save(os.path.join(app.config['UPLOAD_FOLDER_STUDENT'],request.form["usn"]+"."+filename.split(".")[1]))
            # return redirect(url_for('student_admission',filename=filename))

        # session['oper_table']='student_details'
        prev_hash=prevhash('student_details')
        block_hash=blockhash(request.form.values(),prev_hash)
        sql='insert into student_details(usn,student_name,pwd,sem,section,branch,email,phone_no,year_start,year_end,fathers_name,counselor_teacher_id,time_stamp,prev_block_hash,block_hash) values("'+request.form["usn"]+'","'+request.form['student_name']+'","'+sha256_crypt.hash(request.form['usn'])+'","'+request.form['sem']+'","'+request.form['section']+'","'+request.form['branch']+'","'+request.form['email']+'","'+request.form['phone_no']+'","'+request.form['year_start']+'","'+str((int(request.form['year_start'])+4))+'","'+request.form['fathers_name']+'","'+request.form['counselor_teacher_id']+'",( select strftime("%Y-%m-%d %H:%M:%f", "now") ),"'+prev_hash+'","'+block_hash+'")'      
        execute_db(sql)
        return render_template('student_admission.html',message="Student Admission Successfully Complete")           
    # un comment after testing if session.get("usn"):
    return render_template('student_admission.html')

#Works
@app.route('/results', methods=['POST', 'GET'])
def results():
    if request.method=='POST':
        usn=session.get('usn')
        sem=request.form["sem"]
        grade=request.form["grade"]
        print(sem)
        print(grade)
        if sem and grade:
            print("inside sem and grade")
            marks_only=query_db('select course_code,int1,int2,int3,see,cie,grade from marks where (usn="'+usn+'" and sem="'+sem+'" and grade="'+grade+'")')
            # marks_only=query_db('select course_code,int1,int2,int3,see,cie,grade from marks where (usn="'+usn+'" and sem="'+sem+'" and grade="'+grade+'" )')

            marks=combine_table_results(marks_only,"results")
            return render_template("results.html",rows=marks)
        elif sem:
            print("inside sem")
            marks_only=query_db('select course_code,int1,int2,int3,see,cie,grade from marks where usn="'+usn+'" and sem="'+sem+'"')
            marks=combine_table_results(marks_only,"results")
            return render_template("results.html",rows=marks)
            
        elif grade:
            print("inside grade")
            marks_only=query_db('select course_code,int1,int2,int3,see,cie,grade from marks where usn="'+usn+'" and grade="'+grade+'"')
            marks=combine_table_results(marks_only,"results")
            return render_template("results.html",rows=marks)
        else:
            print("nothing")
            marks_only=query_db('select course_code,int1,int2,int3,see,cie,grade from marks where usn="'+usn+'"')
            marks=combine_table_results(marks_only,"results")
            return render_template("results.html",rows=marks)
    return render_template("results.html")
#Works
def combine_table_results(marks,table=""):
            if table=="":
                no_sub=len(marks)
                row=0
                while(row<no_sub):
                # course=""
                # if type_card="provisional":
                    fail=['F','W','NP']
                
                # if marks[row]["grade"] != "F" and marks[row]["grade"] != "W" and marks[row]["grade"] != "NP":
                    if marks[row]["grade"] not in fail:
                        print(marks[row]["grade"])
                        course = query_db('select course_name,credits from course where course_code="'+marks[row]["course_code"]+'"')
                # if type_card=="transcript":
                    # marks[row]["result_year"]
                        marks[row]["course_name"] = course[0]["course_name"] if course else ""
                        marks[row]["credits"] = course[0]["credits"] if course else ""
                        row+=1
                    else:
                        del marks[row]
                        no_sub-=1
            # if table=="results":
            if table:

                for row in range(0,len(marks)):
                    course = query_db('select course_name,credits from course where course_code="'+marks[row]["course_code"]+'"')
                    marks[row]["course_name"] = course[0]["course_name"] if course else ""
                    marks[row]["credits"] = course[0]["credits"] if course else ""
            print(marks)
            # return sorted(marks, key = lambda i: i['credits'],reverse=True)
            return marks

#Works
@app.route('/provisional_marks_card', methods=['POST', 'GET'])
def provisional():
    if request.method=='POST':
        #find academic year, get sem and usn as input
        #get course code,title,credits,grade(see) for that SEM
        #write a for loop to add all subject details for the number of subects
        #add prepared by in html
        usn=str(session.get('usn'))
        sem=int(request.form['sem'])
        sem_spga_no="sgpa"+str(sem)
        details=query_db('select year_start,student_name,branch,cgpa,'+sem_spga_no+' from student_details where usn="'+usn+'"'+block_part)
        year_start=details[0]["year_start"]
        name=details[0]["student_name"]
        branch=details[0]["branch"]
        sgpa=details[0][sem_spga_no]
        cgpa=details[0]["cgpa"]
        # print(sgpa+"  "+cgpa)
        if sem%2 ==0:
            acm_year=[(year_start+((sem//2)-1)),(year_start+(((sem//2))))] 
        else:
            acm_year=[(year_start+((sem//2))),(year_start+(((sem//2))+1))]
        #edit to add blockpart and programmitically sort by credits
        course=query_db('select course_code,grade from marks where usn="'+usn+'" and sem="'+str(sem)+'"')
        
        course_name=[]
        course_code=[]
        credit=[]
        grade=[]

        for items in course:
            course_code.append(items["course_code"])
            grade.append(items["grade"])
            print(items["course_code"])
            course_details=query_db('select course_name,credits from course where course_code="'+items["course_code"]+'"')
            # print(course_details)
            
            if course_details:
                course_name.append(course_details[0]["course_name"])
                credit.append(course_details[0]["credits"])
            
        provisional_html_generate.converthtml(name,"Bachelor of Engineering(B.E)",usn,sem,acm_year,branch,course_name,course_code,credit,grade,sgpa,cgpa)
        generate_provisional_transcript("provisional",usn,sem)
        pdf_path= os.path.join(os.getcwd(),'provisional_cards','provisional_marks_card_'+usn+'_'+str(sem)+'.pdf')
        filename=os.path.basename(pdf_path)
        sendmail("portalnie@gmail.com","Provisional Marks Card Request Generated","Provisional Marks Card generated for USN: "+usn+" and SEM :"+str(sem)+".\nRequest forward to COE's Office for verification and signature.\nForward the Signed copy to principal's office for signature.",open(pdf_path, "rb"),filename)
        return render_template("provisional_marks_card.html",message="Request Successful")
    return render_template("provisional_marks_card.html")
#Works
@app.route('/generate_transcript', methods=['POST', 'GET'])
def generate_transcript():
    if request.method=='POST':
        usn=session.get('usn')
        student=query_db('select student_name,branch,fathers_name,cgpa from student_details where usn="'+str(usn)+'"'+block_part)[0]
        student_name=student["student_name"]
        branch=student["branch"]
        fathers_name=student["fathers_name"]
        cgpa=student["cgpa"]
        marks=[]
        for sem in range(1,9):
            marks_only=query_db('select course_code,grade,result_year from marks where usn="'+str(usn)+'" and sem="'+str(sem)+'"')
            marks.append(combine_table_results(marks_only))
        print(marks)
        transcript_html_generate.converthtml(student_name,usn,fathers_name,branch,marks,cgpa)
        generate_provisional_transcript("transcript",usn)
        pdf_path= os.path.join(os.getcwd(),'transcripts','transcript_'+usn+'.pdf')
        # print(pdf_path)
        filename=os.path.basename(pdf_path)
        sendmail("portalnie@gmail.com","Transcript Request Generated","Transcript generated for USN: "+usn+".\nRequest forward to COE's Office for verification and signature.\nForward the Signed copy to principal's office for signature.",open(pdf_path, "rb"),filename)
        return render_template("transcript.html",message="Request Successful")

    return render_template("transcript.html")

app.config['UPLOAD_FOLDER_QUESTION'] = UPLOAD_FOLDER_QUESTION
app.config['UPLOAD_FOLDER_STUDENT'] = UPLOAD_FOLDER_STUDENT
def allowed_file(filename,usecase):
    if usecase is "question_paper":
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_QUESTION
    if usecase is "student_image":
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_STUDENT     
#Works
@app.route('/question_papers', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename,"question_paper"):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_QUESTION'], filename))
            return redirect(url_for('upload_file',filename=filename))
    return render_template("question_papers.html")
#Works
def generate_provisional_transcript(pdf_type,usn,sem=""):
    # cur_dir=os.path.dirname(__file__)
    usn=str(usn)
    sem=str(sem)

    if pdf_type=="provisional":
        html_path_provisional=os.path.join(os.getcwd(),'provisional_cards','provisional_marks_card_'+usn+'_'+sem+'.html')
        pdf_path_provisional= os.path.join(os.getcwd(),'provisional_cards','provisional_marks_card_'+usn+'_'+sem+'.pdf')
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

        pdfkit.from_file(html_path_provisional,pdf_path_provisional, configuration=config)
        set_password(pdf_path_provisional,usn+sem,usn+sem)
        
    if pdf_type=="transcript":
        html_path_transcript=  os.path.join(os.getcwd(),'transcripts','transcript'+usn+'.html')
        pdf_path_transcript= os.path.join(os.getcwd(),'transcripts','transcript_'+usn+'.pdf')
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

        pdfkit.from_file(html_path_transcript,pdf_path_transcript, configuration=config)
        set_password(pdf_path_transcript,usn,usn)
        
#Works
def sendmail(to,mail_subject,mail_body,mail_attach,filename=""):
    fromaddr = "portalnie@gmail.com"
    toaddr = to
    # instance of MIMEMultipart 
    msg = MIMEMultipart() 
    # storing the senders email address   
    msg['From'] = fromaddr 
    # storing the receivers email address  
    msg['To'] = toaddr 
    # storing the subject  
    msg['Subject'] = mail_subject
    # string to store the body of the mail 
    body = mail_body
    # attach the body with the msg instance 
    # open the file to be sent  
    attachment = mail_attach
    noattach=1 if attachment else 0
    if attachment:
    # To change the payload into encoded form 
        msg.attach(MIMEText(body, 'plain')) 
        p = MIMEBase('application', 'octet-stream') 
        p.set_payload((attachment).read()) 
    # encode into base64 
        encoders.encode_base64(p) 

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    # attach the instance 'p' to instance 'msg' 
        msg.attach(p) 
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    # start TLS for security 
    s.starttls() 
    # Authentication, provide account password here
    s.login(fromaddr, "portalniewelcome") 
    # Converts the Multipart msg into a string 
    text = msg.as_string() if noattach else 'Subject: {}\n\n{}'.format(mail_subject,mail_body)
    #if noattach else mail_body
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
    # terminating the session 
    s.quit() 
#Works
def set_password(input_file, user_pass, owner_pass):
    path, filename = os.path.split(input_file)
    output_file = os.path.join(path, "temp_" + filename)
    output = PyPDF2.PdfFileWriter()
    input_stream = PyPDF2.PdfFileReader(open(input_file, "rb"))
    for i in range(0, input_stream.getNumPages()):
        output.addPage(input_stream.getPage(i))
    outputStream = open(output_file, "wb")
    # Set user and owner password to pdf file
    output.encrypt(user_pass, owner_pass, use_128bit=True)
    output.write(outputStream)
    outputStream.close()
    move(output_file,input_file)
#Works
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.secret_key = 'qslkjJjhkNBkjhhJkUJjkjsds'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='127.0.0.1', port=8000, debug=True,threaded=True)
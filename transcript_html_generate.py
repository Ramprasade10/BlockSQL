from pathlib import Path
import datetime
import os
def converthtml(student_name,usn,fathers_name,branch,marks,cgpa):
    total_credits=0
    now = datetime.datetime.now()
    date=now.strftime('%d/%m/%Y')
    html="""<!DOCTYPE html>   
<html>
<head>
<title>Transcript</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style> 
h5{
margin: 0px 0px 0px 0px; 
padding: 0px 0px 0px 0px;
text-align: center;
font-weight:normal;
}
h4,h2{
margin: 0px 0px 0px 0px; 
padding: 0px 0px 0px 0px;
text-align: center;
}
table{
    font-size: 12px;
}
img{
margin: 0px 0px 5px 0px; 


padding: 0px 0px 0px 30px;}
table.solid1{
        border-collapse: collapse;
    margin-left:15px;}


th {
   
border-top: thin solid black;
border-bottom: thin solid black;
border-left:thin solid black;
border-right:thin solid black;
}
table.solid2{
   border-collapse: collapse;
    margin-right:15px;}
</style>
</head>


<body>

<br>
<img src="static/nie_logo.png" alt="NIE,MYSORE" align="left" width="75" height="75">"""
    html+='<img src="../static/images/'+usn+'.jpeg"'
    html+=""" alt="STUDENT,MYSORE" align="right" width="75" height="75">
<h2 align=center>THE NATIONAL INSTITUTE OF ENGINEERING</h2>
<p align=center> Mananthavadi Road, Mysuru-570008, India<br>
(Autonomous Institute Under Visvesvaraya Technological University,Belagavi)
</p>
<h4 align=center >TRANSCRIPT</h4>
<table style="width:48%" align="left" >"""
    html+='<tr><td>Name:&emsp;&emsp;&emsp;&emsp;&emsp;'+student_name+'</td></tr>'
    html+='<tr><td>Father Name:&emsp;&emsp;'+fathers_name+'</td></tr>'
    html+='<tr><td><br></td></tr>'
    html+='</table>'

    html+='<table style="width:48%" align="right">'
    html+='<tr><td colspan="100">USN:&emsp;&emsp;'+usn+'</td></tr>'
    html+='<tr><td colspan="100">Course:&emsp;BE in '+branch+'</td></tr>'
    html+="""<tr><td colspan="100">Medium of Instruction:&emsp;English</td></tr>"""
    html+='</table>'

    html+='<table style="width:48%" align="left" class=solid1>'
    html+="""<tr>
        <th width="20%">Course Code</th>
        <th>Course Title</th>
        <th>Credits</th>
        <th>Grade</th>
        <th>Exam Year</th>
    </tr>"""
    for sem in range(0,4):
            if marks[sem]: 
                html+="<tr><td><b>SEMESTER "+str(sem+1)+" </b></td></tr>"
                print(sem)
                for no_sub in range(0,len(marks[sem])):
                    print(marks[sem][no_sub])
                    course_code=marks[sem][no_sub]["course_code"]
                    grade=marks[sem][no_sub]["grade"]
                    result_year=marks[sem][no_sub]["result_year"].split("-")[0]
                    course_name=marks[sem][no_sub]["course_name"]
                    credit=marks[sem][no_sub]["credits"]
                    if credit and course_name and course_code:
                        total_credits+=float(credit)
                        html+='<tr><td>'+course_code+'</td>'
                        html+='<td>'+course_name+'</td>'
                        html+='<td>'+str(credit)+'</td>'
                        html+='<td>'+grade+'</td>'
                        html+='<td>'+result_year+'</td></tr>'
                    
    html+='</table>'
    html+='<table style="width:48%" align="right" class=solid2>'
    html+="""<tr>
        <th width="20%">Course Code</th>
        <th>Course Title</th>
        <th>Credits</th>
        <th>Grade</th>
        <th>Exam Year</th>
    </tr>"""
    if len(marks)>4:
        for sem in range(4,len(marks)):
                if marks[sem]: 

                    html+="<tr><td><b>SEMESTER "+str(sem+1)+" </b></td></tr>"
                    for no_sub in range(0,len(marks[sem])):
                        course_code=marks[sem][no_sub]["course_code"]
                        grade=marks[sem][no_sub]["grade"]
                        result_year=marks[sem][no_sub]["result_year"].split("-")[0]
                        course_name=marks[sem][no_sub]["course_name"]
                        credit=marks[sem][no_sub]["credits"]
                        if credit and course_name and course_code:
                            total_credits+=float(credit)
                        
                            html+='<tr><td>'+course_code+'</td>'
                            html+='<td>'+course_name+'</td>'
                            html+='<td>'+str(credit)+'</td>'
                            html+='<td>'+grade+'</td>'
                            html+='<td>'+result_year+'</td></tr>'
    html+='</table>'                    
    html+='</table><br><br><br><br>'

    html+='<table style="width:51%" align="center" >'
    html+='<tr><td colspan="50"><b>Total Credits:'+str("{:.2f}".format(total_credits))+'</b></td>'
    html+='<td colspan="50" align="right"><b>Cumulative Grade Point Average:'+str("{:.2f}".format(cgpa))+'</b></td></tr>'
    html+='</table>'

    html+='<p align="center">AUTHENTIC</p><br><br><br><br><br><br>'

    html+='<table style="width:90%" align="center">'
    html+="""<tr><td align="left"><b>Dr. T N Shridhar</td>
<td align="right"><b>Dr. G Ravi</td></tr>
<tr>
<td align="left"><b>Controller of Examinations</td>
<td align="right"><b>Principal</td>
</tr>"""
    html+='</table><br><br>'

    html+='<table  align="center" width="70%"rules="rows" border="1">'
    html+="""<tr><th align="left">
Grade
</th>
<td><b>S</td>
<td><b>A</td>
<td><b>B</td>
<td><b>C</td>
<td><b>D</td>
<td><b>PP</td>
</tr>
<tr>
<th align="left">
Marks
</th>
<td>>=90</td>
<td>75-89</td>
<td>60-74</td>
<td>50-59</td>
<td>45-49</td>
<td>Satisfactory</td>
</tr>"""
    html+='</table>'

    html+='<table style="width:27%" align="right">'
    html+='<tr><td><b>Date Of Issue:'+date+'</b></td></tr>'
    html+='</table></body></html>'


    with open(os.path.join(os.getcwd(),'transcripts','transcript'+str(usn)+'.html'), "w") as html_file:
            html_file.write(html)
        

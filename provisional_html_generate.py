from pathlib import Path
import os
def converthtml(name,programme,usn,sem,acm_year,branch,course_name,course_code,credit,grade,sgpa,cgpa):
    #variable setup
    year_start=str(acm_year[0])
    year_end=str(acm_year[1])
    total_credits=0
    for cr in credit:
        total_credits+=int(cr)
    total_credits=str(total_credits)
    usn=str(usn)
    sem=str(sem)
    html="""<!DOCTYPE html>   
<html>
<head>
<title>Provisional Markscard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
div{
 border: 5px solid black;
}
h5,h2{
margin: 0px 0px 0px 0px; 

padding: 0px 0px 0px 0px;
text-align: center;
}
img{
margin: 0px 0px 5px 0px; 

padding: 0px 0px 0px 30px;}
</style>
<!--table, th, td {
    border: 1px solid black;
    border-collapse: collapse;          
}
.nav li {
    display: inline-block;
    font-size: 20px;
    padding: 10px;
}
-->
</head>
<body>   

<div>
<br>
<img src="static/nie_logo.png" alt="NIE,MYSORE" align="left" width="75" height="75">
<h2 >THE NATIONAL INSTITUTE OF ENGINEERING</h2>
<h5 >(Autonomous Institute Under Visvesvaraya Technological University,Belagavi)</h5>
<h5>MYSURU - 570 008 (KARNATAKA-INDIA)</h5>
<h2>PROVISIONAL GRADE CARD</h2>
<br><br>
<table style="width:90%" align="center"  >"""
    html+='<tr><td colspan="50">Name:'+name+'</td></tr>'
    html+='<tr><td colspan="50">Programme:'+programme+'</td>'
    html+='<td colspan="50">USN:'+usn+'</td></tr>'
    html+='<br>'
    html+='<tr><td colspan="50">Semester:'+str(sem)+'</td>'
    html+='<td colspan="50">Academic Year:'+year_start+'-'+year_end+'</td></tr>'
    html+='<br>'
    html+='<tr><td colspan="50">Branch:'+branch+'</td></tr>' 
    html+='<br></table><br><br>'
    html+='<table style="width:90%" align="center" border="1">'
    html+="""<tr>
    <th height="40">Course Code</th>    
    <th height="40">Course Title</th> 
    <th height="40">Credits</th>
    <th height="40">Grade</th>
  </tr>"""
    for item in range(0,len(course_name)):        
        html+='<tr><td align=center>'+course_code[item]+'</td>'
        html+='<td>'+course_name[item]+'</td>'
        html+='<td align=center>'+str(credit[item])+'</td>'
        html+='<td align=center>'+grade[item]+'</td></tr>'
    html+='<tr><th height="30"colspan="3" align="left">Total Earned Credits</th>'
    html+='<td  align=center height="30" >'+total_credits+'</td></tr>'
    html+='<tr><th height="30" colspan="3" align="left">Semester Grade Point Average (SGPA)</th>'
    html+='<td  align=center height="30" >'+"{0:.2f}".format(float(sgpa))+'</td></tr>'
    html+='<tr><th height="30" colspan="3" align="left">Cumulative Grade Point Average (CGPA)</th>'
    html+='<td  align=center height="30">'+"{:.2f}".format(float(cgpa))+'</td></tr>'
    html+='</table><br><br>'
    html+='<table  align="center" width="90%" rules="rows" border="1">'
    html+='<tr><th align="left">Letter Grade:</th>'
    html+='<td>S</td>'
    html+='<td>A</td>'
    html+='<td>B</td>'
    html+='<td>C</td>'
    html+='<td>D</td>'
    html+='<td>E</td>'
    html+='<td>F</td></tr>'
    html+='<tr><th align="left">Grade Point:</th>'
    html+='<td>10</td>'
    html+='<td>9</td>'
    html+='<td>8</td>'
    html+='<td>7</td>'
    html+='<td>5</td>'
    html+='<td>4</td>'
    html+='<td>0</td></tr>'
    html+='<tr><th colspan="8" align="center"> S, A, B, C & D are Pass Grades,E & F are Fail Grades </th></tr>'
    html+='</table><br><br>'
    html+='<center>This provisional grade card is issued at the specific request of the student.</center>'          
    html+='<table style="width:90%" align="center">'
    html+='<tr><td align="left">Prepared by:</td>'
    html+='<td align="center">Scrutinized by:</td>'
    html+='<td align="right">Date of Issue</td></tr>'
    html+='</table><br><br>'
    html+='<h4 align=center>Signature of Head of the dept. with Seal</h4><br><br>' 
    html+='</div></body></html>'
    
    with open(os.path.join(os.getcwd(),'provisional_cards','provisional_marks_card_'\
    +str(usn)+'_'+str(sem)+'.html'), "w") as html_file:
        html_file.write(html)

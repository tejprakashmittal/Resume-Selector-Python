import os
import PyPDF2
from sqlalchemy.sql.expression import desc
import re
import string
import pandas as pd
import mysql.connector
from enum import unique
from flask import Flask,render_template,request,flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin

app = Flask(__name__)
p='12345'
_username=""
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/resume_build'%p
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secrethaibhai'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    user_type = db.Column(db.String(80))
    name = db.Column(db.String(80))
    username = db.Column(db.String(80),primary_key = True)
    password = db.Column(db.String(120))
    
    def get_id(self):
           return (self.username)
       
class File_Data(db.Model):
    __tablename__ = 'file_data'
    #username Foreign Key
    fileid=db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    filepath = db.Column(db.String(40))
    sde = db.Column(db.Integer)
    research = db.Column(db.Integer)
    operations = db.Column(db.Integer)
    supplychain = db.Column(db.Integer)
    project = db.Column(db.Integer)
    data = db.Column(db.Integer)
    healthcare = db.Column(db.Integer)
    content = db.Column(db.Integer)
    marketing = db.Column(db.Integer)
    teaching = db.Column(db.Integer)
    security = db.Column(db.Integer)

    def get_id(self):
        return (self.file_path)
    
    def __init__(self, username,filepath, sde, research, operations, supplychain, project, data, healthcare,content,teaching,marketing,security):
        self.username = username
        self.filepath =filepath
        self.sde= sde
        self.research=research
        self.operations=operations
        self.supplychain=supplychain
        self.project=project
        self.data=data
        self.healthcare=healthcare
        self.content=content
        self.marketing=marketing
        self.teaching=teaching
        self.security=security
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
        
# _user = User('admin', 'admin123', 'admin@example.com')
# db.session.add(_user)
# db.session.commit()
#dbData = user.query.all()
# db.session.add(_user)
# db.session.commit()

@app.route("/")
def index():
    # _user = User('admin', 'admin123', 'admin@example.com')
    # db.create_all()
    # db.session.add(_user)
    # db.session.commit()
    # dbData = User.query.all()
    return render_template("home.html") #,dbData = dbData

@app.route('/signup',methods = ['GET', 'POST'])
def signup():
     return render_template("signup.html")
 
@app.route('/do_signup',methods = ['GET', 'POST'])
def do_signup():
    if(request.method=='POST'):
        username = request.form.get('username')
        name = request.form.get('name')
        user_type = request.form.get('user_type')
        password = request.form.get('password')
        if(username == "" or name=="" or user_type=="Open this select menu" or password==""):
            return render_template("signup.html")
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            return render_template("msg_signup.html")
        else:
            user = User(user_type=user_type,name=name, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return render_template("msg_signup_success.html")

@app.route('/login',methods = ['GET', 'POST'])
def login():
     return render_template("login.html")
 
 
@app.route('/do_login',methods = ['GET', 'POST'])
def do_login():
     if(request.method=='POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            if(check_user.password == password and check_user.user_type == user_type):
                login_user(check_user)
                global _username
                _username=username
                if(str(user_type) == 'recruiter'):
                    return render_template("index.html")
                return render_template("user_seeker.html")
            else:
                return render_template("msg_inc_pass.html")
        else:
            return render_template("msg_inc_pass.html")

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return render_template("home.html")
        
def parse_pdf(filepath,filename):
    # Open pdf file
    pdfFileObj = open(filepath,'rb')

    # Read file
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    num_pages = pdfReader.numPages

    # Initialize a count for the number of pages
    count = 0

    # Initialize a text empty etring variable
    text = ""

    # Extract text from every page on the file
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count +=1
        text += pageObj.extractText()


    # Convert all strings to lowercase
    text = text.lower()

    # Remove numbers
    text = re.sub(r'\d+','',text)

    # Remove punctuation
    text = text.translate(str.maketrans('','',string.punctuation))


    # Create dictionary with industrial and system engineering key terms by area
    terms = {'SDE':['software','developer','c','c++','java','python',
                                'shell', 'database','scripting','php','node','javascript','systems','algorithm',
                                'data','performance','quality',
                                'sql','mongodb','mysql','networks','iit','iiit','nit',
                                'programming','production','git','bitbucket'],
            'Research Analyst':['research','analytical','conceptual','problem solving','high quality','reliable solutions',
                                'acquisition', 'cross platform','analysis','interpretation','documentation','report','ieee',
                                'publish','conference','paper'],
            'Operations management':['automation','bottleneck','constraints','cycle time','efficiency','fmea',
                                    'machinery','maintenance','manufacture','line balancing','oee','operations',
                                    'operations research','optimization','overall equipment effectiveness',
                                    'pfmea','process','process mapping','production','resources','safety',
                                    'stoppage','value stream mapping','utilization'],
            'Supply chain':['abc analysis','apics','customer','customs','delivery','distribution','eoq','epq',
                            'fleet','forecast','inventory','logistic','materials','outsourcing','procurement',
                            'reorder point','rout','safety stock','scheduling','shipping','stock','suppliers',
                            'third party logistics','transport','transportation','traffic','supply chain',
                            'vendor','warehouse','wip','work in progress'],
            'Project management':['administration','agile','budget','cost','direction','feasibility analysis',
                                'finance','kanban','leader','leadership','management','milestones','planning',
                                'pmi','pmp','problem','project','risk','schedule','scrum','stakeholders'],
            'Data analytics':['analytics','api','aws','big data','busines intelligence','clustering','code',
                            'coding','data','database','data mining','data science','deep learning','hadoop',
                            'hypothesis test','iot','internet','machine learning','modeling','nosql','nlp',
                            'predictive','programming','python','r','sql','tableau','text mining',
                            'visualuzation'],
            'Healthcare':['adverse events','care','clinic','cphq','ergonomics','healthcare',
                        'health care','health','hospital','human factors','medical','near misses',
                        'patient','reporting system'],
            'Content Writing':['Bloggers','Social','Media','Posts','Copy','writing','SEO','experience','knowledge', 'sales','product','media','professional','publication','newsletters','Writing','tonality',
                        'Word','PowerPoint','Excel'],
              	
            'Marketing':['business consultant','business plan',' purchase',' branding',' advertising',' remodeling',' and marketing',' increasing monthly sales','social media','followers','marketing campaigns','email','print',' digital',' outdoor','social media', 
                  'Crafted concept content for journal ads',' direct mail campaigns','blogs','Achieved','Executed','Promoted','','Analyzed','Generated','Researched','Captured','Implemented','Spearheaded','Designed','Increased','Tracked','Developed','Initiated','Utilized'],
              
            'Teaching':['Classroom management','Elementary or secondary education','Special education','Student-centered instruction','Parent involvement','interactive learning','Curriculum development',
			'Learning/instructional styles','Cooperative learning','Differentiated instruction','Distance learning','Behavior analysis/management','Lesson planning','Hands-on learning','Discipline management/strategies',
			'Educational assessment','Individual learning plan/individualized educational plans (IEP)','Teaching methodologies','Instructional technology','Developmental levels','Student advocate','Classroom instruction'],
		    
            'Security Analyst':['Testing','Web','Application','Security','Vulnerability','Assessment','Cybersecurity','Ethical','Hacking','Network Security','Information Security','Application Security','Burp','Suite','Linux','Security','Metasploit','Malware',
            'Analysis','Programming','Incident','Response']}


    # Initializie score counters for each area
    sde=0
    research=0
    operations = 0
    supplychain = 0
    project = 0
    data = 0
    healthcare = 0
    content=0
    marketing=0
    teaching=0
    security=0

    # Create an empty list where the scores will be stored
    scores = []

    # Obtain the scores for each area
    for area in terms.keys():
        if area == 'SDE':
            for word in terms[area]:
                if word in text:
                    sde +=1
            scores.append(sde)
                
        elif area == 'Research Analyst':
            for word in terms[area]:
                if word in text:
                    research +=1
            scores.append(research)
                    
        elif area == 'Operations management':
            for word in terms[area]:
                if word in text:
                    operations +=1
            scores.append(operations)
            
        elif area == 'Supply chain':
            for word in terms[area]:
                if word in text:
                    supplychain +=1
            scores.append(supplychain)
            
        elif area == 'Project management':
            for word in terms[area]:
                if word in text:
                    project +=1
            scores.append(project)
            
        elif area == 'Data analytics':
            for word in terms[area]:
                if word in text:
                    data +=1
            scores.append(data)
    
        elif area == 'Healthcare':
            for word in terms[area]:
                if word in text:
                    healthcare +=1
            scores.append(healthcare)

        elif area == 'Content Writing':
            for word in terms[area]:
                if word in text:
                    content +=1
            scores.append(content)

        elif area == 'Marketing':
            for word in terms[area]:
                if word in text:
                    marketing +=1
            scores.append(marketing)

        elif area == 'Teaching':
            for word in terms[area]:
                if word in text:
                    teaching +=1
            scores.append(teaching)

        else:
            for word in terms[area]:
                if word in text:
                    security +=1
            scores.append(security)

    f=File_Data(_username,filename,scores[0],scores[1],scores[2],scores[3],scores[4],scores[5],scores[6],scores[7],scores[8],scores[9],scores[10])
    db.session.add(f)
    db.session.commit()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/user_seeker', methods=['GET', 'POST'])
def upload_file():
    if(request.method == 'POST'):
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            summry = parse_pdf(filepath,filename)
            return render_template("message.html")                 #redirect(url_for('download_file', name=filename))
            #return redirect(url_for('download_file', name=filename))
    return render_template("msg_noupload.html")

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/fetch_data',methods=['GET', 'POST'])
def fetch_data():
    if(request.method == 'POST'):
        area = request.form.get('areas_select')
        if(area is not None):
            
            mydb = mysql.connector.connect(host="localhost",user="root",passwd="12345",)
            my_cursr = mydb.cursor()
            my_cursr.execute("use resume_build")
            sql1="SELECT %s,file_data.filepath,user.name FROM file_data,user WHERE file_"%area
            sql2="data.username = user.username ORDER BY %s DESC"%area
            sql1=sql1+sql2
            _area=(area,area)
            my_cursr.execute(sql1)
            #my_cursr.execute("SELECT %(res)s from file_data",{'res':area})
            data = my_cursr.fetchall()
            #print(data)
            # user_name=data[0][2]
            # my_cursr.execute("SELECT name FROM user WHERE username = %(res)s",{'res':user_name})
            # my_name = my_cursr.fetchall()
            # print(my_name)
            # data=File_Data.query.with_entities(text(area),File_Data.filepath).order_by(desc(text(area)))
            # print(data)
            # #name = User.query.filter_by(username=data['username']).first()
            # #print(name)
            # data1=User.query.all()
            # name=""
            # for i in data1:
            #     if(i.username == data[7]):
            #         name=i.name
            # print(name)        
            return render_template('index.html', data=data)
        else:
            return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True,port=5600)
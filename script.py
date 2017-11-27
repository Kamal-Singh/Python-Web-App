from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from email.mime.text import MIMEText
import smtplib

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres123@localhost/height_data'
db = SQLAlchemy(app)

def send_email(email,height,average_height,count):
    from_email="example@mail.com"
    from_pass="yourpass"
    message="Hey there, your height is <strong> %s</strong>. <br> \
    Average height is <strong>%s</strong> out of <strong>%s</strong> users. <br> \
    Thanks!" \
    % (height, average_height, count)
    subject="Height Statistics"

    gmail=smtplib.SMTP("smtp.gmail.com",587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email,from_pass)

    msg=MIMEText(message, 'html')
    msg['Subject']=subject
    msg['To']=email
    msg['From']=from_email

    gmail.send_message(msg)


class Data(db.Model):
    __tablename__="data"
    id=db.Column(db.Integer,primary_key=True)
    email_=db.Column(db.String(120),unique=True)
    height_=db.Column(db.Integer)

    def __init__(self, email_, height_):
        self.email_=email_
        self.height_=height_

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success',methods=['POST'])
def success():
    if request.method=='POST':
        email = request.form['email_data']
        height= request.form['height_data']
        print(email,height)
        print(db.session.query(Data).filter(Data.email_==email).count())
        if not db.session.query(Data).filter(Data.email_==email).count():
            reg=Data(email,height)
            db.session.add(reg)
            db.session.commit()
            average_height=db.session.query(func.avg(Data.height_)).scalar()
            average_height=round(average_height,1)
            count=db.session.query(Data).count()
            send_email(email,height,average_height,count)
            return render_template('success.html')
        else:
            return render_template('index.html',text="The Entered Email Has Already Been Used!!")

if __name__=='__main__':
    app.debug=True
    app.run()


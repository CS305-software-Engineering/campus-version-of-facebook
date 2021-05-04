from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from time import time
import json
import jwt
from app import app

db = SQLAlchemy()

class Credentials(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(), nullable= False)

    liked = db.relationship(
        'PostLike',
        foreign_keys='PostLike.user_id',
        backref='credentials', lazy='dynamic')

    def like_post(self, post_id):
        if not self.has_liked_post(post_id):
            print(self.id)
            like = PostLike(user_id=self.id, post_id=post_id)
            db.session.add(like)
            db.session.commit()

    def unlike_post(self, post_id):
        if self.has_liked_post(post_id):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post_id).delete()
            db.session.commit()

    def has_liked_post(self, post_id):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post_id).count() > 0

    def report_post(self, post_id):
        if not self.has_reported_post(post_id):
            print(self.id)
            report = PostReport(user_id=self.id, post_id=post_id)
            db.session.add(report)
            db.session.commit()

    def unreport_post(self, post_id):
        if self.has_reported_post(post_id):
            PostReport.query.filter_by(
                user_id=self.id,
                post_id=post_id).delete()
            db.session.commit()

    def has_reported_post(self, post_id):
        return PostReport.query.filter(
            PostReport.user_id == self.id,
            PostReport.post_id == post_id).count() > 0
    
    #get_reset_password_token() function returns a jwt token as a string which is generated directly by jwt.encode()
    def get_reset_password_token(self, expires_in=6000):
        return jwt.encode(
            {'reset_password': self.mail_id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    #verify_reset_password_token() is a static method(can be invoked directly from class)
    #this method takes token and attempts to decode it by pyJWT's jwt.decode()
    #if the token is invalid , an exception will be raised, and in that case i catch it to prevent the error, and
    #return none to the caller
    
    ##if the token is valid, id is returned from the token's payload by decdding it
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        print("heyymodels",id) #for personal convenience
        return id

class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('credentials.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('postss.id'))

class PostReport(db.Model):
    __tablename__ = 'post_report'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('credentials.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('postss.id'))


class newprofile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(50), unique = True, nullable = False)
    full_name = db.Column(db.String(), nullable= False)
    year = db.Column(db.Integer, nullable = False)
    department = db.Column(db.String(), nullable= False)
    degree = db.Column(db.String(), nullable= False)
    
# post datatable to store post details of with images
class Postss(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail_id = db.Column(db.String(25), unique=True, nullable=False)#mail_id of the person who created the post
    date = db.Column(db.DateTime(timezone=False), nullable=False)# date of the post creation
    post_description = db.Column(db.String(),nullable=False) # description of the post
    tag1  = db.Column(db.String(),nullable=False)  # tag (to show is related to a particular event)
    tag2 = db.Column(db.String(),nullable=True) # tag (to show is related to a particular event)
    tag3 = db.Column(db.String(),nullable=True) # tag (to show is related to a particular event)
    post_img = db.Column(db.LargeBinary, nullable=False) # images if anyone person wants to post with image
    reports = db.relationship('PostReport',backref='post',lazy = 'dynamic')
    def __init__(self,mid,d,pd,t1,t2,t3,pi):
        self.mail_id=mid
        self.date = d
        self.post_description =pd
        self.tag1 =t1
        self.tag2 = t2
        self.tag3 =t3
        self.post_img = pi
        #print(pd,t1,t2,t3,sep=" ")

# post datatable to store post details of without images         
class post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail_id = db.Column(db.String(25), unique=True, nullable=False) #mail_id of the person who created the post
    date = db.Column(db.DateTime(timezone=False), nullable=False) # date of the post creation
    post_description = db.Column(db.String(), nullable=False) # description of the post
    tag1 = db.Column(db.String(), nullable=False) # tag (to show is related to a particular event)
    tag2 = db.Column(db.String(), nullable=True)  # tag (to show is related to a particular event)
    tag3 = db.Column(db.String(), nullable=True)  # tag (to show is related to a particular event)
    post_img = db.Column(db.LargeBinary, nullable=True) # images if anyone person wants to post with image 

    def __init__(self, mid, d, pd, t1, t2, t3, pi):
        self.mail_id = mid
        self.date = d
        self.post_description = pd
        self.tag1 = t1
        self.tag2 = t2
        self.tag3 = t3
        self.post_img = pi

# datatable to store event details
class events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False) # username/mail_id of the person created the event
    title = db.Column(db.String(), nullable=False) #title of event
    description = db.Column(db.String(), nullable=False) # descriptoin of event
    venue = db.Column(db.String(), nullable=False) # venue of the event where it takes place
    tag = db.Column(db.String(), nullable=False) # tag of the event 
    sdate = db.Column(db.DateTime(timezone=False),nullable=False) # start date of the event
    stime = db.Column(db.DateTime(),nullable=False)# start time of the event
    edate = db.Column(db.DateTime(timezone=False))# end date of the event
    etime = db.Column(db.DateTime())# end time of the event
    color = db.Column(db.String(), nullable=False)# color of event to display in the calendar

    def __init__(self,un,t,d,v,tag,sd,st,ed,et,c):
        self.username=un
        self.title=t
        self.description=d
        self.venue=v
        self.tag=tag
        self.sdate=sd
        self.stime=st
        self.edate=ed
        self.etime=et
        self.color=c

# datatable to store tags of every event        
class eventags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(), nullable=False) # tag of event
    count = db.Column(db.Integer,nullable=False) # tag counter shows number of include the coresponding tag

    def __init__(self,t,c):
        self.tag= t
        self.count= c
        

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField,TimeField,FileField, DateField,SelectField,TextAreaField
from wtforms.validators import InputRequired, ValidationError,DataRequired, EqualTo,Email
from wtforms.fields.html5 import EmailField
from app.models import *
import datetime
from werkzeug.security import check_password_hash
import re
import email_validator
def invalid_credentials(form,field):
    mail_id_entered = form.mail_id.data
    password_entered = field.data
    user_object = Credentials.query.filter_by(mail_id = mail_id_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif not check_password_hash(user_object.password,password_entered):
        raise ValidationError("Username or password is incorrect")

def invalid_mail(form,field):
    mail_id_entered = form.mail_id.data
    user_object = Credentials.query.filter_by(mail_id=mail_id_entered).first()
    if user_object:
        raise ValidationError("Email already exists.")
    date=datetime.datetime.today()
    yr=date.strftime('%Y')    
    if '@iitrpr.ac.in' not in mail_id_entered or yr < mail_id_entered[:4]:
    	raise ValidationError("Use valid college Email-id for Registration")


def joining_yr_validation(form,field):
    mail_id_entered = form.mail_id.data
    join_yr = field.data
    if join_yr!= mail_id_entered[:4]:
        raise ValidationError("not a valid year")

def invalid_password(form,field):
    password_entered = field.data
    regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pattern = re.compile(regex)
    result = re.search(pattern,password_entered)
    if not result:
        raise ValidationError("Password must contain atleast one digit, one uppercase, one lowercase, one special symbol and between 6 to 20 characters")

class LoginForm(FlaskForm):
    mail_id = EmailField('mail_id', validators=[InputRequired(message = "Email required required"), Email("This field requires a valid email address")])
    password = PasswordField('Password', validators=[InputRequired(message = "Password required"),invalid_credentials])


class RegistrationForm(FlaskForm):
    mail_id = EmailField('mail_id', validators=[InputRequired(message = "Email required required"), Email("This field requires a valid email address"),invalid_mail])
    password = PasswordField('password',validators=[InputRequired(message = "Password mismatch"),invalid_password])
    confirm_password = PasswordField('confirm_password',validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('full_name')
    year = IntegerField('year',validators=[InputRequired(),joining_yr_validation])
    department = SelectField(label = 'department', choices = [('CSE','CSE'),('Electrical','Electrical'),('Maths and Computing','Maths and Computing'),('Mechanical','Mechanical'),('Civil','Civil'),('Chemical','Chemical'),('Metallurgy','Metallurgy')])
    degree = SelectField(label = 'degree', choices = [('B.Tech','B.Tech'),('M.Tech','M.Tech'),('M.Sc','M.Sc'),('PhD','PhD')])

# form for creating posts    
class PosttForm(FlaskForm):
    post_description = TextAreaField('caption', validators=[InputRequired()]) #caption is required field
    post_img = FileField("upload") # image is optional 
    tag1 = SelectField("Select a tag   ", coerce=int, validators=[InputRequired()],default=0) # one tag is required field
    tag2 = SelectField("Select a tag   ", coerce=int,default=0) # tag is optional
    tag3 = SelectField("Select a tag   ", coerce=int,default=0) # tag is optional
    date = DateField("date",format='%Y-%m-%d') # posted date of the post

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.date.data:
            self.date.data = datetime.date.today() #the date need not be entered in the it will automatically takes today's date

# input fields in reset password request form
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])  #only valid email-id are accepted
    submit = SubmitField('Request Password Reset')   #submit button field in the form

 # input fields in reset password form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',validators=[InputRequired(message = "Password mismatch"),invalid_password])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])   #confirming the password2 and checking for match using EqualTo() validator
     submit = SubmitField('Submit')  #submit button field in the form

#form is to search tag in the home page    
class HomeForm(FlaskForm):
    #the choices are sent dynamic way (from database system ) in application.py
    tag_search = SelectField('enter the tag       ',coerce=int,validators=[InputRequired()]) #tags can be selected only from the ones are present 
    
#form is to create event form 
class EventForm(FlaskForm):
    title = StringField("Title",validators=[InputRequired()]) # title of the event is required field
    description =TextAreaField("Description",validators=[InputRequired()])# description of the event(contains details of the event can have links to registration form too) is required field
    venue      = StringField("Venue",validators=[InputRequired()])# venue(location/platform) of the event is required field
    sdate     = DateField("Start Date",format='%Y-%m-%d',validators=[InputRequired()])# start date of the event is required field
    stime     = TimeField("Start Time", format="%H:%M",validators=[InputRequired()])# time when event starts is required field
    edate = DateField("End Date", format='%Y-%m-%d',validators=[InputRequired()])# end date of the event is required field
    etime = TimeField("End Time", format="%H:%M",validators=[InputRequired()])# time when event ends is required field
    tag   = StringField("Tag",validators=[InputRequired()]) # tag of the event(to tag event in the posts) is required field
    color = SelectField("Colour",choices=[('#4fbd0a',' green'),('#082b96 ','blue'),('#4a0896 ','violet'),('#96087e ','purple'),('#960833',' pink'),('#960808 ','maroon'),('#bd5a0a','brown'),('#089669 ','navygreen'),('#086e96',' navyblue')])
                  #color of event to be displayed in calendar



class UpdateYourAccountForm(FlaskForm):
    mail_id = StringField('mail_id', validators=[InputRequired(message = "Email required required"), Email("This field requires a valid email address")])  #validators=[invalid_mail,InputRequired(message="Mail already exists")], check this
    full_name = StringField('full_name')
    year = IntegerField('year')
    # department = StringField('department')
    # degree = StringField('degree')
    department = SelectField(label='department', choices=[('CSE', 'CSE'), ('Electrical', 'Electrical'),
                                                          ('Maths and Computing', 'Maths and Computing'),
                                                          ('Mechanical', 'Mechanical'), ('Civil', 'Civil'),
                                                          ('Chemical', 'Chemical'), ('Metallurgy', 'Metallurgy')])
    degree = SelectField(label='degree',
                         choices=[('B.Tech', 'B.Tech'), ('M.Tech', 'M.Tech'), ('M.Sc', 'M.Sc'), ('PhD', 'PhD')])
    # image_file = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    # submit = SubmitField('Update')


    #####____________________THese checks need to be reevaluated__________________________#####
    # def validate_email(self, mail_id):
    #     if mail_id.data != mail_id.email:
    #         user = Profile.query.filter_by(mail_id=mail_id.data).first()
    #         if user:
    #             raise ValidationError('That email is taken. Please choose a different one.')

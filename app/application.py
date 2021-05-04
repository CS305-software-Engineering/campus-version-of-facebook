from app import app ##for initiating the app
from app.forms import * ## to get all the forms and validators in them
from app.models import * ## all the tables present in database 
from flask import render_template, url_for, redirect,request, jsonify,flash ## components of flask to connect to frontend
from flask_login import LoginManager, login_user, current_user, login_required, logout_user ## modules for logging in a user
from sqlalchemy import create_engine ## connecting to database
from flask_mail import Mail, Message  ## to send mails in forgot password
from app.e import * ## to send mails in forgot password
from itsdangerous import URLSafeTimedSerializer 
from werkzeug.security import generate_password_hash,check_password_hash ## to hash password and validating entered password with the hash of password
import base64 ## encode and decode images
from functools import cmp_to_key
import spacy
import en_core_web_sm
import os
import secrets
from PIL import Image

# creating engine
engine = create_engine('postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk')
# connecting to database
connection = engine.raw_connection()
# creating a cursor
mycursor = connection.cursor()
# configuring database
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) ## instance of database
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# session = db.session()
# cursor = session.execute(sql).cursor


login = LoginManager(app)
login.init_app(app)

# configuring the mail details from which mail is to be sent
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'developmentsoftware305@gmail.com'
app.config['MAIL_PASSWORD'] = 'tempmail1@'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

def wordsim(w1,w2):
    nlp = en_core_web_sm.load()
   # print("Enter two space-separated words")
   # words = input()
    words = w1 + w2
    tokens = nlp(words)

    for token in tokens:
        print(token.text, token.has_vector, token.vector_norm, token.is_oov)

    token1, token2 = tokens[0], tokens[1]

    print("Similarity:", token1.similarity(token2))
    return  token1.similarity(token2)
#function for loading the user if logged in
@login.user_loader
def load_user(id):
    return Credentials.query.get(int(id))

#home route
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods = ['GET','POST'])
def login():
    login_form = LoginForm() # loading login form
    reg_form = RegistrationForm()#loading register form
    print(request.method)
    if request.method == 'POST': # if form submitted
        if request.form["action"] == "Login": # if login form submitted
            if login_form.validate_on_submit():  # if conditions specified in forms.py are satisfied
                user_object = Credentials.query.filter_by(mail_id = login_form.mail_id.data).first() # get details from Credentials table
                login_user(user_object) #login the particular user

                return redirect(url_for('home')) # redirect to home page after successful login
        elif request.form["action"] == "Register": # if registration form submitted
            if reg_form.validate_on_submit(): # if conditions specified in forms.py are satisfied
                mail_id = reg_form.mail_id.data # get details from the form submitted
                password = reg_form.password.data
                cred = Credentials(mail_id=mail_id, password=generate_password_hash(password)) # create object for Credentials ## password is hashed here
                prof = newprofile(mail_id=mail_id, full_name=reg_form.full_name.data, year=reg_form.year.data,
                               department=reg_form.department.data, degree=reg_form.degree.data) # create object for Profile
                db.session.add(cred) # add the details to the Credentials table in database 
                db.session.add(prof) # add the profile details to the Profile table in database
                db.session.commit()
                flash('You were successfully registered')
                return redirect(url_for('login')) # redirect to login after successful registration
    return render_template("login.html", form1 = login_form, form = reg_form) # if the method is post then return the login form

#reset password route, to retreive the mail id and send mail to the same
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
#if the user is logged in, then there is no need of reset password functionality,so redirected to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))

#form to retreive the email_id, falls under reset_password_request.html
    form = ResetPasswordRequestForm()
        #if form details are valid
    if form.validate_on_submit():
        user = Credentials.query.filter_by(mail_id=form.email.data).first()  #check if the given id is registered in db or not
        if user:
            print("user found")
            send_password_reset_email(user) #if user is found, invoke send_password function defined in models corr to the user mail
        #flash('Check your email for the instructions to reset your password')
         flash('Reset password link has been sent to your email account.')
        return redirect(url_for('login'))   #redirect to login page
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

#when the user clicks on the password reset link , a second route associated with password reset is triggered
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #retreiving the user by invoking verify_reset_token_method
    idRec = Credentials.verify_reset_password_token(token)
    print("heyappplication""", idRec) #for personal convenience

    
    #if token is valid the user is presented with aform to reset password    
    form = ResetPasswordForm()
        # if form details are valid
    if form.validate_on_submit():
        user = Credentials.query.filter_by(mail_id=idRec).first()  #fetch the user from database for updation
        print("heyy after reset password", form.password.data)
        print("heyy before reset password", user.password)   ##for personal convenience
        user.password=generate_password_hash(form.password.data) ## generate password hash ##reseting the users password to one retreived from form
        
        #update query
        mycursor.execute("UPDATE credentials SET password = '{password}' WHERE mail_id = '{mail}' ".format(password = str(user.password), mail =  str(idRec)))
        connection.commit()
        print("heyy after reset password in database", user.password)
        flash('Your password has been reset.')
        return redirect(url_for('login'))   #finally redirect to login page
    return render_template('reset_password.html', form=form)     #rendering corresponding template with password reset form

#after successful login it is redirected to home route
@app.route('/home',methods=["POST","GET"])
@login_required
def home():
    mycursor.execute("select id,tag from eventags order by count desc") # fetching the event tags data order b count in descending order
    trending1 = mycursor.fetchall()
    trending = [x[1] for x in trending1[:4]]           # made a list of tags 
    trending = trending[:4]                           #gives top 4 trending tags
    hform = HomeForm()                                # form for searching tags
    value = [(x[0], x[1]) for x in trending1]          #list of tuples with id,tag 
    value = sorted(value)                             #sorted according to id's
    hform.tag_search.choices = value[1:]                  #this list is passed to HomeForm tag search for choices
    date = datetime.datetime.today()
    mycursor.execute("select * from events where sdate>='{d}' order by sdate " .format(d=date)) # upcomimg events are taken using this qu
    upcoming = mycursor.fetchall()
    if len(upcoming)>4:
        upcoming=upcoming[:4]
    mycursor.execute("select post_id from post_like where user_id = '{0}'".format(str(current_user.id)))
    posts = mycursor.fetchall()
    all_fav_tags = []
    print(posts)
    for i in posts:
        print(i[0])
        mycursor.execute("select tag1,tag2,tag3 from post where id = {0}".format(i[0]))
        tags = mycursor.fetchall()
        print(tags)
        if tags:
            for x in tags[0]:
                if x:
                    all_fav_tags.append(x)

    print(all_fav_tags)
    liked = max(set(all_fav_tags), key=all_fav_tags.count)
    print(liked)
    mycursor.execute("select tag from eventags")
    all_tags = mycursor.fetchall()
    similarity = []
    all_tags = list(all_tags)

    def similarity_cmp(a, b):
        a = a[0]
        b = b[0]
        print(type(liked))
        if (wordsim(liked, a) < wordsim(liked, b)):
            return -1
        else:
            return 1

    similarity_cmp_key = cmp_to_key(similarity_cmp)
    all_tags.sort(key=similarity_cmp_key)
    recommended_tags = all_tags[0:4]
    print(recommended_tags)
    recommended_events = []
    for tag in recommended_tags:
        mycursor.execute("select * from events where tag = '{0}'".format(str(tag[0])))
        recommended_events += mycursor.fetchall()

    #print(recommended_events)
    if len(recommended_events)>4:
        recommended_events=recommended_events[:4]

    return render_template('home.html', form=hform,trending=trending,upcoming=upcoming)   # rendering home page passing form and trending events data


# it is routed to homeSearch by ajax present in Home.html
@app.route('/homeSearch',methods=["POST","GET"])
@login_required
def homeSearch():
    if request.method == "GET":            # method type is GET
        mycursor.execute(
            "select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id,p.id from post as po , newprofile as p where p.mail_id=po.mail_id order by date")
        data1 = mycursor.fetchall()         # date,description,tags username of the person posted of all posts with images are fetched from database
        mycursor.execute(
            "select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id,p.id from postss as po , newprofile as p where p.mail_id=po.mail_id order by date")
        data = mycursor.fetchall()          # date,description,tags username of the person posted of all posts with images are fetched from database
        data = [list(x) for x in data]      # tuples are converted into lists
        #print(data,data1,sep="\n")
        imgs = [base64.b64encode(x[4]) for x in data]    # binary files are encoded(converted) to text form(readable) using base64 library
        imgs = [x.decode('utf-8') for x in imgs]        # files are decoded to form can be displayed in html using base64      

        for i in range(len(data)):
            data[i][4] = imgs[i]            # these images are replaced with the before ones
        data.extend(data1)                  # data related to posts with image and without image are merged into one list

        data.sort(key=lambda x: x[1], reverse=True)        # data is sorted according to the posted date

        return jsonify({"htmlresponse": render_template('response.html', data=data)}) # this data are sent to response.html using htmlresponse in jsonify

    elif request.method == "POST":
        mycursor.execute("select id,tag from eventags") # fetching the event tags data order b count in descending order
        tvalue = mycursor.fetchall()
        tvalue = [(x[0], x[1]) for x in tvalue]  #list of tuples with id,tag 
        tvalue = dict(tvalue)          # converted them into dictionary
        tvalue[0] = ''                 # no tag is selected gives 0 that is converted to empty string
        x = request.form['tag']        # requesting the value of tag searched
       # print(x)
        x = tvalue.get(int(x))         # using dictionary getting the tag 
        if x:                          # if tag is not a empty string 
            mycursor.execute(
                " select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id,p.id from postss as po , newprofile as p"
                " where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date".format(
                    str(x)))     # date,description,tags username of the person posted of the posts that related to tag searched with images are fetched from database
            data = mycursor.fetchall()
            mycursor.execute(
                " select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id,p.id from post as po , newprofile as p"
                " where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date".format(
                    str(x)))   # date,description,tags username of the person posted of the posts that related to tag searched without images are fetched from database
            data1 = mycursor.fetchall()
            data = [list(x) for x in data]       # tuples are converted into lists 
            imgs = [base64.b64encode(x[4]) for x in data]  # binary files are encoded(converted) to text form(readable) using base64 library
            imgs = [x.decode('utf-8') for x in imgs]         # files are decoded to form can be displayed in html using base64      
            for i in range(len(data)):
                data[i][4] = imgs[i]                       # these images are replaced with the before ones
            data.extend(data1)                              # data related to posts with image and without image are merged into one list
            data.sort(key=lambda x: x[1], reverse=True)        # data is sorted according to the posted date
            return jsonify({"htmlresponse": render_template('response.html', data=data)}) # this data are sent to response.html using htmlresponse in jsonify

        else:
            return jsonify({"error": "Select a tag "})     # this is returned when string is empty

    return jsonify({"error": "error"})


#route to create post and routed to this page on clicking create post button
@app.route('/create_post', methods = ['GET','POST'])
@login_required
def create_post():
    ptform = PosttForm()              # form to create post
    mycursor.execute("select id,tag from eventags") # fetching the event tags data order b count in descending order
    value = mycursor.fetchall()
    value = [(x[0], x[1]) for x in value]            #list of tuples with id,tag 
    value = sorted(value)                            #sorted according to id's
    ptform.tag1.choices = value[1:]                       #this list is passed to postForm tag1 choices for selction  
    ptform.tag2.choices = value                       #this list is passed to postForm tag2 choices for selction
    ptform.tag3.choices = value                        #this list is passed to postForm tag3 choices for selction  
    value = dict(value)                              #converted it into dictionary
    value[0] = ''                                   # that is selected no tag 
    if request.method == "POST":
        if ptform.validate_on_submit():
            f = request.files['post_img']           # storing image file in f     
            mycursor.execute("update eventags set count=count+1 where id='{0}'".format(ptform.tag1.data)) # if tag is used in post counter is incremented of the coresponding tag
            connection.commit()
            if ptform.tag2.data != 0:
                mycursor.execute("update eventags set count=count+1 where id='{0}'".format(ptform.tag2.data)) # if tag is used in post counter is incremented of the coresponding tag
                connection.commit()
            if ptform.tag3.data != 0:
                mycursor.execute("update eventags set count=count+1 where id='{0}'".format(ptform.tag3.data))# if tag is used in post counter is incremented of the coresponding tag
                connection.commit()
            if f:
                newPost = Postss(d=ptform.date.data, pd=ptform.post_description.data,
                                 t1=value[ptform.tag1.data], t2=value[ptform.tag2.data], t3=value[ptform.tag3.data],
                                 mid=current_user.mail_id
                                 , pi=f.read())    # if there is image in the created post it is stored in postss datatable
            else:
                newPost = post(d=ptform.date.data, pd=ptform.post_description.data,
                               t1=value[ptform.tag1.data], t2=value[ptform.tag2.data], t3=value[ptform.tag3.data],
                               mid=current_user.mail_id
                               , pi=f.read())         # if there is no image in the created post it is stored in post datatable

            db.session.add(newPost)
            db.session.commit()
            return "uploaded successfully"
    return render_template('create_post.html', form=ptform) # rendering create_post and passing the post form 

#route to like or dislike a post
@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):  
   
    if action == 'like': ## if the post is liked
        current_user.like_post(post_id) ## call like_post in models to include the post in post_like table

    if action == 'unlike': ## if the post is disliked
        current_user.unlike_post(post_id) ## call unlike_post in models to delete the post in post_like table

    return redirect(request.referrer) ## return to the same page

#route to report or take back report of a post and auto delete a post if many people reported 
@app.route('/report/<int:post_id>/<action>') 
@login_required
def report_action(post_id, action):
    print(post_id)
    if action == 'report': ## if the post is reported
        current_user.report_post(post_id) ## call report_post in models to include the post in post_report table
        mycursor.execute("select id, user_id from post_report where post_id = {0} ".format(post_id)) ## fetching all users and ids  who reported the post
        reports = mycursor.fetchall() 
        reports = [x[0] for x in reports] ## getting users
        no_of_reports = len(reports) ##counting number of users who reported the post
        print(no_of_reports) 
        if no_of_reports>1 : ## if no of reports crosses a threshold value
            mycursor.execute("delete from postss where id = {0}".format(post_id)) ## delete the post if no of reports crosses a threshold value
            connection.commit() ## commit the changes to database 
    if action == 'unreport': ## if a report on post is  taken back
        current_user.unreport_post(post_id) ## call unreport_post in models to delete the post in post_report table

    return redirect(request.referrer)## return to the same page



@app.route('/calendar', methods=["GET", "POST"])
@login_required
def calendar():
    mycursor.execute("select * from events order by id") # selecting all the event data form database
    data = mycursor.fetchall()
    timedate1 = [datetime.datetime.combine(x[5], x[6]) for x in data] # combining the start date and time of every event
    timedate2 = [datetime.datetime.combine(x[7], x[8]) for x in data] # combining the end date and time of every event
    data = [list(x) for x in data]

    for i in range(len(data)):
        data[i][5] = timedate1[i] #replacing the value with combined start date and time event.
        data[i][6] = timedate2[i] #replacing the value with  end date and time event.

    return render_template("calendar1.html", data=data)

#route to create/add event and routed to this page on clicking create/add event button
@app.route("/addevent", methods=['GET', 'POST'])
@login_required
def addevent():
    eform = EventForm()                                        #form to create event
    mycursor.execute("select tag from eventags")            #fetching event tags data 
    value = mycursor.fetchall()
    value = [x[0] for x in value]                          # creating list of tags    
    if request.method == 'POST':

        if eform.tag.data not in value:                     #tag given is not present in the tags collection  
            x = 0
            newtag = eventags(t = eform.tag.data, c=x)     #inserting this tag in evnetags data table with count 0
            db.session.add(newtag)
            db.session.commit()

        newevents = events(t=eform.title.data, d=eform.description.data, v=eform.venue.data, tag=eform.tag.data,
                           sd=eform.sdate.data,
                           st=eform.stime.data, ed=eform.edate.data, et=eform.etime.data, un=current_user.mail_id,
                           c=eform.color.data)   # event details are inserted into event data table
        db.session.add(newevents)
        db.session.commit()
        return "success"
    return render_template('create_event.html', form=eform) #rendering create_event and passing the form

# logout route
@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()   # inbuilt function to logout user
    return redirect(url_for('login')) # redirect to login page



#################for updating profile####################################

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)  ###for resizing
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/viewProfile/<string:id>", methods=["GET","POST"])
@login_required
def viewProfile(id):
    mycursor.execute("select * from newprofile where id='{0}'".format(id))
    pdata=mycursor.fetchall()
    pdata=list(pdata[0])
    user = pdata[1]
    pdata[1]=str(pdata[1]).strip("@iitrpr.ac.in")
    mycursor.execute("select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id,p.id from post as po , newprofile as p where p.mail_id=po.mail_id and po.mail_id='{mailid}' order by date"
                     .format(mailid=user))
    data1 = mycursor.fetchall()  # date,description,tags username of the person posted of all posts with images are fetched from database
    mycursor.execute(
        "select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id,p.id from postss as po , newprofile as p where p.mail_id=po.mail_id and po.mail_id='{mailid}' order by date"
            .format(mailid=user) )
    data = mycursor.fetchall()  # date,description,tags username of the person posted of all posts with images are fetched from database
    data = [list(x) for x in data]  # tuples are converted into lists
    imgs = [base64.b64encode(x[4]) for x in
            data]  # binary files are encoded(converted) to text form(readable) using base64 library
    imgs = [x.decode('utf-8') for x in imgs]  # files are decoded to form can be displayed in html using base64

    for i in range(len(data)):
        data[i][4] = imgs[i]  # these images are replaced with the before ones
    data.extend(data1)  # data related to posts with image and without image are merged into one list
    data.sort(key=lambda x: x[1], reverse=True)  # data is sorted according to the posted date

    #return jsonify({"htmlresponse": render_template('response.html',
      #                                              data=data)})  # this data are sent to response.html using htmlresponse in jsonify

    return render_template("viewProfile.html",pdata=pdata,data=data)


@app.route('/updateAccount', methods=['GET', 'POST'])
@login_required  #  to be checked
def updateAccount():
    form = UpdateYourAccountForm()
    if form.validate_on_submit():
        # picture_file=" "
        # if form.image_file.data:
        #     picture_file = save_picture(form.image_file.data)
            # current_user.image_file = picture_file  to be checkeddd
        # image_file=picture_file
        ###yet to be seen
        mail_id = form.mail_id.data
        if mail_id!= current_user.mail_id:
                user = newprofile.query.filter_by(mail_id=mail_id).first()
                if user:
                    raise ValidationError('That email is taken. Please choose a different one.')
        ##to be seen
        full_name = form.full_name.data
        # prof = Newprofile(full_name=form.full_name.data, year=form.year.data,
        #                department=form.department.data, degree=form.degree.data, mail_id=mail_id, image_file=picture_file)
        mycursor.execute("UPDATE Newprofile SET full_name= '{fullName}', year='{year}', department='{dept}', degree='{degree}', mail_id='{mail}' WHERE mail_id = '{mailId}' ".format(fullName=str(form.full_name.data),year=int(form.year.data), dept=str(form.department.data),degree=str(form.degree.data), mail=str(form.mail_id.data), mailId=str(current_user.mail_id)))
        mycursor.execute("UPDATE credentials SET mail_id = '{mail}' WHERE mail_id = '{mailId}' ".format(mail=str(form.mail_id.data), mailId=str(current_user.mail_id)))
        connection.commit()
        ### THIS UPDATING INFO TO BE SEEN YET
        # flash('Your account has been updated!', 'success')
        return redirect(url_for('home'))    #redirection to be seennn

    elif request.method == 'GET':
         # form.full_name.data = current_user.full_name
         user = newprofile.query.filter_by(mail_id=current_user.mail_id).first()   ###nothing done for error
         #others fields to be added yet
         form.mail_id.data = user.mail_id
         form.full_name.data=user.full_name
         form.year.data = user.year
         form.department.data=user.department
         form.degree.data = user.degree




    # imagefile = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('updateProfile.html', title='Account',form=form)

     ##image_file to be passed yet


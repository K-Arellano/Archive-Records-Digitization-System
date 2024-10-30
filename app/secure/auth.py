from flask import render_template, redirect, url_for, request, Blueprint, jsonify, session
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from app.secure.user_logs import updateDB
from app import login_manager, argon2, captcha 
from app.database import config
from app.secure.login_form import LoginForm
from app.secure.randomizer import generate_key, generate_token, check_token
from app.secure.user_logs import loginHistory
from app.secure.authorization import admin_required

auth = Blueprint('auth', __name__)

#setup query to update database when user session expired
def session_expired(username):
    if username:
        updateDB()
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user WHERE username = %s AND online = 1', (username))
            userData = cursor.fetchone()
            
            if userData:
                cursor.execute('SELECT * FROM session WHERE username = %s AND online = 1', (username))
                sessionData = cursor.fetchone()

                if sessionData:
                    cursor.execute('DELETE FROM session WHERE username = %s', (username,))
                    config.conn.commit()
                else:
                    print('session user not found')
            else:
                print('session user not found')

#setup for user session
class User(UserMixin):
    def __init__(self, id, username, role, token):
        self.id = id
        self.username  = username
        self.role = role
        self.token = token

    #fetch user information based on input
    def get_User(self):
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM session WHERE session_id = %s', (self.id,))
            user_session = cursor.fetchone()

            if user_session:
                cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_session['user_id'],))
                return cursor.fetchone()
            else:
                return None
            
    #verify user session token authentication           
    @property
    def is_authenticated(self):
        with config.conn.cursor() as cursor:
            user = self.get_User()
            if user and check_token(self.token, user['password'], user['pass_key'], self.id):
                cursor.execute('UPDATE user SET online = 1, last_online = NULL WHERE user_id = %s AND online = 0', (user['user_id'],))
                config.conn.commit()
                return True
            else:
                return False
            
    #verify if user account is not deactivated
    @property
    def is_active(self):
        user = self.get_User()
        if user and user['status'] == 1:
            return True
        else:
            return False
        
#load user account in session
@login_manager.user_loader
def load_user(session_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM session WHERE session_id = %s', (session_id))
            search_session = cursor.fetchone()
           
            if search_session:
                cursor.execute('SELECT * FROM user WHERE user_id = %s', (search_session['user_id'],))
                user = cursor.fetchone()
                    
                if user:
                    token = generate_token(user['password'], user['pass_key'], session_id)
                    return User(session_id, search_session['username'], {1: 'admin', 2: 'staff'}.get(search_session['role']), token)
                else:
                    return None
            else:
                return None
            
    except Exception as e:
        print(f"login loader: {e}")

#setup route for login procedure
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    role = ''
    invalidError = 'User not Found or Invalid Password. Please Try Again!'
    captchaError = 'Please solve the captcha to verify you’re not a robot. Please Try Again!'
    attemptError = 'Excessive login attempts detected. You’re temporarily blocked for 1 hour. Please try again later.'
    error = invalidError
    
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        input_captcha = request.form.get('captcha')
        form.captcha.data = ''
        user_role = {'1': 'admin', '2': 'staff'}.get(role, 'error')
        role = int(role)
        
        if username and password:
            with config.conn.cursor() as cursor:
                #Search for the user in the database
                cursor.execute('SELECT * FROM user WHERE username = %s AND role = %s', (username, role))
                user = cursor.fetchone()

                if captcha.get_answer() == input_captcha:#validate captcha input
                    if user and argon2.check_password_hash(user['password'], password) and user['status'] == 1:#authentication for login

                        cursor.execute('SELECT * FROM session WHERE user_id = %s', (user['user_id']))
                        session_data = cursor.fetchone()

                        if session_data and len(session_data['session_id']) == 128:
                            session_id = session_data['session_id']
                        else:
                            session_id = generate_key()
                            cursor.execute('INSERT INTO session(session_id, user_id, username, role) VALUES (%s,%s,%s,%s)', (session_id, user['user_id'], username, role))
                            config.conn.commit()
                            
                        if session_id:
                            #generate token for session creation on cookies
                            token = generate_token(user['password'], user['pass_key'], session_id)
                            #register user to flask-login
                            login_user(User(session_id, username, user_role, token), remember=False)
                            #register login history
                            loginHistory(user['user_id'], session_id)
                            #return to page according to user roles
                            redirect_url = {1: 'admin.dashboard', 2: 'staff.records'}.get(user['role'], 'auth.logout')
                            if redirect_url:#redirect if user is authenicated and authorized
                                return redirect(url_for(redirect_url))
                            else:
                                error = invalidError
                        else:
                            error = invalidError
                    else:
                        error = invalidError
                else:
                    error = captchaError       
    return render_template('public/index.html', error_message=error, role = role, form=form)

#setup route for logout user 
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if current_user:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM session WHERE session_id = %s', (current_user.id,))
            user_session = cursor.fetchone()

            if user_session:
                cursor.execute('DELETE FROM session WHERE session_id = %s', (current_user.id,))
                config.conn.commit()
            else:
                print('Sign out error occurred')

            logout_user()
            session.clear()

    return redirect(url_for('home'))

#setup route for requesting heartbeat session status
@auth.route('/get_heartbeat/<username>', endpoint='heartbeat')
def heartbeat(username):
    if current_user and current_user.username == username:
        if current_user.is_authenticated and current_user.is_active:
            return jsonify(session_Inactive = False)
        else:
            print('timeout')
            if current_user.username:
                session_expired(username)
            return jsonify(session_Inactive = True)
    else:
        session_expired(username)
        return jsonify(session_Inactive = True)
    
#setup route for redirecting to logout to prevent expired CSRF token
@auth.route('/authenticate-user/check-token/timeout/')
def user_timeout():
    return redirect(url_for('auth.logout'))

# role format function
def get_role(role):
    if not role:
        return 0
    else:
        #if the input type is string use dictionary fixed values
        if isinstance(role, str) and len(role) > 1: 
            return {'admin': 1, 'staff':2}.get(role, 2)
        # convert it to integer instead   
        elif role in [1, 2 ,'1', '2']: 
            return int(role)
        
#check duplicate entries
def checkDuplicateAccount(user_id, credential, dataSearch):
    if not user_id and not credential and not dataSearch:
        return False
    else:
        user_id = int(user_id)
        credential = {'username': 'username', 'fullname': 'fullname'}.get(credential, 'fullname')

        # Initialize the query and parameters
        query = 'SELECT user_id FROM user WHERE 1=1'
        params = []

        # Add the appropriate condition to the query based on the credential
        if credential == 'username':
            query += ' AND username = %s'
            params.append(dataSearch)
        elif credential == 'fullname':
            query += ' AND fullname = %s'
            params.append(dataSearch)
        
        # Exclude the current user_id from the search
        if not user_id == 0:
            query += ' AND NOT user_id = %s'
            params.append(user_id)

        try:
            with config.conn.cursor() as cursor:
                # Execute the query
                cursor.execute(query, tuple(params))
                search_result = cursor.fetchone()

                # Return True if a duplicate account is found, False otherwise
                if search_result:
                    return True
                else:
                    return False

        except Exception as e:
            print(f"An error occurred while checking for duplicate accounts: {e}")

# dynamic update user data function
def updateAccount(user_id, fullname, username, role, password):
    # Initialize the query and parameters
    query = 'UPDATE user SET '
    params = []
    hasChanged = {}
    role = get_role(role) # Convert the role to its corresponding value
    pChecker = False
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()

            if not user:
                return 'userNotFound'
        
            else:
                if password != "":
                    pChecker = argon2.check_password_hash(user['password'], password)
                
                if user['fullname'] == fullname and user['username'] == username and user['role'] == role and pChecker:
                    return 'noChanges'
                
                else:
                    if user['fullname'] != fullname:
                        query += 'fullname = %s, '
                        params.append(fullname)
                        hasChanged.update({"fullname": fullname})

                    if user['username'] != username:
                        query += 'username = %s, '
                        params.append(username)
                        hasChanged.update({"username": username})

                    if user['role'] != role:
                        query += 'role = %s, '
                        params.append(role)
                        hasChanged.update({"role": role})

                        # If the password has changed, add it to the query and parameters
                    if password and not argon2.check_password_hash(user['password'], password):
                        query += 'password = %s, '
                        hashed_password = argon2.generate_password_hash(password)
                        params.append(hashed_password)
                        hasChanged.update({"password": hashed_password})

                    # Remove the trailing comma and space from the query
                    query = query.rstrip(', ')
                    query += ' WHERE user_id = %s'
                    params.append(user_id)
                        
                    # Execute the update query
                    cursor.execute(query, tuple(params))
                    config.conn.commit()

                    # Verify if the update was successful
                    keys_str = ', '.join(list(hasChanged.keys()))
                    verifyQuery = 'SELECT '+ keys_str + ' FROM user WHERE user_id = %s'
                    cursor.execute(verifyQuery, (user_id,))
                    user_update = cursor.fetchone()

                    if user_update == hasChanged:
                        return 'success'
                    else:
                        return 'failed'
                
    except Exception as e:
        print(f"updateAccount() : {e}")

def addNewUser( add_fullname, add_username, add_password):
    if not add_fullname and not add_username and not add_password:
        return 'failed'
    else:
        try:
            with config.conn.cursor() as cursor: 
                # Check if the username or fullname already exists
                usernameExists = checkDuplicateAccount(0, 'username', add_username)
                fullnameExists = checkDuplicateAccount(0, 'fullname', add_fullname)

                # If the username or fullname does not exist, proceed with adding the new user
                if not usernameExists and not fullnameExists:
                    h_password = argon2.generate_password_hash(add_password) # Generate a hashed password and a new pass_key
                    pass_key = generate_key()
                    role = 2 # Define the role and status for the new user

                    # Insert the new user data into the database
                    cursor.execute('INSERT INTO user (username, fullname, password, pass_key, role, status, online, last_online) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)',
                                (add_username, add_fullname, h_password, pass_key , role, 1, 0) )
                    config.conn.commit()
                    # Check if the user creation was successful
                    cursor.execute('SELECT user_id FROM user WHERE username = %s', (add_username))
                    insertSuccess = cursor.fetchone()

                    # Set the return value based on the success of the user creation
                    if insertSuccess:
                        data = 'success'
                    else:
                        data = 'failed'
                else:
                    data = 'duplicate'
                return data
            
        except Exception as e:
                print(f"addNewUser() : {e}")
                
#setup route for redirecting to logout to prevent expired CSRF token
@auth.route('/admin/user-manager/manage/data/new-user/data-credentials/register-account', methods=['POST', 'GET'])
@admin_required
def create_account():
    try:
        if request.method == "POST":
            fullname = request.form.get('newuser_fullname')
            username = request.form.get('newuser_username')
            password = request.form.get('newuser_password')
            re_password = request.form.get('newuser_repassword')
            
            if password == re_password:
                account_added = addNewUser(fullname, username, password)
                
                if account_added:
                    register_querry = account_added
                else:
                    register_querry = 'error'
            else:
                register_querry = 'incorrectPassword'
                
            return jsonify({'register_querry': register_querry})
            
    except Exception as e:
         print(f"create user route error occurred: {e}")

@auth.route('/admin/user-manager/manage/data/user/update/account-credentials/new-data', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_user():
    try:
        if request.method == "POST":
            user_id = request.form.get('update_user_id')
            fullname = request.form.get('update_fullname')
            username = request.form.get('update_username')
            role = request.form.get('update_role')
            password = request.form.get('update_password')
            re_password = request.form.get('update_repassword')

            if password == re_password:
                update_status = updateAccount(user_id, fullname, username, role, password)

                if update_status:
                    return jsonify({'update_query': update_status})
                else:
                    return jsonify({'update_query': 'error'})
            else:
                return jsonify({'update_query': 'incorrectPassword'})
                
    except Exception as e:
            print(f"update user credentials  error occurred: {e}")
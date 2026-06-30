from flask import current_app, render_template,redirect, request,url_for,flash
from sqlalchemy import func
from app.forms import RegistrationForm,LoginForm,BetForm,DepositForm,ForgotPasswordForm,ResetPasswordForm,BankForm,WithdrawForm
from app.models import User,Spin,Bet
from flask_login import login_user,current_user,logout_user
import threading
import time
from datetime import datetime,date
from app import db,socketIO,mail
import random
from flask_login import login_required

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

user_socket_map = {}

timer_running = False
timer_thread = None
thread_lock = threading.Lock()

current_spin_id = None
current_spin_result = None


# ✅ Password reset token functions
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

# Returns the email if the token is valid, otherwise returns None
def verify_reset_token(token, expiration=3600):  # Valid for (3600s) i.e. 1 hour
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except Exception as e:
        return None

def countdown(app):

    global timer_running,current_spin_id,current_spin_result
    while timer_running:

        #count up
        for number in range(0,11):
            if not timer_running:
                break
            socketIO.emit('timer_update',{
                'timer':number,
                'mode':'up'
            })

            time.sleep(1)
        #count down
        for number in range(10,-1,-1):
            if not timer_running:
                break
            socketIO.emit('timer_update',{
                'timer':number,
                'mode':'down'
            })

            if number == 10:

                print(f"New Spin created :")

                with app.app_context():
                    spin = Spin(result = "pending")

                    db.session.add(spin)
                    db.session.commit()

                    # 1. SAVE THE GENERATED ID TO THE GLOBAL VARIABLE
                    current_spin_id = spin.id

                    socketIO.emit('new_spin',{
                        'spin_id':current_spin_id
                    })

            if number == 2:
                print("Checking bets")

                with app.app_context():
                    bets = Bet.query.filter_by(spin_id = current_spin_id).all()

                    heads_total = 0
                    tails_total = 0

                    for bet in bets:
                        if bet.choice.lower() == "heads":
                            heads_total += bet.amount
                        elif bet.choice.lower() == "tails":
                            tails_total += bet.amount

                        print(f"Heads Total = {heads_total} | Tails Total = {tails_total}")

                    if heads_total > tails_total:
                        current_spin_result = "Tails"
                        print("Current Spin Result: Tails")
                    elif tails_total > heads_total:
                        current_spin_result = "Heads"
                        print("Current Spin Result: Heads")
                    else:
                        current_spin_result = random.choice(["Heads","Tails"])
                        print("It's a tie! Randomly selected result: ", current_spin_result )
                    # ✅ SEND THE REAL DECIDED RESULT NOW!
                    socketIO.emit('spin_animation', {
                        'result': current_spin_result
                    })

            if number == 0:
                print("Spin ended")
                # Here we will be checking the bets and updating the spin result
                with app.app_context():
                    spin = Spin.query.get(current_spin_id)
                    print(f"Spin Id: {current_spin_id } |" f"Result: {current_spin_result}")

                    if spin:
                        spin.result = current_spin_result
                        db.session.commit()

                        bets = Bet.query.filter_by(spin_id = current_spin_id).all()
                        total_bets = sum(int(bet.amount) for bet in bets)
                        total_winnings = 0

                        for bet in bets:
                            if bet.choice.lower() == current_spin_result.lower():
                                user = User.query.get(bet.user_id)
                                winnings = int(bet.amount) * 2
                                user.coins += winnings
                                total_winnings += winnings

                                sid = user_socket_map.get(user.id)
                                if sid:
                                    socketIO.emit('balance_update',{'coins' : user.coins},room = sid)
                        spin.profits = total_bets - total_winnings
                        db.session.commit()


                                

                        

                        recent_spin = Spin.query.filter(Spin.result != "pending").order_by(Spin.id.desc()).limit(6).all()

                        results = [spin.result for spin in recent_spin]

                        socketIO.emit('recent_spin_update',{'results':results})
            time.sleep(1)


def init_routes(app):

    @app.route('/init-db')
    def init_db():
        db.drop_all()
        db.create_all()
        return redirect(url_for('register'))
    @app.route('/',methods =['GET','POST'])
    @login_required
    def index():

        if not current_user.is_authenticated:
            return redirect(url_for('login'))


        form = BetForm()
        print(" Route Loaded")

        #get last 6 completed spins
        recent_spins = Spin.query.filter(Spin.result != "pending").order_by(Spin.id.desc()).limit(7).all()
        
        if request.method == 'POST':
            print("Post request received")
            choice = request.form.get('bet-choice')
            amount = request.form.get('bet-amount')
            current_spin_id = request.form.get('current-spin-id')
            user_id = current_user.id

            ballance = current_user.coins
            if (ballance < int(amount)):
                flash("Insufficient coins to place bet")
                return redirect(url_for('index'))


            new_bet = Bet(user_id = user_id,choice = choice,amount = amount,spin_id = current_spin_id)
            current_user.coins -= int(amount)

            db.session.add(new_bet)
            db.session.commit()
            print(f"Bet saved spin id: {new_bet.spin_id}, choice = {new_bet.choice}, amount ={new_bet.amount}")
            print(f"Successfully placed R{amount} on {choice}!")
            print('Bet added')

            
        
        return render_template('test.html',form = form,recent_spins = recent_spins)

    @app.route('/register',methods=['GET','POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if request.method== "POST":

            print("submit button pressed")
            username = form.username.data
            email = form.email.data
            cell = form.cellphone.data
            password = form.password.data
            age = form.age.data
            id_number = form.id_number.data
            gender = form.gender.data
            


            #check username
            existing_user = User.query.filter_by(username = username).first()
            if existing_user:
                flash('Username already exista',"error")
                return redirect(url_for('register'))


            #check email
            existing_email = User.query.filter_by(email = email).first()
            if existing_email:
                flash('email already exist',"error")
                return redirect(url_for('register'))



            #checkk cell number
            existing_cell = User.query.filter_by(cellphone = cell).first()
            if existing_cell:
                flash('Cell phone is taken',"error")
                return redirect(url_for('register'))


            #check Id_number
            existing_id = User.query.filter_by(id_number = id_number).first()
            if existing_id:
                flash('The ID number is taken',"error")
                return redirect(url_for('register'))


            #check password lenght
            if len(password)< 8:
                flash('Password must be atleast 8 charecters',"error")

                return redirect(url_for('register'))


            user = User(username = username,email = email,cellphone = cell,age = age,id_number = id_number,gender = gender,role= "user",coins = 50)

            user.set_password(password)
            try:
                db.session.add(user)
                db.session.commit()
                print("Account created successfully Login","success")
                return redirect(url_for('login'))
            except:
                db.session.rollback()
                print( 'an error happened')
        return render_template('register.html',form = form)

    @app.route('/terms')
    def terms():
        return render_template('terms.html')
    @app.route('/deposit')
    def deposit():
        return render_template('deposit.html')
    @app.route('/withdraw',methods = ['GET','POST'])
    def withdraw():
        form = WithdrawForm()
        if form.validate_on_submit():
            amount = form.amount.data

            if amount > current_user.coins:
                flash(f'Insufficient balance,','error')
                # return redirect(url_for(deposit))
                return redirect(url_for('withdraw'))

            try:
                msg = Message(
                    subject=f'Zwipi withdrawal request for User {current_user.id}',
                    sender='thembamaseko1990@gmail.com',
                    recipients= ['zimomaseko@gmail.com']
                )
                msg.body = f"""
                            New withdrawal request received on Zwipi,
                            User ID : {current_user.id}
                            Username: {current_user.username}
                            Amount : R{amount:.2f}
                            Balance: R{current_user.coins:.2f}
                            Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
                            Please log into the admin panel to review and process this request
                            """.strip()
                mail.send(msg)
                current_user.coins = current_user.coins - amount
                db.session.commit

                flash('Your withdrawla request has been submitted','success')
            except Exception as e:
                flash('Request recieved but email sending failed please contact Support','error')
                return redirect(url_for(withdraw))

        return render_template('withdraw.html',form = form)
    
    @app.route('/profile')
    @login_required
    def profile():
        # Query the last 10 bets made by this specific user
        # We use a join so the template can easily access spin data (like the final result)
        past_bets = db.session.query(Bet).filter(Bet.user_id == current_user.id).order_by(Bet.id.desc()).limit(10).all()
        print(f"User {current_user.username} has {len(past_bets)} past bets.")

        spins = {}
        for bet in past_bets:
            if bet.spin_id:
                spins[bet.spin_id] = Spin.query.get(bet.spin_id)            
        
        return render_template('profile.html', user=current_user, bets= past_bets,spins=spins)

    @app.route('/login',methods = ['GET','POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                flash("Username and Password do not match","error")
                return redirect("/login")
            login_user(user)
            return redirect(url_for("index"))
        return render_template('login.html',form = form)

    @app.route('/addcoins/<int:id>',methods = ['GET','POST'])
    @login_required
    def addcoins(id):
        if current_user.username != "sudo Zee" or current_user.role != "admin":
            return redirect(url_for("e404"))
        form = DepositForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                user = User.query.filter_by(id = id).first()
                user.coins = form.deposit_amount.data
                db.session.commit()
                flash('Updated successfully')
                return redirect(url_for('admin'))

        return render_template('addcoins.html',form = form,user = user)


    @app.route('/404')
    def e404():
        return render_template('404.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out')
        return redirect(url_for("login"))
    
    @app.route('/fogort',methods = ['GET','POST'])
    def fogort():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = ForgotPasswordForm()
        email = form.email.data
        if form.validate_on_submit():
            user = User.query.filter_by(email= email).first()

            #we need an if user:
            try:
                # Generate Reset Token
                token = generate_reset_token(email)
                reset_link = url_for('reset_pass', token=token, _external=True)

                # Send Email
                msg = Message('Password Reset Request', sender='noreply@zwipionline.com', recipients=[user.email])
                msg.body = f'Click the link to reset your password: {reset_link}'
                mail.send(msg)

                flash('Password reset link has been sent to your email!', 'success')
                print(f'password reset link send with token')
            except Exception as e:
                print(e)
                flash('An error occurred while sending email. Please try again.', 'error')
           

        return render_template('fogort.html',form = form)

    @app.route('/reset_password/<token>',methods = ['GET','POST'])
    def reset_pass(token):
        form = ResetPasswordForm()

        email = verify_reset_token(token)

        if not email:
            flash('invalid or expired token')
            return redirect(url_for('login'))
        

        if form.validate_on_submit():
            new_password = form.password.data
            confirm = form.confirm_password.data
            if new_password != confirm:
                flash('Passwords dont match try again')
                return redirect(url_for('reset_pass', token=token)) 
            user = User.query.filter_by(email=email).first()
            user.set_password(new_password) 

            db.session.commit()
            flash('Password successfully updated')
            return redirect(url_for('login'))

        return render_template('reset.html',form = form)

    @app.route('/admin',methods = ['GET','POST'])
    @login_required
    def admin():
        if current_user.username == "Sudo" or current_user.role == "admin":
            if request.method == "POST":
                user_id = request.form.get("user_id")
                user = User.query.get(user_id)
                if user:
                    user.role = "admin"
                    db.session.commit()
                    return redirect(url_for("admin"))
            user = User.query.all()
            recent_spins = Spin.query.filter(Spin.result != "pending").order_by(Spin.id.desc()).limit(6).all()
            bets = Bet.query.all()

            # get all registers users
            toatal_users = User.query.count()

            # stats of all user coins
            total_coins = db.session.query(db.func.sum(User.coins)).scalar() or 0

            today_8am = datetime.combine(date.today(), datetime.min.time()).replace(hour=8)
            total_profit = db.session.query(db.func.sum(Spin.profits)).filter(Spin.created >= today_8am, Spin.result != "pending").scalar() or 0
        else:
            return redirect(url_for('e404'))
           
        return render_template('admin.html', users = user,spins = recent_spins, bets = bets, total_users = toatal_users, total_coins = total_coins, total_profit = total_profit)

    @app.route('/bank',methods = ['GET','POST'])
    @login_required
    def bank():
        if current_user.username == "sudo Zee" or current_user.role == "admin":
           
            form = BankForm()
            user = None

            id = 2128
            spin = Spin.query.get(id)
            # print(f"Spin ID: {spin.id} | Result: {spin.result} | Profits: {spin.profits} | Created: {spin.created}")
            
            # Pull the phone from previous steps if a form was submitted, 
            # so the user remains visible on-screen during balance adjustments
            # 1. Always look up the user first if a phone number was submitted
            cellphone = request.form.get('phone') or form.phone.data
            user = None

            if cellphone:
                # CRITICAL FIX: Changed id=phone_number to phone_number=phone_number
                # (Adjust 'phone_number=' to match the exact column name in your User model)
                user = User.query.filter_by(cellphone=cellphone).first()

            if form.validate_on_submit():
        
                # Action 1: Searching for the user
                if form.search.data:
                    if not user:
                        flash('No user found with that cellphone number.', 'error')
                    else:
                        flash(f"User {user.username} found with {user.coins} coins.", "info")
                elif form.add.data:
                    if user:
                        amount = form.amount.data or 0
                        user.coins += int(amount)
                        db.session.commit()
                        flash(f'Successfully added {amount} coins to {user.username}.', 'success')
                    sid = user_socket_map.get(user.id)
                    if sid:
                        socketIO.emit('balance_update', {'coins': user.coins}, room=sid)
                    else:
                        flash('Please search for a valid user by phone number first.', 'error')

                elif form.deduct.data:
                    if user:
                        amount = form.amount.data or 0
                        if user.coins < int(amount):
                            flash(f'Cannot deduct. User only has {user.coins} coins.', 'error')
                        else:
                            user.coins -= int(amount)
                            db.session.commit()
                            flash(f'Successfully deducted {amount} coins from {user.username}.', 'success')
                            
                            # Push immediate live update to the user's frontend UI if they are online
                            sid = user_socket_map.get(user.id)
                            if sid:
                                socketIO.emit('balance_update', {'coins': user.coins}, room=sid)
                    else:
                        flash('Please search for a valid user by phone number first.', 'error')
        else:
            return redirect(url_for('e404'))

       
        return render_template('bank.html',form = form, user = user)
    @socketIO.on('connect')
    def handle_connect():
        print ('client connected')
        # Map the current authenticated user's ID to their unique session connection ID
        user_socket_map[current_user.id] = request.sid
        socketIO.emit('new_spin',{'spin_id': current_spin_id})

        socketIO.emit('balance_update', {'coins': current_user.coins}, room=request.sid)
        socketIO.emit('new_spin', {'spin_id': current_spin_id}, room=request.sid)
        # Send the active spin ID to the user who just connected
        socketIO.emit('new_spin', {'spin_id': current_spin_id})

    @socketIO.on('place_bet')
    def place_bet(data):
        new_bet = Bet(
            user_id = current_user.id,
            choice = data["choice"],
            amount=data["amount"],
            spin_id = data["spin_id"]
        )
        current_user.coins -= int(data["amount"])
        db.session.add(new_bet)
        db.session.commit()

        sid = user_socket_map.get(current_user.id)
        if sid:
            socketIO.emit(
                "balance_update",
                {"coins": current_user.coins},room = request.sid
            )
    @socketIO.on('check')
    def handle_check():
        # here we will be checking the bets table and display the result
        print ("Checking bets")

    @socketIO.on('start_timer')
    def handle_start():
        print('timer started')

        global timer_running
        global timer_thread
        with thread_lock:
            if not timer_running:
                timer_running = True

                timer_thread = threading.Thread(target=countdown, args=(app,))
                timer_thread.daemon = True
                timer_thread.start()

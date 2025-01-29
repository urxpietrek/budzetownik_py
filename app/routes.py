from flask import (
    render_template,
    redirect, url_for,
    request,
    flash,
    session,
    Blueprint,
    jsonify)

from utils.charts import create_charts

from flask_bcrypt import Bcrypt
from .models import User, Expense, Goal, db

import os
from datetime import date, datetime

import matplotlib
matplotlib.use('Agg')

PASSWORD_SECURITY_SALT = os.environ.get('PASSWORD_SECURITY_SALT', 'TESTOWE')

bp = Blueprint('routes', __name__)
bcrypt = Bcrypt()

@bp.route('/')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        try: 
            user = User.query.filter_by(id=user_id).one()
        except:
            session.clear()
            return redirect(url_for('routes.login'))
        expenses = Expense.query.filter_by(user_id=user_id).all()
        goals = Goal.query.filter_by(user_id=user_id).all()
        expense_list = [
            {
                'id': exp.id,
                'category': exp.category,
                'amount': exp.amount,
                'date': exp.date
            }
            for exp in expenses
        ]
        
        goal_list = [
            { 
                "id": goal.id,
                "name": goal.name,
                "saved_amount": goal.saved_amount,
                "target_amount": goal.target_amount
            }
            for goal in goals
        ]
        

        pie_chart, bar_chart = create_charts(expenses=expenses)
        return render_template('dashboard.html',
                               user=user,
                               expenses=expense_list,
                               goals=goal_list,
                               chart_pie = pie_chart,
                               chart_bar = bar_chart)
    return redirect(url_for('routes.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('routes.register'))
        
        hashed_password = bcrypt.generate_password_hash(password + PASSWORD_SECURITY_SALT)
        new_user = User(username=username, password=hashed_password, email=email)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('routes.login'))
        except:
            flash('Username already exists!', 'danger')

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password + PASSWORD_SECURITY_SALT):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('routes.home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('routes.login'))

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                hashed_password = bcrypt.generate_password_hash(new_password + PASSWORD_SECURITY_SALT)
                user.password = hashed_password
                db.session.commit()
                flash('Password reset successful. Please log in.', 'success')
                return redirect(url_for('routes.login'))
            else:
                flash('Passwords do not match.', 'danger')
        else:
            flash('Email not found.', 'danger')

    return render_template('reset_password.html')

@bp.route('/add-expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('routes.login'))

    try:
        category = request.form['category']
        if category == 'Other':
            category = request.form['custom_category']
            
        exp_date = request.form['date'] or date.today()    
        if isinstance(exp_date, str):
            exp_date = datetime.strptime(exp_date,'%Y-%m-%d')
    except:
        flash("Wystąpił błąd. Spróbuj ponownie.", 'danger')
        return redirect(url_for('routes.home'))
    
    try:
        amount = float(request.form['amount'])
        if amount < 0:
            flash("Koszt nie może być ujemny.", 'danger')
            return redirect(url_for('routes.home'))
    except:
        flash('Nie można dodać pustego kosztu!', 'danger')
        return redirect(url_for('routes.home'))
    else:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).one()
        
    if amount <= user.balance:
        new_expense = Expense(user_id=session['user_id'], category=category, amount=amount, date=exp_date)
        user.balance -= amount
        
        db.session.add(new_expense)
        db.session.commit()
    else:
        
        flash('Nie masz wystarczającego salda do kwoty', 'danger')
        return redirect(url_for('routes.home'))
        
    flash('Wydatek został dodany!', 'success')
    return redirect(url_for('routes.home'))

@bp.route('/add-balance', methods=['POST'])
def add_balance():
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('routes.login'))

    amount = float(request.form['amount'] or 0) 
    if amount < 0:
        flash("Kwota nie może być ujemna.", 'danger')
        return redirect(url_for('routes.home'))

    user = User.query.get(session['user_id'])
    user.balance += amount
    db.session.commit()

    flash('Saldo zostało zaktualizowane!', 'success')
    return redirect(url_for('routes.home'))


@bp.route('/add-goal', methods=['POST'])
def add_goal():
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('routes.login'))

    name = request.form['name']
    
    try:
        target_amount = float(request.form['target_amount'])
        
        if target_amount < 0:
            flash("Kwota nie może być ujemna.", 'danger')
            return redirect(url_for('routes.home'))
    except:
        flash('Nie można utworzyć tego celu oszczędnościowego!', 'danger')
        return redirect(url_for('routes.home'))

    new_goal = Goal(user_id=session['user_id'], name=name, target_amount=target_amount, saved_amount=0)
    db.session.add(new_goal)
    db.session.commit()

    flash('Cel oszczędnościowy został dodany!', 'success')
    return redirect(url_for('routes.home'))

@bp.route('/allocate-to-goal', methods=['POST'])
def allocate_to_goal():
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('routes.login'))

    goal_id = request.form['goal_id']
    amount = float(request.form['amount'] or 0)
    user_id = session['user_id']
    
    user = User.query.filter_by(id=user_id).one()
    goal = Goal.query.filter_by(id=goal_id).one()
    
    if not goal or goal.user_id != user.id:
        flash('Nie znaleziono celu lub nie masz do niego dostępu.', 'danger')
        return redirect(url_for('routes.home'))

    if amount > user.balance:
        flash('Nie masz wystarczających środków na saldzie!', 'danger')
    else:
        user.balance -= amount
        goal.saved_amount += amount
        db.session.commit()
        flash(f'Przeznaczono {amount} PLN na cel "{goal.name}"!', 'success')

    return redirect(url_for('routes.home'))

@bp.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
    return redirect(url_for('routes.home'))

@bp.route('/delete_goal/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal:
        db.session.delete(goal)
        db.session.commit()
    return redirect(url_for('routes.home'))

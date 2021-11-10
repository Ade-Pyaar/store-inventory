from flask import render_template, redirect, url_for, flash, request
from store_inventory.models import User, Product
from store_inventory.forms import Loginform, Regform, Updateform, RequestResetForm, ResetPasswordForm
from store_inventory import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from flask_paginate import Pagination, get_page_args
from string import ascii_uppercase
import os



if not os.path.exists("inventory.db"):
    db.create_all()




@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('all_products'))
    form = Regform()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, password=hashed_password,)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.name.data}, you can now login ", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)






@app.route('/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_products'))
    form = Loginform()
    if form.validate_on_submit():

        user = User.query.filter_by(name=form.name.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome {form.name.data}!", 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('all_products'))
        else:
            flash('Login unsuccessful, please check the name and password', 'danger')
    return render_template('login.html', title='Login', form=form)






@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))






@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = Updateform()
    if form.validate_on_submit():

        user = User.query.filter_by(name=current_user.name).first()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        if current_user.name == form.name.data and current_user.password != hashed_password:
            User.query.filter_by(name=current_user.name).update({User.password: hashed_password})

        elif current_user.name != form.name.data and current_user.password != hashed_password:
            User.query.filter_by(name=current_user.name).update({User.name: form.name.data, User.password: hashed_password})

        elif current_user.name != form.name.data and current_user.password == hashed_password:
            User.query.filter_by(name=current_user.name).update({User.name: form.name.data}) 
        
        db.session.commit()

        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
        
    elif request.method == 'GET':
        form.name.data = current_user.name
    return render_template('account.html', title='Account', form=form)






@app.route('/account/delete/')
@login_required
def delete_account():

    user = User.query.filter_by(name=current_user.name).first()
    db.session.delete(user)
    db.session.commit()

    flash('The account has been deleted', 'success')
    return redirect(url_for('login'))




@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('all_products'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        return redirect(url_for('reset_token', token=user.name))
    return render_template('reset_request.html', title='Reset Password', form=form)






@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('all_products'))
    user = User.query.filter_by(name=token).first()

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)






@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():    

    if request.method == "POST":
        length = int(len(request.form) / 3)
        counter = 0

        for i in range(1, length+1):
            if len(request.form.get('name'+str(i))) != 0:
                item = Product(name=request.form.get('name'+str(i)).capitalize().replace('\\', '/').replace('\'', '').replace('\"', ''),
                                quantity=request.form.get('quantity'+str(i)),
                                price=request.form.get('price'+str(i)))
                db.session.add(item)
                counter += 1

        db.session.commit()
        # db.session.close()
        flash(f"{counter} Product(s) Entered", 'success')
    return render_template('new_product.html', title='Add a new product')






@app.route('/all_products')
@login_required
def all_products():

    all_products = Product.query.order_by(Product.name)
    
    product_list = [item.name for item in all_products]

    letter = request.args.get('letter', "#", type=str)
    all_letters = [i for i in ascii_uppercase]
    all_letters.insert(0, '#')
    if letter == '#':
        letter_product = Product.query.order_by(Product.name).filter(Product.name.startswith(''))
    else:
        letter_product = Product.query.order_by(Product.name).filter(Product.name.startswith(letter))

    final_product = [i.name for i in letter_product]

    page, per_page, _ = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 50

    pagination = Pagination(page=page, per_page=per_page, total=len(final_product), css_framework='bootstrap3')

    try:
        sample_sales = final_product[(page-1)*per_page:(page)*per_page]

    except IndexError:
        sample_sales = final_product[page*per_page:] 
    
    num_product = len(product_list)


    return render_template('all_products.html', title='All Product', all_letters=all_letters, current_letter=letter, num_product=num_product, per_page=per_page, pagination=pagination, page=page, sample_sales=sample_sales, product_list=product_list)






@app.route('/product/edit/', methods=['GET', 'POST'])
@login_required
def edit_product():

    product_name = request.args.get('name', '', type=str)

    product = Product.query.filter_by(name=product_name).first()

    if request.method == "POST":
        id = request.form.get('id')
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')

        update_dict = {Product.name:name, Product.quantity:quantity, Product.price:price}

        Product.query.filter_by(id=id).update(update_dict)
        db.session.commit()

        flash('You have successfully updated the details', 'success')
        return redirect(url_for('all_products'))

    return render_template('edit_product.html', title='Edit Product', product=product)





@app.route('/search', methods=["POST", "GET"])
@login_required
def search():
    if request.method == "POST":
        search_text = request.form.get("search_text")

        return url_for('edit_product', name=search_text)






@app.route("/product/delete/", methods=['POST', 'GET'])
@login_required
def delete_product():
    product_name = request.args.get("name", '', type=str)

    product = Product.query.filter_by(name=product_name).first()
    
    db.session.delete(product)
    db.session.commit()

    flash("The product have been deleted successfully", "success")
    return redirect(url_for("all_products"))
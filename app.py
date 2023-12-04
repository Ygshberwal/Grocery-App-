from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__)
db = SQLAlchemy()
bcrypt=Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database.sqlite3"
app.config['SECRET_KEY'] = 'thisisasecretkey'
db.init_app(app)
app.app_context().push()


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#DataBase
class User(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20), nullable=False, unique=True)
    password=db.Column(db.String(80), nullable=False)
    cart_item=db.relationship('Cart', backref='user')

class Manager(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20), nullable=False, unique=True)
    password=db.Column(db.String(80), nullable=False)

class Categories(db.Model, UserMixin):    
    category_id=db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(20),nullable=False,unique=True)
    c_products = db.relationship('Products',backref="p_category")
    
class Products(db.Model,UserMixin):
    product_id=db.Column(db.Integer,primary_key=True)
    product_name=db.Column(db.String(20),nullable=False, unique=True)
    product_unit=db.Column(db.String(10),nullable=False)
    product_rate=db.Column(db.Integer,nullable=False)
    product_quantity=db.Column(db.Integer,nullable=False)
    p_category_id=db.Column(db.Integer(),db.ForeignKey("categories.category_id"), nullable=False)
      
class Cart(db.Model):
    cart_id = db.Column(db.Integer(),primary_key=True)
    cart_name=db.Column(db.String() , nullable=False)
    cart_rate =db.Column(db.Integer() , nullable=False)
    cart_quantity = db.Column (db.Integer(), nullable=False)
    cart_totalprice = db.Column (db.Integer(), nullable=False)
    cart_user = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)


#login
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


#Routes
@app.route('/')
def home():
    return render_template("home.html")

#userlogin
@app.route('/login', methods=['POST','GET'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                session['user_id']=user.id
                return redirect(url_for('user_dashboard'))
            
    return render_template("login.html",form=form)

#userregister
@app.route('/register', methods=['POST','GET'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("register.html",form=form)

#manager register
@app.route('/manager_register', methods=['POST','GET'])
def manager_register():
    form=RegisterForm()
    if form.validate_on_submit():
        #hashed_password=bcrypt.generate_password_hash(form.password.data)
        new_manager=Manager(username=form.username.data, password=form.password.data)
        db.session.add(new_manager)
        db.session.commit()
        return redirect(url_for('manager_login'))

    return render_template("manager_register.html",form=form)

#manager login
@app.route('/manager_login', methods=['POST','GET'])
def manager_login():
    form=LoginForm()
    if form.validate_on_submit():
        manager=Manager.query.filter_by(username=form.username.data).first()
        if manager:
            if (manager.password==form.password.data):
                login_user(manager)
                return redirect(url_for('manager_dashboard'))
    return render_template("manager_login.html",form=form)


#user dashboard
@app.route('/user_dashboard', methods=['POST','GET'])
@login_required
def user_dashboard():
    category = Categories.query.all()
    product=Products.query.all()
    #products = Products.query.filter_by(p_category_id=category_id).all()
    return render_template("user_dashboard.html",category=category,product=product)

#manager dashboard
@app.route('/manager_dashboard', methods=['POST','GET'])
@login_required
def manager_dashboard():
    category = Categories.query.all()
    product=Products.query.all()
    return render_template("manager_dashboard.html",category=category,product=product)


@app.route('/logout', methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



#manager login crud operations

#create category
@app.route('/create' , methods = ['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('createpage.html')
 
    if request.method == 'POST':
        cat = request.form['category_name']
        # Check if a category with the same name already exists
        existing_category = Categories.query.filter_by(category_name=cat).first()
        if existing_category:
            return redirect('/create')
        
        category = Categories(
            category_name=cat        
        )
        db.session.add(category)
        db.session.commit()
        return redirect('/manager_dashboard')

#category list
@app.route('/list')
def RetrieveList():
    category = Categories.query.all()
    return render_template('datalist.html',category = category)

#delete category
@app.route('/<int:category_id>/cdelete', methods=['GET','POST'])
def cdelete(category_id):
    cats = Categories.query.filter_by(category_id=category_id).first()
    if request.method == 'POST':
        if cats:
            db.session.delete(cats)
            db.session.commit()
            return redirect('/manager_dashboard')
    return render_template('delete.html')

#edit category
@app.route('/<int:category_id>/cedit', methods=['GET', 'POST'])
def cedit(category_id):
    cats = Categories.query.filter_by(category_id=category_id).first()

    if request.method == 'POST':
        c_name = request.form['category_name']
        if cats:
            cats.category_name=c_name
            db.session.commit()       
            return redirect('/manager_dashboard')
        
    return render_template('createpage.html', cats=cats)

#product list in category
@app.route('/<int:category_id>/products', methods=['GET', 'POST'])
def show_products(category_id):
    products = Products.query.filter_by(p_category_id=category_id).all()
    return render_template("productlist.html",products=products)


#add product
@app.route('/<int:category_id>/add', methods=['GET', 'POST'])
def add(category_id):
    category = Categories.query.get(category_id)
    if not category:
        return redirect('/manager_dashboard')

    if request.method == 'POST':
        p_name = request.form['product_name']
        existing_prod = Products.query.filter_by(product_name=p_name).first()
        if existing_prod:
            return render_template('create_product.html', category=category)

        product_name = request.form['product_name']
        product_unit = request.form['product_unit']
        product_rate = request.form['product_rate']
        product_quantity = request.form['product_quantity']

        prod = Products(
            product_name=product_name,
            product_unit=product_unit,
            product_rate=product_rate,
            product_quantity=product_quantity,
            p_category=category  # Associate the product with the category
        )
        db.session.add(prod)
        db.session.commit()
        return redirect('/manager_dashboard')

    return render_template('create_product.html', category=category)

# edit product   
@app.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit(product_id):
    existing_prod=Products.query.get(product_id)
    if not existing_prod:
        return redirect('/manager_dashboard')

    if request.method == 'POST':
        p_name = request.form['product_name']
        p_rate=request.form['product_rate']
        quantity_increase=0
        if request.form['product_quantity']:
            quantity_increase = int(request.form['product_quantity'])
        
        
        if existing_prod:
            if p_name:
                existing_prod.product_name=p_name
            if p_rate:
                existing_prod.product_rate=p_rate
            if quantity_increase:
                existing_prod.product_quantity += quantity_increase
            db.session.commit()
            return redirect('/manager_dashboard')
        
    return render_template('update.html', existing_prod=existing_prod)


#delete product
@app.route('/<int:product_id>/delete', methods=['GET','POST'])
def delete(product_id):
    pod = Products.query.get(product_id)
    if request.method == 'POST':
        if pod:
            db.session.delete(pod)
            db.session.commit()
            return redirect('/manager_dashboard')
    return render_template('delete.html')



#buy items
@app.route('/<int:product_id>/buy', methods=['GET', 'POST'])
def buy(product_id):
    pod = Products.query.get(product_id)

    user_id = session.get('user_id')
    user_obj= User.query.filter_by(id=user_id).first()
    cart_user=user_obj.username
    
    if request.method=="GET":        
        return render_template('buy.html', pod=pod, cart_user=cart_user)
    if user_id:
        if request.method == 'POST':
            quantity = int(request.form['quantity'])
            cart_name=pod.product_name
            cart_rate=pod.product_rate
            cart_totalprice=quantity*cart_rate
  
            if pod and quantity > 0 and quantity<=pod.product_quantity:
                c=Cart(
                    cart_name=cart_name,
                    cart_rate=cart_rate,
                    cart_quantity=quantity,
                    cart_totalprice=cart_totalprice,
                    cart_user=cart_user
                )

                db.session.add(c)

                pod.product_quantity-=quantity

                db.session.commit()
                return redirect('/user_dashboard')
        else:
            return redirect("/login")
            

    # return render_template('buy.html', pod=pod, cart_user=cart_user)


#remove item from cart
@app.route('/<int:cart_id>/remove', methods=['GET','POST'])
def remove(cart_id):
    item=Cart.query.get(cart_id)
    if request.method=='POST':
        if item:
            prod=Products.query.filter_by(product_name=item.cart_name).first()
            prod.product_quantity+=item.cart_quantity
            db.session.delete(item)
            db.session.commit()

            return redirect('/cart')
        
    return render_template("remove.html")

#user cart
@app.route('/cart', methods=['GET', 'POST'])
def cart():

    user_id = session.get('user_id')
    user_obj= User.query.filter_by(id=user_id).first()
    cart_user=user_obj.username

    cart=Cart.query.filter_by(cart_user=cart_user)
    grand_total = 0
    for item in cart:
        grand_total+=item.cart_totalprice

    
    if request.method == 'POST':
        session.pop('cart', None)
        return redirect('/user_home')
    
    return render_template('cart.html', cart=cart, grand_total=grand_total)

#search in manager
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    
    if not query:
        return redirect('/manager_dashboard')
    product = Products.query.filter(Products.product_name.ilike(f'%{query}%')).all()
    category = Categories.query.filter(Categories.category_name.ilike(f'%{query}%')).all()
    # price = Products.query.filter(Products.p_rate.ilike(f'%{query}%')).all()
    
    return render_template('manager_dashboard.html', category=category, product=product)


#search in user
@app.route('/searchh', methods=['GET'])
def searchh():
    query = request.args.get('query', '').strip()
    
    if not query:
        return redirect('/user_dashboard')
    
    categories = Categories.query.filter(Categories.category_name.ilike(f'%{query}%')).all()
    products = Products.query.filter(Products.product_name.ilike(f'%{query}%')).all()
    
    return render_template('user_dashboard.html', category=categories, product=products)

#thank you note
@app.route('/user_home')
def thanku():
    return render_template("user_home.html")

if __name__=="__main__":
    app.run(debug=True)

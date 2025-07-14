from flask import *
import uuid, time, datetime
import flask_sqlalchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

db = flask_sqlalchemy.SQLAlchemy(app)

#region Models

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    singular = db.Column(db.String(50), nullable=False)
    plural = db.Column(db.String(50), nullable=False)
    items = db.relationship('Item', backref=db.backref('type', lazy=True))
    def __repr__(self):
        return f'<Type {self.singular}, {self.plural}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    text = db.Column(db.Text, nullable=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)
    identifier = db.Column(db.String(50), nullable=False)
    def __repr__(self):
        return f'<Item {self.title}>'

#endregion

token_storage = {}
admin_storage = {}
EXPIRATION_TIME = 3600  # 1 hour expiration time

@app.before_request
def before_request():
    if request.path == '/login' or request.path == '/admin':
        return

    token = request.cookies.get('access_token')
    
    if not token:
        # No hay token, generamos uno nuevo y lo guardamos con la fecha actual y timestamp
        token = str(uuid.uuid4())
        hoy_str = datetime.datetime.now().strftime("%d-%m-%Y")
        token_storage[token] = (hoy_str, time.time())
        
        res = make_response(redirect(request.path))  # redirigimos a la misma ruta para que continúe
        res.set_cookie('access_token', token, max_age=EXPIRATION_TIME)
        return res
    
    if token in token_storage:
        # Revisamos si el token expiró
        fecha_guardada, last_time = token_storage[token]
        if time.time() - last_time > EXPIRATION_TIME:
            # Token expiró: eliminar y forzar nuevo token en próxima request
            del token_storage[token]
            res = make_response(redirect(request.path))
            res.set_cookie('access_token', '', expires=0)
            return res
        else:
            # Renovamos el timestamp para que expire 1 hora desde esta acción
            token_storage[token] = (fecha_guardada, time.time())
    else:
        # Token no reconocido: crear nuevo token y cookie
        token = str(uuid.uuid4())
        hoy_str = datetime.datetime.now().strftime("%d-%m-%Y")
        token_storage[token] = (hoy_str, time.time())
        res = make_response(redirect(request.path))
        res.set_cookie('access_token', token, max_age=EXPIRATION_TIME)
        return res

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
            token = str(uuid.uuid4())
            admin_storage[token] = (True, time.time())
            
            res = make_response(redirect('/admin'))
            res.set_cookie('admin_token', token, max_age=EXPIRATION_TIME)
            return res
        else:
            return render_template('login.html')

    if request.method == 'GET':
        if request.cookies.get('admin_token') in admin_storage and admin_storage[request.cookies.get('admin_token')][0]:
            return redirect('/admin')
        return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.cookies.get('admin_token') not in admin_storage or not admin_storage[request.cookies.get('admin_token')][0]:
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('admin.html', types=Type.query.all(), items=Item.query.all())
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date = datetime.datetime.now()
        type = request.form.get('type')
        text = request.form.get('text')
        identifier = request.form.get('identifier')

        type_id = Type.query.filter_by(singular=type).first().id if type else None

        if None in [title, type, text, description, identifier]:
            return render_template('admin.html', error="Todos los campos son obligatorios", types=Type.query.all(), items=Item.query.all())
        
        new_item = Item(title=title, description=description, date=date, text=text, type_id=type_id, identifier=identifier)
        db.session.add(new_item)
        db.session.commit()

        return redirect('/admin')

@app.route('/', methods=['GET'])
def home():
    token = request.cookies.get('access_token')

    date = datetime.datetime.now() if not token else datetime.datetime.strptime(token_storage.get(token, (datetime.datetime.now().strftime("%d-%m-%Y"), time.time()))[0], "%d-%m-%Y")

    return render_template('index.html', 
                           current_year=date.year, 
                           current_month=date.month, 
                           current_day=date.day, 
                           calendar_month=date.month, 
                           calendar_year=date.year,
                           items=Item.query.filter_by(date=date.date()).all(),
                           types=Type.query.all())

@app.route('/text/<id>', methods=['GET'])
def text(id):
    if not id:
        return abort(404)
    
    if Item.query.filter_by(id=id).count() == 0:
        return abort(404)
    
    item = Item.query.filter_by(id=id).first()

    token = request.cookies.get('access_token')

    date = datetime.datetime.now() if not token else datetime.datetime.strptime(token_storage.get(token, (datetime.datetime.now().strftime("%d-%m-%Y"), time.time()))[0], "%d-%m-%Y")

    return render_template('text.html', 
                           current_year=date.year, 
                           current_month=date.month, 
                           current_day=date.day, 
                           calendar_month=date.month, 
                           calendar_year=date.year, 
                           data=item
                           )

@app.route('/update/<date>', methods=['GET'])
def update_date(date):
    token = request.cookies.get('access_token')
    token_storage[token] = (date, time.time())

    res = make_response(redirect("/"))
    res.set_cookie('access_token', token, max_age=EXPIRATION_TIME)
    return res

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True, port=80)
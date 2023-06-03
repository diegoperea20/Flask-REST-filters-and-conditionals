from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypassword@localhost:3306/flaskmysql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# tables 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))

    def __init__(self, title, description):
        self.title = title
        self.description = description


class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    country = db.Column(db.String(100))

    def __init__(self, first_name, last_name, age, country):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.country = country


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))

    def __init__(self, item, amount, customer_id):
        self.item = item
        self.amount = amount
        self.customer_id = customer_id


class Shipping(db.Model):
    shipping_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))

    def __init__(self, status, customer_id):
        self.status = status
        self.customer_id = customer_id



with app.app_context():
    db.create_all()

# shemas 

class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description')


class CustomerSchema(ma.Schema):
    class Meta:
        fields = ('customer_id', 'first_name', 'last_name', 'age', 'country')


class OrderSchema(ma.Schema):
    class Meta:
        fields = ('order_id', 'item', 'amount', 'customer_id')


class ShippingSchema(ma.Schema):
    class Meta:
        fields = ('shipping_id', 'status', 'customer_id')


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

shipping_schema = ShippingSchema()
shippings_schema = ShippingSchema(many=True)

#routes

@app.route('/tasks', methods=['POST'])
def create_task():
    title=request.json['title']
    description=request.json['description']

    new_task=Task(title, description)
    db.session.add(new_task)
    db.session.commit()
    return task_schema.jsonify(new_task)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    all_tasks=Task.query.all()
    result=tasks_schema.dump(all_tasks)
    return jsonify(result)                    

@app.route('/tasks/<id>', methods=['GET'])
def get_task(id):
    task=Task.query.get(id)
    return task_schema.jsonify(task) 

@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    task=Task.query.get(id)
    title=request.json['title']
    description=request.json['description']

    task.title=title
    task.description=description
    db.session.commit()
    return task_schema.jsonify(task)


@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task=Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return task_schema.jsonify(task)


#customers
@app.route('/customers', methods=['POST'])
def create_customer():
    first_name=request.json['first_name']
    last_name=request.json['last_name']
    age=request.json['age']
    country=request.json['country']
    customer_new=Customer(first_name, last_name, age, country)
    db.session.add(customer_new)
    db.session.commit()
    return customer_schema.jsonify(customer_new)

@app.route('/customers', methods=['GET'])
def get_customers():
    all_customers=Customer.query.all()
    result=customers_schema.dump(all_customers)
    return jsonify(result)

#Orders
@app.route('/orders', methods=['POST'])
def create_order():
    item=request.json['item']
    amount=request.json['amount']
    customer_id=request.json['customer_id']
    order_new=Orders(item, amount, customer_id)
    db.session.add(order_new)
    db.session.commit()
    return order_schema.jsonify(order_new)

@app.route('/orders', methods=['GET'])
def get_orders():
    all_orders=Orders.query.all()
    result=orders_schema.dump(all_orders)
    return jsonify(result)

#Shipping
@app.route('/shippings', methods=['POST'])
def create_shipping():
    status=request.json['status']
    customer_id=request.json['customer_id']
    shipping_new=Shipping(status, customer_id)
    db.session.add(shipping_new)
    db.session.commit()
    return shipping_schema.jsonify(shipping_new)

@app.route('/shippings', methods=['GET'])
def get_shippings():
    all_shippings=Shipping.query.all()
    result=shippings_schema.dump(all_shippings)
    return jsonify(result)


#filtros y condiciones
#1.Obtener todos los clientes con su información completa.
@app.route('/customers/all-info', methods=['GET'])
def get_customers_all_info():
    all_customers = Customer.query.all()
    result = customers_schema.dump(all_customers)
    customers_info = result

    for customer_info in customers_info:
        customer_id = customer_info['customer_id']
        orders = Orders.query.filter_by(customer_id=customer_id).all()
        orders_info = orders_schema.dump(orders)
        customer_info['orders'] = orders_info

        shipping = Shipping.query.filter_by(customer_id=customer_id).first()
        if shipping:
            shipping_info = shipping_schema.dump(shipping)
            customer_info['shipping'] = shipping_info
        else:
            customer_info['shipping'] = None

    return jsonify(customers_info)

#2.Filtrar los clientes por país.
@app.route('/customers/pais/<country>', methods=['GET'])
def get_customers_country(country):
    all_customers = Customer.query.filter_by(country=country).all()
    result = customers_schema.dump(all_customers)
    return jsonify(result)
    
#3.Obtener los pedidos de un cliente específico.
@app.route('/orders/<first_name>/<last_name>', methods=['GET'])
def get_orders_customer(first_name, last_name):
    customer = Customer.query.filter_by(first_name=first_name, last_name=last_name).first()
    if customer:
        customer_id = customer.customer_id
        all_orders = Orders.query.filter_by(customer_id=customer_id).all()
        resultinfo = orders_schema.dump(all_orders)
        return jsonify(resultinfo)
    else:
        return jsonify({'message': 'Cliente no encontrado'})


#4.Filtrar los pedidos por cantidad (por encima de cierto amount).
@app.route('/orders/amount/<amount>', methods=['GET'])
def get_orders_amount(amount):
    all_orders = Orders.query.filter(Orders.amount > amount).all()
    resultinfo = orders_schema.dump(all_orders)
    return jsonify(resultinfo)

#5.Obtener los envíos pendientes.
@app.route('/shippings/envios/', methods=['GET'])
def get_shippings_sends_status():
    all_shippings = Shipping.query.filter(Shipping.status == "Pending").all()
    resultinfo = shippings_schema.dump(all_shippings)
    return jsonify(resultinfo)

#6.Filtrar los envíos por estado (entregado o pendiente).
@app.route('/shippings/status/<status>', methods=['GET'])
def get_shippings_status(status):
    all_shippings = Shipping.query.filter(Shipping.status == status).all()
    if all_shippings:
        customer_ids = [shipping.customer_id for shipping in all_shippings]
        all_orders = Orders.query.filter(Orders.customer_id.in_(customer_ids)).all()
        resultinfo = orders_schema.dump(all_orders)
        return jsonify(resultinfo)
    else:
        return jsonify({'message': 'Status no encontrado'})

#7.Filtrar los clientes por rango de edad.
@app.route('/customers/edad/<edad>', methods=['GET'])
def get_range_age(edad):
    all_customers = Customer.query.filter(Customer.age > edad).all()
    resultinfo = customers_schema.dump(all_customers)
    return jsonify(resultinfo)

#8.Filtrar los clientes por nombre y apellidos.
@app.route('/customers/all-info/<first_name>/<last_name>', methods=['GET'])
def get_customers_all_info_name_full(first_name, last_name):
    query = Customer.query
    if first_name:
        query = query.filter(Customer.first_name == first_name)
    if last_name:
        query = query.filter(Customer.last_name == last_name)

    all_customers = query.all()
    result = customers_schema.dump(all_customers)
    customers_info = result

    for customer_info in customers_info:
        customer_id = customer_info['customer_id']
        orders = Orders.query.filter_by(customer_id=customer_id).all()
        orders_info = orders_schema.dump(orders)
        customer_info['orders'] = orders_info

        shipping = Shipping.query.filter_by(customer_id=customer_id).first()
        if shipping:
            shipping_info = shipping_schema.dump(shipping)
            customer_info['shipping'] = shipping_info
        else:
            customer_info['shipping'] = None

    return jsonify(customers_info)


#9.Filtrar los clientes por edad ascendente y descendente
@app.route('/customers/asc/edad/', methods=['GET'])
def get_asc_age():
    all_customers = Customer.query.order_by(Customer.age.asc()).all()
    resultinfo = customers_schema.dump(all_customers)
    return jsonify(resultinfo)

#10.Agrupar clientes por pais y cuantos hay en cada uno 
from sqlalchemy import func

@app.route('/customers/countrygroup/', methods=['GET'])
def get_country_group():
    result = db.session.query(func.count(Customer.customer_id).label("Number of customers"), Customer.country).group_by(Customer.country).all()
    resultinfo = [{"Number of customers": row[0], "country": row[1]} for row in result]
    return jsonify(resultinfo)




if __name__ == '__main__':
    app.run(debug=True)

#Comands for use docker container mysql
#docker run --name mymysql -e MYSQL_ROOT_PASSWORD=mypassword -p 3306:3306 -d mysql:latest
#docker exec -it mymysql bash
#mysql -u root -p
#create database flaskmysql;


#Save data bases cointainer docker 
#docker exec -it mymysql bash
#mkdir /var/backup
#mysqldump -u root -p mydatabase > /var/backup/backup.sql
#in this case: mysqldump -u root -p flaskmysql> /var/backup/backup.sql
#Luego, desde otra terminal en tu sistema host, copia el archivo de respaldo desde el contenedor a la ubicación deseada en tu sistema host (Windows):
#docker cp mymysql:/var/backup/backup.sql C:\path\to\Folder\



#Para ejecutar backup en el contenedor
#docker cp C:\path\to\backup.sql mymysql:/backup.sql
#mysql -u root -p
#create database flaskmysql;  # crear base de datos
#use flaskmysql;  # seleccionar base de datos
#source /backup.sql;  # ejecutar script

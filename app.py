from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pytz

# Obtener la zona horaria
tz = pytz.timezone('America/Argentina/Buenos_Aires')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///earnings.db'
db = SQLAlchemy(app)

class Earning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    earnings = db.Column(db.Float, nullable=False)
    agency = db.Column(db.String(64), nullable=False)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

@app.route('/central')
def central():
    return render_template('index_agencia.html')

@app.route('/subagency')
def subagency():
    return render_template('index_subagencia.html')

@app.route('/api/earnings', methods=['POST'])
def submit_earnings():
    data = request.json
    print(data)
    try:
        date_str = data['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        earnings_value = data['earnings']
        if isinstance(earnings_value, dict):
            return jsonify({'error': 'Earnings should be a number, not a dictionary'}), 400
        new_earning = Earning(date=date_obj, earnings=float(earnings_value), agency=data['agency'])
        db.session.add(new_earning)
        db.session.commit()
        return jsonify({'message': 'Earnings report sent successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/earnings', methods=['GET'])
def get_earnings():
    date_filter = request.args.get('date')
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            earnings = Earning.query.filter_by(date=date_obj).all()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        earnings = Earning.query.all()
    
    results = [
        {
            'date': (earning.date + timedelta(days=1)).isoformat(),  # Sumar un día a la fecha
            'earnings': earning.earnings,
            'agency': earning.agency
        } for earning in earnings
    ]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


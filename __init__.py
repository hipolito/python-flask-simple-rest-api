import os

from flask import Flask, request, jsonify
from flask_migrate import Migrate

def create_app(test_config=None):

    from .models import db, Ticket

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', default='dev')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    from .models import db
    db.init_app(app)
    migrate= Migrate(app, db)

    from sqlalchemy.orm import exc


    @app.route('/api/tickets', methods=['GET'])
    def tickets():
        tickets = Ticket.query.all()
        return jsonify([ticket.to_json() for ticket in tickets])
    
    @app.route('/api/tickets', methods=['POST'])
    def tickets_create():
        body = request.json
        if body is None:
            return 'Body is missing'
            
        ticket = Ticket(name=body['name'], status=body['status'], url=body['url'])
        db.session.add(ticket)
        db.session.commit()
        return f"Ticket #{ticket.id}:{body['name']}, created successfully"

    @app.route('/api/tickets/<ticket_id>', methods=['GET'])
    def tickets_getTicketById(ticket_id):
        try:
            ticket = Ticket.query.filter_by(id=ticket_id).one()
            return ticket.to_json()
        except exc.NoResultFound:
            return jsonify({'error': 'Ticket not found'}), 404
    
    @app.route('/api/tickets/<ticket_id>', methods=['PUT'])
    def tickets_updateTicketById(ticket_id):
        try:
            ticket = Ticket.query.filter_by(id=ticket_id).one()
            updatedTicket = request.json
            ticket.name = updatedTicket['name']
            ticket.status = updatedTicket['status']
            ticket.url = updatedTicket['url']
            db.session.add(ticket)
            db.session.commit()
            return ticket.to_json()
        except exc.NoResultFound:
            return jsonify({'error': 'Ticket not found'}), 404 
    
    @app.route('/api/tickets/<ticket_id>', methods=['DELETE'])
    def tickets_deleteTicketById(ticket_id):
        try:
            ticket = Ticket.query.filter_by(id=ticket_id).one()
            db.session.delete(ticket)
            db.session.commit()
            return f"Ticket removed successfully"
        except exc.NoResultFound:
            return jsonify({'error': 'Ticket not found'}), 404
    
    return app


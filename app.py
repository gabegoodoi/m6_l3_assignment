from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError
from password import mypassword

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{mypassword}@localhost/ManagingAFitnessCenter'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MembersSchema(ma.Schema):
    id = fields.Int()
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ('name', 'age', 'id')

member_schema = MembersSchema()
members_schema = MembersSchema(many=True)

class WorkoutSessionsSchema(ma.Schema):
    session_id = fields.Int()
    member_id = fields.Int(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ('member_id', 'session_date', 'session_time', 'activity', 'session_id')

workout_session_schema = WorkoutSessionsSchema()
workout_sessions_schema = WorkoutSessionsSchema(many=True)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    workout_sessions = db.relationship('WorkoutSession', backref='member')

class WorkoutSession(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(255), nullable=False)

@app.route('/')
def home():
    return "Welcome to the home page"

@app.route("/members", methods=["GET"])
def get_all_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route("/members/<int:id>", methods=["GET"])
def get_member_by_id(id):
    member = Member.query.get_or_404(id)
    return member_schema.jsonify(member)

@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_member = Member(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"})

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "member details updated successfully"})

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "member deleted successfully"})

@app.route("/sessions", methods=["POST"])
def schedule_session():
    try:
        session_data = workout_session_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_session = WorkoutSession(member_id=session_data['member_id'], session_date=session_data['session_date'], session_time=session_data['session_time'], activity=session_data['activity'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message": "New session added successfully"})

@app.route("/sessions/<int:session_id>", methods=["PUT"])
def update_session(session_id):
    session = WorkoutSession.query.get_or_404(session_id)
    try:
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    session.member_id = session_data['member_id']
    session.session_date = session_data['session_date']
    session.session_time = session_data['session_time']
    session.activity = session_data['activity']
    db.session.commit()
    return jsonify({"message": "session details updated successfully"})

@app.route("/sessions", methods=["GET"])
def get_all_sessions():
    sessions = WorkoutSession.query.all()
    return workout_sessions_schema.jsonify(sessions)

@app.route("/sessions/<int:session_id>", methods=["GET"])
def get_sessions_by_session_id(session_id):
    session = WorkoutSession.query.get_or_404(session_id)
    return workout_session_schema.jsonify(session)


@app.route("/sessions/member/<int:member_id>", methods=["GET"])
def get_sessions_by_member_id(member_id):
    member = Member.query.get_or_404(member_id)
    sessions = member.workout_sessions
    if not sessions:
        return jsonify({"message": "No sessions found for this member"})

    return workout_sessions_schema.jsonify(sessions)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
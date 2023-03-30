from flask import Flask
from flask import jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import urllib.request
import json
import datetime

app = Flask(__name__)
app.debug = True

user_name = "HR"
pass_ = "Password123"

cluster = MongoClient(f"mongodb+srv://{user_name}:{pass_}@interview.nuuublq.mongodb.net/test")
db = cluster['interview']
collection = db['schedule']

CORS(app)

def insert_employees():
    details = employees_page()
    db['employee'].delete_many({})
    for emp in details:
        my_dict = {"e_id": emp['id'],
                    "e_name": emp['first_name']+" "+emp['last_name'],
                    "e_role": emp['employee_role']}
        db['employee'].insert_one(my_dict)

def employees_page():
    url = "https://employee-data-platform.vercel.app/api/fetchall"
    response = urllib.request.urlopen(url)

    data = response.read()
    data_dict = json.loads(data)
    data = []
    for c in data_dict:
        data.append(dict(c))
    return data

def insert_candidate():
    details = employees_page()
    db['candidate'].delete_many({})
    for can in details:
        my_dict = {
                    "c_id": can['id'],
                    "c_name": can['name']
                   }
        db['candidate'].insert_one(my_dict)

def candidate_page():
    url = "http://3.6.195.51:3000/api/v1/candidates/get_all_candidates"
    response = urllib.request.urlopen(url)

    data = response.read()
    data_dict = json.loads(data)
    data = []
    for c in data_dict:
        data.append(dict(c))
    return data


@app.route('/EmployeeDetails/', endpoint= 'employees_details', methods = ['GET'])
def employees_details():

    if request.method == 'GET':
        employees = db['employee'].find({}, {'_id': 0, 'e_id': 1, 'e_name': 1})
        response = []
        for i in employees:
            response.append(dict(i))
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/CandidateDetails/', endpoint= 'candidate_details', methods = ['GET'])
def candidate_details():
    if request.method == 'GET':
        candidates = db['candidate'].find({}, {'_id': 0, 'c_id': 1, 'c_name': 1})
        response = []
        for i in candidates:
            response.append(dict(i))
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/')
@app.route('/home', endpoint="home_page", methods=['GET', 'DELETE'])
def home_page():

    # GET Interview data from database
    if request.method == 'GET':

        # Insert employee details
        # insert_employees()

        # Insert Candidates
        # insert_candidate()

        collection.update_many({}, [{'$set': {'date': {'$toDate': '$date'}}}])

        result = collection.aggregate([
            {
                '$lookup': {'from': 'employee', 'localField': 'employees', 'foreignField': 'e_id', 'as': 'employees'}
            },
            {
                "$lookup": {'from': 'candidate', 'localField': 'candidate', 'foreignField': 'c_id', 'as': 'candidate'}
            },
            {
                "$project": {
                    "_id": 0,
                    "interview_id": 1,
                    "employees": ["$employees.e_id", "$employees.e_name"],
                    "candidate": ["$candidate.c_id", "$candidate.c_name"],
                    "date": {"year": {"$year": "$date"},
                             "month": {"$month": "$date"},
                             "day": {"$dayOfMonth": "$date"}
                             },
                    "slot": 1,
                    "status": 1
                }
            }
        ])
        interview_slots = []
        for c in result:
            interview_slots.append(dict(c))
        print(interview_slots)
        for interview in interview_slots:
            interview['employees'] = list(
                map(lambda x: {"id": x[0], "name": x[1]}, zip(interview['employees'][0], interview['employees'][1])))
            interview['candidate'] = {"id": interview['candidate'][0][0], "name": interview['candidate'][1][0]}
        response = jsonify(interview_slots)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # DELETE a interview slot
    if request.method == 'DELETE':
        body = request.json
        id = body['interview_id']

        db.schedule.delete_one({'interview_id': id})
        print('\n # Deletion successful # \n')
        response = jsonify({'status': 'Interview ID: ' + id + ' is deleted!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/interview/<int:id>', endpoint= 'onedata', methods=['GET', 'PUT'])
def onedata(id):
    # GET a specific interview data by interview id
    if request.method == 'GET':

        result = collection.aggregate([
            {
                "$match": {"interview_id": id}
            },
            {
                '$lookup': {'from': 'employee', 'localField': 'employees', 'foreignField': 'e_id', 'as': 'employees'}
            },
            {
                "$lookup": {'from': 'candidate', 'localField': 'candidate', 'foreignField': 'c_id', 'as': 'candidate'}
            },

            {
                "$project": {
                    "_id": 0,
                    "interview_id": 1,
                    "employees": ["$employees.e_id", "$employees.e_name"],
                    "candidate": ["$candidate.c_id", "$candidate.c_name"],
                    "date": {"Year": {"$year": "$date"},
                             "Month": {"$month": "$date"},
                             "Day": {"$dayOfMonth": "$date"}
                             },
                    "interview_start_time": 1,
                    "interview_end_time": 1,
                    "status": 1
                }
            }
        ])
        print(id)
        interview_slots = []

        for c in result:
            interview_slots.append(dict(c))
        print(interview_slots)

        for interview in interview_slots:
            interview['employees'] = list(
                map(lambda x: {"id": x[0], "name": x[1]}, zip(interview['employees'][0], interview['employees'][1])))
            interview['candidate'] = {"id": interview['candidate'][0][0], "name": interview['candidate'][1][0]}
        response = jsonify(interview_slots)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

    # UPDATE a interview slot details by id
    if request.method == 'PUT':

        body = request.json

        ID = body['interview_id']

        candidate_id = body['candidateId']
        employees_id = body['employeeIds']

        slot = body['slot']
        day = body['day']
        month = body['month']
        year = body['year']

        status = body['status']

        date = str(year) + "-" + str(month) + "-" + str(day)
        d = datetime.datetime.strptime(date, "%Y-%m-%d")

        db['schedule'].update_one(
            {'interview_id': ID},
            {
                "$set": {
                    "date": d,
                    "candidate": candidate_id,
                    "employees": employees_id,
                    "slot": slot,
                    "status": bool(status)
                }
            }
        )

        return jsonify({'status': 'Interview id: ' + str(ID) + ' is updated!'})


@app.route('/NewInterview/', endpoint='new_interview', methods=['POST'])
def new_interview():

    # Create a new interview slot details
    if request.method == 'POST':

        body = request.json

        doc = collection.find({}, {'_id': 0, 'interview_id': 1})

        interviews_id = []
        for i in doc:
            i = dict(i)
            print(type(i['interview_id']))
            interviews_id.append(i['interview_id'])

        ID = max(interviews_id)+1

        print(type(body['candidateId']))
        print(type(body['employeeIds']))

        candidate_id = body['candidateId']
        # ['c_id']
        employees_id = body['employeeIds']
        # employees_id = [emp['e_id'] for emp in employees]

        slot = body['slot']
        day = body['day']
        month = body['month']
        year = body['year']

        date = str(year)+"-"+str(month)+"-"+str(day)
        d = datetime.datetime.strptime(date, "%Y-%m-%d")
        # date = datetime.datetime(year, month, day)

        dict1 = {
            'interview_id': ID,
            'candidate': candidate_id,
            'employees': employees_id,
            'date': d,
            'slot': slot,
            'status': True
         }

        db['schedule'].insert_one(
            dict1
        )

        response = jsonify({'status': 'Interview slot with ID : ' + str(ID) + ' is Inserted!'})
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

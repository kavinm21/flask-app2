from flask import Flask
from flask import jsonify, request
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
app.debug = True

user_name = "HR"
pass_ = "Password123"

cluster = MongoClient(f"mongodb+srv://{user_name}:{pass_}@interview.nuuublq.mongodb.net/test")
db = cluster['interview']
collection = db['schedule']

CORS(app)


@app.route('/home', endpoint="home_page", methods=['GET', 'DELETE'])
def home_page():
    # GET Interview data from database
    if request.method == 'GET':

        collection.update_many({}, [{'$set': {'date': {'$toDate': '$date'}}}])

        result = collection.aggregate([
            {
                '$lookup': {'from': 'employee', 'localField': 'employees', 'foreignField': '_id', 'as': 'employees'}
            },
            {
                "$lookup": {'from': 'candidate', 'localField': 'candidate', 'foreignField': '_id', 'as': 'candidate'}
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
        return jsonify({'status': 'Interview ID: ' + id + ' is deleted!'})


@app.route('/interview/<id>', methods=['GET', 'PUT'])
def onedata(id):
    # GET a specific interview data by interview id
    if request.method == 'GET':

        result = collection.aggregate([
            {
                '$lookup': {'from': 'employee', 'localField': 'employees', 'foreignField': '_id', 'as': 'employees'}
            },
            {
                "$lookup": {'from': 'candidate', 'localField': 'candidate', 'foreignField': '_id', 'as': 'candidate'}
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
            },
            {
                "$match": {"interview_id": id}
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

        ID = body['InterviewID']
        candidate = body['Candidate']
        itm = db.candidate.find_one({"c_id": candidate})
        candidate_id = itm.get('_id')

        employees = body['Employees']
        itm = [db.employee.find_one({"e_id": emp}) for emp in employees]
        employees_id = [item.get('_id') for item in itm]

        start_time = body['StartTime']
        end_time = body['EndTime']
        date = body['Date']
        status = body['status']

        db['schedule'].update_one(
            {'interview_id': ID},
            {
                "$set": {
                    "date": date,
                    "interview_start_time": start_time,
                    "interview_end_time": end_time,
                    "Candidate": candidate_id,
                    "Employees": employees_id,
                    "status": status
                }
            }
        )

        return jsonify({'status': 'Interview id: ' + id + ' is updated!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
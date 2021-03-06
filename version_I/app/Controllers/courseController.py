from flask import request,jsonify
from app import app
import json
import os
import cv2
import face_recognition
import numpy as np

from app.helpers.data_helper import get_student_encoding,get_student_rolls

from app.Services.courseServices import  courseServices
from app.Services.studentServices import studentServices


@app.route('/initiate_attendence',methods=['POST'])
def initiate_attendence():
    
    courseData = json.loads(request.form.get('courseData'))
    imagestr = request.files['file']
    try: 
        IMAGE_UPLOAD_PATH = "/home/ubaid/Desktop/MyDrive/Projects/Attendance-App/backend/app/static/images"
        path = os.path.join(IMAGE_UPLOAD_PATH,courseData.get('name'))
        
        imagestr.save(path)    
        imageLoaded = cv2.imread(path)

        class_image_encodings = face_recognition.face_encodings(imageLoaded)
        all_student_data = studentServices.get_all_students_enrolled(**courseData)
        known_face_encodings = get_student_encoding(all_student_data)
        all_student_roll_nos = get_student_rolls(all_student_data)

        courseServices.mark_all_absent(courseData)

        for face_encoding,student_roll in zip(class_image_encodings,all_student_roll_nos):
            matches = face_recognition.compare_faces(known_face_encodings,face_encoding)
            face_distance = face_recognition.face_distance(known_face_encodings,face_encoding)
            best_match_index = np.argmin(face_distance)

            if matches[best_match_index]:
                courseServices.mark_present(student_roll,courseData)
        return jsonify({
            "status": 200,
            "result": {
                "status": 201,
                "message": "Attendance Done"
            }
        })
    except:
        return jsonify({
            "status": 200,
            "result": {
                "status": 400,
                "message": "Some problem check your image"
            }
        })


@app.route('/add_course',methods=['POST'])
def add_course():
    # Structur of "data"
    # data = {
    #     "name": "",
    #     "teacherAssigned"
    # }
    courseData = json.loads(request.data.decode('utf8'))
    return courseServices.add_course(courseData)


@app.route('/get_all_courses',methods=['POST'])
def get_all_courses():
    
    # filters = json.loads(request.data.decode('utf8'))
    
    curser = courseServices.get_all_courses()
    
    allCourses = []
    for course in curser:
        del course['student_enrolled']
        del course['_id']
        allCourses.append(course)
    
    response = jsonify({
        "allCourses":allCourses
    })
    
    return response




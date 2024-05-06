from flask import Flask, request, jsonify  # Make sure request is imported here
from flask_restful import Resource, Api
import sqlite3
from tasks import enqueue_training_task

app = Flask(__name__)
api = Api(app)

class User(Resource):
    def post(self):
        
        data = request.get_json()
        name = data['user_name']
        password = data['user_password']
        email = data['user_email']

        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            # Check if the email and password match an entry in the authorization table
            c.execute("SELECT * FROM authorization WHERE auth_email = ? AND auth_password = ?", (email, password))
            auth = c.fetchone()

            if not auth:
                return {'error': 'Unauthorized access'}, 401  # Unauthorized if no match

            # Insert new user if authorized
            c.execute("INSERT INTO user (user_name, user_password, user_email) VALUES (?, ?, ?)", (name, password, email))
            user_id = c.lastrowid
            conn.commit()
            return {'status': 'success', 'user_id': user_id}, 201

        except sqlite3.IntegrityError as e:
            return {'error': 'User already exists'}, 409  # Conflict if user already exists

        except Exception as e:
            return {'error': str(e)}, 400  # Bad request for other exceptions

        finally:
            conn.close()

class GetUser(Resource):
    def get(self, user_id):
        try:
            conn = sqlite3.connect('projectdatabase.db')
            c = conn.cursor()
            c.execute("SELECT user_id, user_name, user_email FROM user WHERE user_id = ?", (user_id,))
            user = c.fetchone()
            conn.close()

            if user:
                return {'user_id': user[0], 'user_name': user[1], 'user_email': user[2]}, 200
            else:
                return {'message': 'User not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 400

class CreateAuthUser(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data['auth_email']
            password = data['auth_password']

            conn = sqlite3.connect('projectdatabase.db')
            c = conn.cursor()
            c.execute("INSERT INTO authorization (auth_email, auth_password) VALUES (?, ?)", (email, password))
            user_id = c.lastrowid
            conn.commit()
            conn.close()

            return {'status': 'success', 'auth_email': email}, 201
        except Exception as e:
            return {'error': str(e)}, 400

class DataUpload(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        train_data = data.get('train_data')
        test_data = data.get('test_data')
        train_label = data.get('train_label')
        test_label = data.get('test_label')

        # Ensure all required fields are present
        if not all([user_id, train_data, test_data, train_label, test_label]):
            return {'error': 'All fields are required'}, 400

        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO dataupload (user_id, train_data, test_data, train_label, test_label)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, train_data, test_data, train_label, test_label))
            conn.commit()
            return {'message': 'Data uploaded successfully', 'data_id': c.lastrowid}, 201

        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'Integrity error, possibly foreign key violation'}, 400

        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        finally:
            conn.close()

class Model(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        model_ver = data.get('model_ver')

        if not all([user_id, model_ver]):
            return {'error': 'Missing user_id or model_ver'}, 400

        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO model (user_id, model_ver)
                VALUES (?, ?)
            """, (user_id, model_ver))
            model_id = c.lastrowid
            conn.commit()
            return {'message': 'Model created successfully', 'model_id': model_id}, 201

        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'Model could not be created, integrity error (possibly duplicate model_id)'}, 409

        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        finally:
            conn.close()

class Project(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        model_id = data.get('model_id')
        data_id = data.get('data_id')

        if not all([user_id, model_id, data_id]):
            return {'error': 'Missing required fields: user_id, model_id, or data_id'}, 400

        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO projects (user_id, model_id, data_id)
                VALUES (?, ?, ?)
            """, (user_id, model_id, data_id))
            project_id = c.lastrowid
            conn.commit()
            return {'message': 'Project created successfully', 'project_id': project_id}, 201

        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'Project could not be created due to integrity error'}, 409

        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        finally:
            conn.close()

class Training(Resource):
    def post(self):
        data = request.get_json()
        data_id = data.get('data_id')
        training_points = data.get('training_points')
        training_parameters = data.get('training_parameters')
        training_result = data.get('training_result')

        if not all([data_id, training_points, training_parameters, training_result]):
            return {'error': 'Missing required fields'}, 400

        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO training (data_id, training_points, training_parameters, training_result)
                VALUES (?, ?, ?, ?)
            """, (data_id, training_points, training_parameters, training_result))
            project_id = c.lastrowid
            conn.commit()
            return {'message': 'Training data added successfully', 'project_id': project_id}, 201

        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        finally:
            conn.close()

class Testing(Resource):
    def post(self):
        data = request.get_json()
        data_id = data.get('data_id')
        testing_result = data.get('testing_result')

        if not all([data_id, testing_result]):
            return {'error': 'Missing required fields'}, 400

        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO testing (data_id, testing_result)
                VALUES (?, ?)
            """, (data_id, testing_result))
            project_id = c.lastrowid
            conn.commit()
            return {'message': 'Testing data added successfully', 'project_id': project_id}, 201

        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        finally:
            conn.close()

class GetTrainingResult(Resource):
    def get(self, project_id):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("SELECT * FROM training WHERE project_id = ?", (project_id,))
            result = c.fetchone()
            if result:
                data = {
                    'project_id': result[0],
                    'data_id': result[1],
                    'training_points': result[2],
                    'training_parameters': result[3],
                    'training_result': result[4]
                }
                return {'status': 'success', 'data': data}, 200
            else:
                return {'status': 'error', 'message': 'No training record found with the provided project_id'}, 404

        finally:
            conn.close()

class UpdateTrainingParameters(Resource):
    def put(self, project_id):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()
        
        try:
            # Get the updated training parameters from the request
            data = request.get_json()
            updated_parameters = data.get('training_parameters')
            
            if updated_parameters:
                # Update the training parameters in the database
                c.execute("UPDATE training SET training_parameters = ? WHERE project_id = ?", (updated_parameters, project_id))
                conn.commit()
                
                return {'status': 'success', 'message': 'Training parameters updated successfully'}, 200
            else:
                return {'status': 'error', 'message': 'Missing training_parameters in the request'}, 400
        
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500
        
        finally:
            conn.close()

class GetTestingResult(Resource):
    def get(self, project_id):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("SELECT * FROM testing WHERE project_id = ?", (project_id,))
            result = c.fetchone()
            if result:
                data = {
                    'project_id': result[0],
                    'data_id': result[1],
                    'testing_result': result[2]
                }
                return {'status': 'success', 'data': data}, 200
            else:
                return {'status': 'error', 'message': 'No testing record found with the provided project_id'}, 404

        finally:
            conn.close()

class AnalyseResults(Resource):
    def post(self, project_id):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            # Fetch results for training and testing based on project_id
            c.execute("SELECT training_result FROM training WHERE project_id = ?", (project_id,))
            training_result_row = c.fetchone()
            training_result = training_result_row[0] if training_result_row else "No training result"

            c.execute("SELECT testing_result FROM testing WHERE project_id = ?", (project_id,))
            testing_result_row = c.fetchone()
            test_result = testing_result_row[0] if testing_result_row else "No testing result"

            # Perform analysis - example: concatenate training and testing results
            analysis_result = f"Analysis: Training Result - {training_result} | Testing Result - {test_result}"

            # Insert the analysis result into the database
            c.execute("""
                INSERT INTO analysis (project_id, training_result, test_result, ana_result)
                VALUES (?, ?, ?, ?)
            """, (project_id, training_result, test_result, analysis_result))
            conn.commit()

            # Return the analysis result
            return {'status': 'success', 'analysis_result': analysis_result}, 201

        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'Integrity error, possibly duplicate project_id'}, 409

        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        finally:
            conn.close()

class Publishing(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        project_id = data.get('project_id')
        data_id = data.get('data_id')
        ana_result = data.get('ana_result')

        if not all([user_id, project_id, data_id, ana_result]):
            return {'error': 'All fields are required'}, 400

        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO publishing (user_id, project_id, data_id, ana_result)
                VALUES (?, ?, ?, ?)
            """, (user_id, project_id, data_id, ana_result))
            conn.commit()
            return {'message': 'Data published successfully'}, 201

        except sqlite3.IntegrityError as e:
            conn.rollback()
            return {'error': 'Integrity error, possibly due to foreign key constraint or duplicate entry'}, 409

        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        finally:
            conn.close()

class GetPublishedResults(Resource):
    def get(self, user_id=None, project_id=None):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            if user_id and project_id:
                # Fetch specific publication based on user_id and project_id
                c.execute("""
                    SELECT * FROM publishing WHERE user_id = ? AND project_id = ?
                """, (user_id, project_id))
            elif user_id:
                # Fetch all publications for a specific user
                c.execute("""
                    SELECT * FROM publishing WHERE user_id = ?
                """, (user_id,))
            else:
                # Fetch all publications
                c.execute("""
                    SELECT * FROM publishing
                """)

            results = c.fetchall()
            if results:
                data = [{'user_id': row[0], 'project_id': row[1], 'data_id': row[2], 'ana_result': row[3]} for row in results]
                return {'status': 'success', 'data': data}, 200
            else:
                return {'status': 'error', 'message': 'No published results found'}, 404

        finally:
            conn.close()

class DeleteProject(Resource):
    def delete(self, project_id):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            if c.rowcount > 0:
                conn.commit()
                return {'message': 'Project deleted successfully'}, 200
            else:
                return {'message': 'Project not found'}, 404
        finally:
            conn.close()

class DeleteData(Resource):
    def delete(self, data_id):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("DELETE FROM dataupload WHERE data_id = ?", (data_id,))
            if c.rowcount > 0:
                conn.commit()
                return {'message': 'Data deleted successfully'}, 200
            else:
                return {'message': 'Data not found'}, 404
        finally:
            conn.close()

class DeleteUser(Resource):
    def delete(self, user_id):
        conn = sqlite3.connect('projectdatabase.db')
        c = conn.cursor()

        try:
            c.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
            if c.rowcount > 0:
                conn.commit()
                return {'message': 'User deleted successfully'}, 200
            else:
                return {'message': 'User not found'}, 404
        finally:
            conn.close()

class SubmitTraining(Resource):
    def post(self):
        data = request.get_json()  # Get data from the POST request
        if not data:
            return {'message': 'No input data provided'}, 400
        
        # Assuming the presence of a 'data' key in the JSON input
        if 'data' in data:
            enqueue_training_task(data['data'])
            return {'message': 'Training request submitted successfully.'}, 200
        else:
            return {'message': 'Invalid data provided'}, 400

api.add_resource(SubmitTraining, '/submit_training')
api.add_resource(DeleteProject, '/delete_project/<int:project_id>')
api.add_resource(DeleteData, '/delete_data/<int:data_id>')
api.add_resource(DeleteUser, '/delete_user/<int:user_id>')
api.add_resource(GetPublishedResults, '/publish', '/publish/<int:user_id>', '/publish/<int:user_id>/<int:project_id>')
api.add_resource(Publishing, '/publish')
api.add_resource(UpdateTrainingParameters, '/update_training_parameters/<int:project_id>')
api.add_resource(AnalyseResults, '/analyse_results/<int:project_id>')
api.add_resource(GetTrainingResult, '/get_training/<int:project_id>')
api.add_resource(GetTestingResult, '/get_testing/<int:project_id>')
api.add_resource(User, '/user')
api.add_resource(GetUser, '/user/<int:user_id>')
api.add_resource(CreateAuthUser, '/create_auth')
api.add_resource(DataUpload, '/upload_data')
api.add_resource(Model, '/create_model')
api.add_resource(Project, '/create_project')
api.add_resource(Training, '/add_training')
api.add_resource(Testing, '/add_testing')


if __name__ == '__main__':
    app.run(debug=True)
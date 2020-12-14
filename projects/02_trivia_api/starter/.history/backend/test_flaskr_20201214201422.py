import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app, models, setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://postgres:Muteaether69@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.

    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["categories"]))

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]))

    def test_404_out_of_range_questions(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

    def test_delete_existing_question(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
    
    def test_delete_non_existing_question(self):
        res = self.client().delete('/questions/1000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

    def test_post_question(self):
        res = self.client().post('/questions', json={
            "question": "WHY?",
            "answer": "BECAUSE",
            'difficulty': 1,
            'category': 1
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_422_post_question_with_wrong_category(self):
        res = self.client().post('/questions', json={
            "question": "WHY?",
            "answer": "BECAUSE",
            'difficulty': 1,
            'category': 80
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"]) 

    def test_search(self):
        res = self.client().post('/questions/search', json={
            "searchTerm": "What"
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"]) 
        self.assertTrue(len(data["questions"])) 

    def test_dummy_search(self):
        res = self.client().post('/questions/search', json={
            "searchTerm": "ksdghskjdgfksjdghfjdgh"
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"]) 
        
    def test_get_by_category(self):
        res = self.client().post('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"]) 
        self.assertTrue(len(data["questions"]))

    def test_400_get_by_non_existing_category(self):
        res = self.client().get('/categories/5000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
    
    def test_quizzes(self):
        res = self.client().get('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {"Science": 1}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertFalse(data["question"] is None)
    
    def test_quizzes_with_wrong_category(self):
        res = self.client().get('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {"NONE": 80}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])


    
    

    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
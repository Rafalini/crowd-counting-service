from crowdControll import db, bcrypt
from crowdControll.models import User, Post

db.drop_all()
db.create_all()

hash = bcrypt.generate_password_hash('test').decode('utf-8')

user_1 = User(username='testUser1', email='test1@m.com', password=hash)
user_2 = User(username='testUser2', email='test2@m.com', password=hash)
user_3 = User(username='t', email='t@m.c', password=hash)

post_1 = Post(title='dogexample', content='People count: 0', latitude=52.287, longitude=20.903, user_id=1)
post_2 = Post(title='exampledog', content='People count: -5', latitude=52.287, longitude=20.603, user_id=2)
post_3 = Post(title='test546', content='People count: 4', latitude=52.587, longitude=20.903, user_id=2)
post_4 = Post(title='helloworld', content='People count: 0', latitude=52.587, longitude=20.603, user_id=2)

db.session.add(user_1)
db.session.add(user_2)
db.session.add(user_3)
db.session.add(post_1)
db.session.add(post_2)
db.session.add(post_3)
db.session.add(post_4)

db.session.commit()

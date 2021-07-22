from flaskblog import db
from flaskblog.models import User, Post

db.drop_all()
db.create_all()

user_1 = User(username='testUser1', email='test1@gmail.com', password='test')
user_2 = User(username='testUser2', email='test2@gmail.com', password='test')
post_1 = Post(title='example', content='example content', user_id=1)
post_2 = Post(title='example', content='content example', user_id=2)

db.session.add(user_1)
db.session.add(user_2)
db.session.add(post_1)
db.session.add(post_2)

db.session.commit()

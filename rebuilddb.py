from crowdControll import db
from crowdControll.models import User, Post

db.drop_all()
db.create_all()

user_1 = User(username='testUser1', email='test1@gmail.com', password='test')
user_2 = User(username='testUser2', email='test2@gmail.com', password='test')
post_1 = Post(title='dog example', content='People count: 0', user_id=1)
post_2 = Post(title='example dog', content='People count: -5', user_id=2)
post_3 = Post(title='test546', content='People count: 4', user_id=2)
post_4 = Post(title='helloworld', content='People count: 0', user_id=2)

db.session.add(user_1)
db.session.add(user_2)
db.session.add(post_1)
db.session.add(post_2)
db.session.add(post_3)
db.session.add(post_4)

db.session.commit()

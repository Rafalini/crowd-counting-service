from flaskblog import db, User, Post

db.drop_all()
db.create_all()

user_1 = User(username='test1', email='test@gmail.com', password='test')
post_1 = Post(title='example', content='example content', user_id=1)

db.session.add(user_1)
db.session.add(post_1)

db.session.commit()

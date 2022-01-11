from crowdControll import app, db, bcrypt, queue
from crowdControll.models import User, Post, Announcement
import random
import time
import datetime


def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))


db.drop_all()
db.create_all()

hash = bcrypt.generate_password_hash('test').decode('utf-8')

user_1 = User(username='testUser1', email='test1@m.com', password=hash)
user_2 = User(username='testUser2', email='test2@m.com', password=hash)
user_3 = User(username='t', email='t@m.c', password=hash)
db.session.add(user_1)
db.session.add(user_2)
db.session.add(user_3)

# date = datetime.datetime.strptime('2021-01-11', '%Y-%m-%d')
# post_1 = Post(title='dogexample', content='Orange warsaw festiwal', date_posted=date, image_file='img_0001.jpg', number_of_people=0, latitude=52.287, longitude=20.903, user_id=1)
# date = datetime.datetime.strptime('2021-01-10', '%Y-%m-%d')
# post_2 = Post(title='exampledog', content='Woodstok 2020', date_posted=date, image_file='img_0001.jpg', number_of_people=0, latitude=52.287, longitude=20.603, user_id=2)
# date = datetime.datetime.strptime('2021-01-12', '%Y-%m-%d')
# post_3 = Post(title='test546', content='Dzień kolorów', date_posted=date, image_file='img_0001.jpg', number_of_people=0, latitude=52.587, longitude=20.903, user_id=2)
# date = datetime.datetime.strptime('2021-01-13', '%Y-%m-%d')
# post_4 = Post(title='helloworld', content='Zjazd motocyklistów', date_posted=date, image_file='img_0001.jpg', number_of_people=0, latitude=52.587, longitude=20.603, user_id=2)

# db.session.add(post_1)
# db.session.add(post_2)
# db.session.add(post_3)
# db.session.add(post_4)

currentDate = datetime.datetime.now().strftime('%Y-%m-%d')

for i in range(1, 50):
    postname = 'example_post_'
    imagefile = 'img_00'

    long = random.uniform(20, 22)
    lati = random.uniform(51.7, 52.6)

    date = str_time_prop('2019-01-01', currentDate, '%Y-%m-%d', random.uniform(0, 1))
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    if i < 10:
        postname += '0'+str(i)
        imagefile += '0'+str(i) + '.jpg'
    else:
        postname += str(i)
        imagefile += str(i) + '.jpg'

    post = Post(title=postname, content='', image_file=imagefile, number_of_people=-1, latitude=lati, longitude=long, user_id=1)
    db.session.add(post)
    db.session.commit()
    db.session.refresh(post)
    queue.put(post.id)

anno1 = Announcement(title='New version 1.0!', content='New version, new features!')
anno2 = Announcement(title='New version 1.1!', content='New version, new features!')

db.session.add(anno1)
db.session.add(anno2)

db.session.commit()
queue.put('exit')

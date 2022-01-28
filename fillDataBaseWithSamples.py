import datetime
import random
import time
import sys

from crowdControll import db, bcrypt, queue
from crowdControll.functions import getAddress
from crowdControll.models import User, Post, Announcement
from essential_generators import DocumentGenerator

n = 25
quick = False

if len(sys.argv) == 3: #make N posts and make quick
    quick = True
    if sys.argv[1].isnumeric():
        n = int(sys.argv[1])
    else:
        n = int(sys.argv[2])
elif len(sys.argv) == 2: #make N posts or make quick
    if sys.argv[1].isnumeric(): #make N
        n = int(sys.argv[1])
        quick = False
    else:                       #make quick
        quick = True
elif len(sys.argv) == 1:
    pass #defaults
else:
    print("Unknown number of arguments! Example usage:")
    print("Note: default setting is to count people on pictures, its resource and time consuming (up to 10s/picture)")
    print("Note: default posts amount is 25")
    print("$ python3 fillDataBaseWithSamples [number_of_posts] [-q]")
    print("To fill with default settings-> $ python3 fillDataBaseWithSamples")
    print("To fill with 10 posts $ python3 fillDataBaseWithSamples 10")
    print("To fill with 10 posts quickly (dont compute pictures)-> $ python3 fillDataBaseWithSamples 10 -q")

gen = DocumentGenerator()


def getSentence():
    text = gen.sentence()
    if text[-1] != '.':
        text += '. '
    return text

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

currentDate = datetime.datetime.now().strftime('%Y-%m-%d')

for i in range(1, n):
    postname = getSentence()
    imagefile = 'img_00'
    content = getSentence()+getSentence()+getSentence()
    # long = random.uniform(20, 22)
    # lati = random.uniform(51.7, 52.6)
    long = random.uniform(17, 22)
    lati = random.uniform(47, 52.6)

    date = str_time_prop('2020-01-01', currentDate, '%Y-%m-%d', random.uniform(0, 1))
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    picNum = i % 25 + 1
    if picNum < 10:
        imagefile += '0'+str(picNum) + '.jpg'
    else:
        imagefile += str(picNum) + '.jpg'

    post = Post(title=postname, content=content, image_file=imagefile, date_posted=date, number_of_people=0, latitude=lati, longitude=long, user_id=1)
    post.address = getAddress(lati, long)

    db.session.add(post)
    db.session.commit()
    db.session.refresh(post)

    if quick:
        post.number_of_people = random.randint(10, 1234)
    else:
        queue.put(post.id)

anno1 = Announcement(title='New version 1.0!', content='First version!')
anno2 = Announcement(title='New version 1.1!', content='Minor update of forms and user input')
anno3 = Announcement(title='New version 1.5!', content='Added statistics')
anno4 = Announcement(title='New version 2.0!', content='Added map, improved time statistics, added calendar!')

db.session.add(anno1)
db.session.add(anno2)
db.session.add(anno3)
db.session.add(anno4)

db.session.commit()
queue.put('exit')

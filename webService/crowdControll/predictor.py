from crowdControll.trainedModel.models import predict, init
from crowdControll.models import Post
from threading import Lock, Thread
from PIL import Image
import torch
import os


class SingletonMeta(type):

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Predictor(metaclass=SingletonMeta):
    device = None
    model = None
    app = None
    db = None
    proc = None

    def __init__(self, queue, db, app) -> None:
        self.db = db
        self.app = app
        self.queue = queue
        self.device = torch.device('cpu')  # device can be "cpu" or "gpu"
        self.model = init(self.device)
        self.proc = Thread(target=consumer, args=(queue, app, db))
        self.proc.start()
        print("init run")

    def doPredict(self, inp):
        return predict(inp, self.device, self.model)


def consumer(queue, app, db):
    print('starting consumemr....')
    predictor = Predictor(queue, app, db)
    while True:
        entry = queue.get()
        post = Post.query.get(entry)
        print('got entry....post id: ' + str(entry))
        picture_path = os.path.join(app.root_path, 'static/post_imgs', post.image_file)
        print('path:' + picture_path)
        number_of_people = predictor.doPredict(Image.open(picture_path))
        print('output number:' + str(number_of_people))
        post.number_of_people = number_of_people
        db.session.commit()
        print('commit post id: ' + str(entry))

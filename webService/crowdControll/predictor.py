from crowdControll.trainedModel.models import predict, init
from crowdControll.models import Post
from multiprocessing import Process, Lock
from PIL import Image
import torch
import os


class Singleton(type):
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


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
    queue = None
    device = None
    model = None
    proc = None

    def __init__(self, queue, app, db):
        print('predictor init...')
        self.queue = queue
        self.device = torch.device('cpu')  # device can be "cpu" or "gpu"
        self.model = init(self.device)
        self.proc = Process(target=consumer, args=(queue, app, db))
        self.proc.daemon = True
        self.proc.start()

    def doPrediction(self, inp):
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
        number_of_people = predictor.doPrediction(Image.open(picture_path))
        print('output number:' + str(number_of_people))
        post.number_of_people = number_of_people
        db.session.commit()
        print('commit post id: ' + str(entry))

from shutil import copyfile

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
    predictionLock = Lock()

    def __init__(self, queue, db, app) -> None:
        self.db = db
        self.app = app
        self.queue = queue
        self.device = torch.device('cpu')  # device can be "cpu" or "gpu"
        self.model = init(self.device)
        self.proc = Thread(target=consumer, args=(queue, app, db))
        self.proc.start()

    def doPredict(self, inp):
        result = 0
        with self.predictionLock:
            out_map, result = predict(inp, self.device, self.model)
        return out_map, result


def consumer(queue, app, db):
    predictor = Predictor(queue, app, db)
    while True:
        try:
            entry = queue.get()
        except KeyboardInterrupt:
            print('ignore CTRL-C from worker')
        if entry == 'exit':
            break
        print('current processing post-picture id: '+str(entry))
        post = Post.query.get(entry)
        picture_path = os.path.join(app.root_path, 'static/post_imgs', post.image_file)
        map_path = os.path.join(app.root_path, 'static/maps', post.image_file)
        try:
            out_map, number_of_people = predictor.doPredict(Image.open(picture_path))
            i = Image.fromarray(out_map)
            i.save(map_path, quality=100)
        except Exception:
            print('error on: '+picture_path)
            error_path = os.path.join(app.root_path, 'static/post_imgs/errors/')
            copyfile(picture_path, error_path)
            number_of_people = 0
        post.number_of_people = number_of_people
        db.session.commit()


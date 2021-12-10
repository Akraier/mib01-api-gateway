class Message():
    """
    This class represents a Message.
    It is not a model, it is only a lightweight class used
    to represents a Message.
    """
    id = None
    sender = None
    title = None
    content = None
    date_of_delivery = None
    receivers = None
    extra_data = None
    
    @staticmethod
    def build_from_json(json: dict):
        kw = {key: json[key] for key in ['id', 'sender', 'title', 'content', 'date_of_delivery', 'font', 'receivers']}
        extra = json.copy()
        all(map(extra.pop, kw))
        kw['extra'] = extra

        return Message(**kw)

    def __init__(self, **kw):
        if kw is None:
            raise RuntimeError('You can\'t build the user with none dict')
        self.id = kw["id"]
        self.sender = kw["sender"]
        self.title = kw["title"]
        self.content = kw["content"]
        self.date_of_delivery = kw["date_of_delivery"]
        self.font = kw["font"]
        self.receivers = kw["receivers"]
        self.extra_data = kw['extra']

    def get_id(self):
        return self.id

    def __getattr__(self, item):
        if item in self.__dict__:
            return self[item]
        elif item in self.extra_data:
            return self.extra_data[item]
        else:
            raise AttributeError('Attribute %s does not exist' % item)

    def __str__(self):
        s = 'Message Object\n'
        for (key, value) in self.__dict__.items():
            s += "%s=%s\n" % (key, value)
        return s
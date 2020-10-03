class DBFiller:
    def __init__(self, filler_class_instances=None):
        if filler_class_instances is None:
            filler_class_instances = []
        self.classes = filler_class_instances

    def refill(self):
        for instance in self.classes:
            instance.refill()

    def add_instance(self, instance):
        self.classes.append(instance)

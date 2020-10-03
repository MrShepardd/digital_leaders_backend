from .general_review import GeneralReview


class Mercury:
    def __init__(self):
        self.res = {}
        self.gr = GeneralReview()

    def get_general_review(self):
        # self.res['get_social_graph'] = self.sgr.get_social_graph()
        return self.res
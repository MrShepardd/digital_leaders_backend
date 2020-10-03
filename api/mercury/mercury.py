from .general_review import GeneralReview


class Mercury:
    def __init__(self):
        self.res = {}
        self.gr = GeneralReview()

    def get_general_review(self):
        # self.res['get_atm_location'] = self.gr.get_atm_location()
        self.res['get_crowded_places'] = self.gr.get_crowded_places()
        # self.res['get_path_crowded_places'] = self.gr.get_path_crowded_places()
        return self.res
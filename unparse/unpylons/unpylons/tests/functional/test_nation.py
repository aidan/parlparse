from demoproj.tests import *

class TestNationController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='nation'))
        # Test response...

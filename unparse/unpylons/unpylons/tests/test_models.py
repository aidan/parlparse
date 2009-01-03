from unpylons.tests import *

import unpylons.model as model
model.metadata.drop_all()
model.metadata.create_all()

class TestModel:

    def test_1(self):
        id = 'S-PV-1234'
        title = u'abc'
        m = model.Meeting(id='S-PV-1234',
            title=title)
        t = model.Topic.by_name(u'Iraq')
        m.topics = [t]
        model.Session.flush()
        model.Session.clear()
        m = model.Meeting.query.filter_by(id=id).first()
        assert m.title == title
        assert len(m.topics) == 1
        # print m.topics[0].name
        # assert False
        


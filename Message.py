import json


class Message:
    def __init__(self, m_author, m_date, m_time, m_type, m_text):
        self.m_author = m_author
        self.m_date = m_date
        self.m_time = m_time
        self.m_type = m_type

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

class Date:
    def __init__(self, s):
        year, month, day = s.split('.')
        self.d = (int(year), int(month), int(day))

    def __gt__(self, odate):
        if not isinstance(odate, Date):
            return NotImplemented
        return self.d > odate.d

    def __lt__(self, odate):
        if not isinstance(odate, Date):
            return NotImplemented
        return self.d < odate.d

    def __ge__(self, odate):
        if not isinstance(odate, Date):
            return NotImplemented
        return self.d >= odate.d

    def __le__(self, odate):
        if not isinstance(odate, Date):
            return NotImplemented
        return self.d <= odate.d

    def __str__(self):
        return '.'.join(self.d)

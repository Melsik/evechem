class NavLocation(object):
    def __init__(self, title, path, fa_icon_class, text, active=False):
        self.title = title
        self.path = path
        self.fa_icon_class = fa_icon_class
        self.text = text
        self.active = active

class EveChemNav(object):

    def __init__(self, active_path=None, root=''):
        self.locations = [
            NavLocation('Operations','/operations','fa-cogs','Operations'),
            NavLocation('Towers','/towers','fa-list','Towers'),
            NavLocation('Inventory','/inventory','fa-cube','Inventory'),
            NavLocation('Statistics','/statistics','fa-pie-chart','Statistics'),
            NavLocation('Market','/market','fa-line-chart','Market'),
            NavLocation('Fuel Ice Calculator','/fuel-ice','fa-snowflake-o','Fuel Ice Calculator')
            ]

        for loc in self.locations:
            if loc.path == active_path:
                loc.active = True

            loc.path = root + loc.path




import requests

TOKEN = ""
URL = ""
PROJECT_IDS = ""

def init(token, url, project_ids):
    global TOKEN
    global URL
    global PROJECT_IDS

    TOKEN = token
    URL = url
    PROJECT_IDS = project_ids


class Project(object):
    """Object representation of a pivotal project"""

    def __init__(self, project_id, name):
        self.project_id = project_id
        self.name = name
        self.epics = []
        self.stories = []
        self.labels = []

    @staticmethod
    def from_json(json):
        """Converts a json dict into a project"""
        return Project(int(json['id']), json['name'])

    @staticmethod
    def from_id(project_id):
        """Gets a project given a project ID"""
        resp = requests.get(URL+'/projects/%s?fields=name,id' % (str(project_id)), headers={'X-TrackerToken' : TOKEN})
        jresp = resp.json()
        ret = Project(int(jresp['id']), jresp['name'])

        # get epics
        #if ('epic_ids' in jresp.keys()):
        #    for ids in jresp['epic_ids']:
        #        ret.epics.append(Epic.from_id(project_id, int(ids)))

        # get labels

        # get stories
        resp = requests.get(URL+'/projects/%s/stories' % (str(project_id)),
                headers={'X-TrackerToken' : TOKEN})
        jresp = resp.json()

        for story in jresp:
            ret.stories.append(Story.from_json(story))

        # get iterations


        return ret


class Label(object):
    """Object representation of a label"""

    def __init__(self, label_id = None, label_name= "", project_id = None):
        self.label_name = label_name
        self.label_id = label_id
        self.project_id = project_id


    @staticmethod
    def from_json(json):
        """Creates a label from a json dict"""
        return Label(label_id = json['id'], label_name = json['name'],
                project_id = json['project_id'])


class Epic(object):
    """Object representation of an epic"""

    def __init___(self, epic_id = None, epic_label = None, project_id = None):
        self.stories = None
        self.label = epic_label
        self.epic_id = epic_id
        self.project_id = project_id


    @staticmethod
    def from_json(json):
        """Creates an epic from a json dict"""
        return Epic(epic_id = int(json['id']), project_id = int(json['project_id']))

    @staticmethod
    def from_id(project_id, epic_id):
        """Creates an epic from an epic ID, given a project ID"""
        resp = requests.get(URL+'/projects/%s/epics/%s?fields=name,id,epic_ids' % (str(project_id), str(epic_id)), headers={'X-TrackerToken' : TOKEN})

        return "test epic"

class Story(object):
    """Object representation of a story"""

    def __init__(self,name = "", description = "", story_type = None, story_id
            = None, project_id = None, estimate = 0, state = None):
        self.story_id = story_id
        self.labels = []
        self.project_id = project_id
        self.estimate = estimate
        self.name = name
        self.description = description
        self.story_type = story_type
        self.state = state

    @staticmethod
    def from_json(json):
        """converts a json string into a a story object"""

        desc = ''
        est = None
        if 'description' in json.keys():
            desc = json['description']
        if 'estimate' in json.keys():
            est = int(json['estimate'])
        ret = Story(name = json['name'], description = desc, 
                story_type = json['story_type'], story_id = json['id'],
                project_id = json['project_id'], estimate = est,
                state = json['current_state'])

        if 'labels' in json.keys():
            for label in json['labels']:
                ret.labels.append(Label.from_json(label))

        return ret



class User(object):
    """Object represenation of a user"""

    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.name = user_name

class Iteration(object):
    """Object representation of an iteration"""

    def __init__(self, iteration_id = None, project_id = None,
            start = None, finish = None, strength = 1.0):
        self.iteration_id = iteration_id
        self.project_id = project_id
        self.start = start
        self.finish = finish
        self.strength = strength

def get_projects(TOKEN):
    project_list = []

    #resp = requests.get(URL+'/projects?fields=name,id,epics', headers={'X-TrackerToken' : TOKEN})
    #jresp = resp.json()

    #print jresp

    for i in PROJECT_IDS:
        project_list.append(Project.from_id(i))

    return project_list

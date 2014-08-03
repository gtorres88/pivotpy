import requests

TOKEN = ""
URL = ""
PROJECT_IDS = ""


_projects_ = {}

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
        self.labels = {}

        global _projects_

        _projects_[int(self.project_id)] = self

    @staticmethod
    def from_json(json):
        """Converts a json dict into a project"""
        return Project(int(json['id']), json['name'])

    @staticmethod
    def from_id(project_id):
        """Gets a project given a project ID"""
        resp = requests.get(URL+'/projects/%s?fields=name,id,epics,labels' % (str(project_id)), headers={'X-TrackerToken' : TOKEN})
        jresp = resp.json()

        ret = Project(int(jresp['id']), jresp['name'])

        #get labels
        for lab in jresp['labels']:
            ret.labels[int(lab['id'])] = lab['name']

        # get epics
        if ('epics' in jresp.keys()):
            for epic in jresp['epics']:
                ret.epics.append(Epic.from_json(epic))


        # get stories
        resp = requests.get(URL+'/projects/%s/stories' % (str(project_id)),
                headers={'X-TrackerToken' : TOKEN})
        jresp = resp.json()

        for story in jresp:
            ret.stories.append(Story.from_json(story))

        # get iterations


        return ret


class Epic(object):
    """Object representation of an epic"""

    def __init__(self, epic_id = None, name = "", epic_label = "", project_id = None):
        self.stories = []
        self.label = epic_label
        self.label_id = 0
        self.epic_id = epic_id
        self.project_id = project_id
        self.name = name


    @staticmethod
    def from_json(json):
        """Creates an epic from a json dict"""

        ret = Epic(epic_id = int(json['id']), name = json['name'], project_id =
                int(json['project_id']))

        if 'label' in json.keys():
            ret.label = json['label']['name']
            ret.label_id = int(json['label']['id'])


        return ret

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
        self.labels = {} #this is just a dictionary of labels - id to name
        self.project_id = project_id
        self.estimate = estimate
        self.name = name
        self.description = description
        self.story_type = story_type
        self.state = state

    @staticmethod
    def from_json(json):
        """converts a json string into a a story object"""

        ret = Story()

        for key in json.keys():
            setattr(ret, key, json[key])

        ret.labels = {}
        if 'labels' in json.keys():
            for lab in json['labels']:
                ret.labels[int(lab['id'])] = lab['name']

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

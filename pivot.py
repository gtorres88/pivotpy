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
        self.done_iterations = []
        self.current_backlog_iterations = []
        self.labels = {}

        global _projects_

        _projects_[int(self.project_id)] = self

    def get_current_iteration(self):
        """returns current iteration"""

        if len(self.current_backlog_iterations) > 0:
            return self.current_backlog_iterations[0]

        #should probably raise an exception here
        return None

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
        offset = 0
        total = 0
        limit = 0

        while True:
            resp = requests.get(URL+'/projects/%s/stories?offset=%s&envelope=true'
                    % (str(project_id), str(offset)),
                    headers={'X-TrackerToken' : TOKEN})
            jresp = resp.json()

            total = int(jresp['pagination']['total'])
            limit = int(jresp['pagination']['limit'])

            for story in jresp['data']:
                ret.stories.append(Story.from_json(story))

            offset = offset + limit
            if (offset >= total):
                break

        # get iterations
        def get_iteration_list(scope):
            offset = 0
            total = 0
            limit = 0

            to_return = [] #list of iterations

            while True:
                resp = requests.get(URL+'/projects/%s/iterations?fields=number,project_id,length,team_strength,story_ids,start,finish&offset=%s&scope=%s&envelope=true'
                        % (str(project_id),str(offset), str(scope)),
                        headers={'X-TrackerToken' : TOKEN})
                jresp = resp.json()


                total = int(jresp['pagination']['total'])
                limit = int(jresp['pagination']['limit'])

                for iteration in jresp['data']:
                    to_return.append(Iteration.from_json(iteration))

                offset = offset + limit
                if (offset >= total):
                    break

            return to_return

        #this gets the done iterations
        ret.done_iterations = get_iteration_list("done")
        ret.current_backlog_iterations = get_iteration_list("current_backlog")

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

    def _get_epic_stories(self):

        global _projects_
        #get the project for this epic:
        proj = _projects_[int(self.project_id)]

        #then we check the stories for this project that belong to this epic
        epic_stories = []
        for s in proj.stories:
            if s.has_label(self.label):
                epic_stories.append(s)

        return epic_stories

    def get_total_points(self):
        """gets an epic's total of points"""

        points = 0

        epic_stories = self._get_epic_stories()

        for s in epic_stories:
            if hasattr(s, 'estimate'):
                points += int(s.estimate)

        return points

    def get_completed_points(self):
        points = 0

        epic_stories = self._get_epic_stories()

        for s in epic_stories:
            if hasattr(s, 'estimate') and (s.current_state == 'accepted'):
                points += int(s.estimate)

        return points

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


    def has_label(self, label_name = None, label_id = None):
        """checks if has a particular label, by name or ID. ID is first if provided"""

        if label_id is not None:
            return (label_id in self.labels.keys())
        elif label_name is not None:
            return (label_name in self.labels.values())
        else:
            return False

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

    def has_story(self, story):
        """checks if story is in iteration, takes a Story object or a story_id"""
        if isinstance(story, Story):
            story_id = int(story.id)
        else:
            story_id = int(story)

        if story_id in self.story_ids:
            return True

        return False

    @staticmethod
    def from_json(json):
        ret = Iteration()

        for key in json.keys():
            setattr(ret, key, json[key])

        return ret


def get_projects(TOKEN):
    project_list = []

    #resp = requests.get(URL+'/projects?fields=name,id,epics', headers={'X-TrackerToken' : TOKEN})
    #jresp = resp.json()

    #print jresp

    for i in PROJECT_IDS:
        project_list.append(Project.from_id(i))

    return project_list

import models as m
from hoomanpy import qlist

ACTIONS_DIR = 'actions'
LOGS_DIR = 'logs'

(CREATED,
 UPDATED,
 DELETED,
 EXECUTED) = range(4)


class ModelManager(object):

    _objects = qlist()

    @classmethod
    def all(cls):
        return cls._objects

    @classmethod
    def filter(cls, **kwargs):
        return cls._objects.filter(**kwargs)

    @classmethod
    def distinct(cls, attribute=None):
        return cls._objects.distinct(attribute=attribute)

    @classmethod
    def get(cls, **kwargs):
        return cls._objects.get(**kwargs)

    @classmethod
    def append(cls, obj):
        cls._objects.append(obj)

    @classmethod
    def remove(cls, obj):
        cls._objects.remove(obj)

    @classmethod
    def extend(cls, iterable):
        cls._objects.extend(iterable)

    @staticmethod
    def _load_from_file(path):

        jsondict = {}
        data = {}
        data['tags'] = qlist()
        data['targets'] = qlist()
        data['docs'] = qlist()

        # extract tags and props from header
        from json import loads
        with open(path) as f:
            for i, line in enumerate(f):
                if i == 0:
                    if line.strip() != '':
                        jsondict = loads(line)
                        if isinstance(jsondict, dict):
                            for key, value in jsondict.iteritems():
                                if key == 'tags':
                                    tags = value.split()
                                    if len(tags) > 0:
                                        data[key].extend(tags)
                                elif key == 'targets':
                                    for t in value:
                                        t = loads(t)
                                        target = m.Target.load(t['freq'], t['starts'], t['measure'],
                                                          period_target=t['period_target'], interval=t['interval'],
                                                          met_after=t['met_after'])
                                        data[key].append(target)
                                else:
                                    data[key] = value
                else:
                    docs = line.replace('\n', '').rstrip()
                    if len(docs) != 0 or len(data['docs']) != 0:
                        data['docs'].append(docs)

        data['persisted'] = jsondict
        return data


class ActionManager(ModelManager):

    #===================================================================================================================
    # collection methods
    #===================================================================================================================
    @classmethod
    def active(cls):
        return cls._objects.filter(status='active')

    @classmethod
    def inactive(cls):
        return cls._objects.filter(status='inactive')

    @classmethod
    def future(cls):
        return cls._objects.filter(status='future')

    #===================================================================================================================
    # public methods - CRUD
    #===================================================================================================================
    @classmethod
    def load(cls, id, parent=None):
        """Load an action from file.

        If the action is part of a plan, a plan instance must be supplied with it for proper relation.
        """

        # load the action
        instance = m.Action.load(id, cls._load_from_file(id), parent=parent)

        # append to internal list
        cls._objects.append(instance)

        return instance

    @classmethod
    def save(cls, action):
        """Save an action to file.

        :param action: Action instance
        :type action: Action
        """

        # first time saving it
        if action.id is None:
            # persist data and set id
            cls._file_create(action)

            # log creation
            DataAccess.log(action, 'created', CREATED, None, None)

            # add to internal collection
            cls._objects.append(action)

        elif action.id != cls._generate_id(action):
            cls._file_rename(action)
            cls._file_write(action)

        elif action in DataAccess.changed:
            cls._file_write(action)

        # write logged changes
        for log in DataAccess.changed_log.filter(obj=action)[:]:
            DataAccess.log(action, log.log, log.type, log.progress, log.minutes)
            DataAccess.changed_log.remove(log)

        # remove from collection of changed models
        if action in DataAccess.changed:
            DataAccess.changed.remove(action)

    @classmethod
    def delete(cls, action, erase_history=True):
        """Delete an action from file.

        :param action: Action instance
        :type action: Action
        """
        if action.id is None:
            return

        # purge history from the logs unless explicitly wanted
        if erase_history:
            DataAccess.purge_object_from_logs(action)

        # remove all references to the action
        if action.parent is not None:
            action.parent.actions.remove(action)
            action.parent = None

        # remove from interal list
        DataAccess.actions.remove(action)

        # delete the file
        cls._file_delete(action)

        DataAccess._print_output("'{}' deleted", action.name)

    #===================================================================================================================
    # internal methods - file system (and eventually git)
    #===================================================================================================================
    @classmethod
    def _file_write(cls, action):
        if action.id is None:
            return

        # rewrite file
        with open(action.id, 'w') as f:
            f.write(DataAccess._properties_to_json(action) + '\n')
            for docline in action.docs:
                f.write(docline + '\n')

    @classmethod
    def _file_delete(cls, action):

        # delete the file
        import os
        os.remove(action.id)

    @classmethod
    def _file_rename(cls, action):
        """Rename a file for an action.

        :param action: Action instance
        :type action: Action
        """

        id = cls._generate_id(action)

        if cls._file_exists(id):
            raise Exception("Cannot rename action to '{}'. An action with the same "
                            "name-generated id already exists.".format(action.name))

        import os
        os.rename(action.id, id)
        action.id = id

    @classmethod
    def _file_create(cls, action):
        """Create a file for an action and sets the id..

        :param action: Action to create a file for.
        :type action: Action
        """

        id = cls._generate_id(action)

        if cls._file_exists(id):
            raise Exception("Cannot create action named '{}'. An action with the same "
                            "name-generated id already exists. Either assign the action "
                            "to a different plan or change the name.".format(action.name))

        action.id = id

        cls._file_write(action)

    @classmethod
    def _file_exists(cls, path):

        try:
            with open(path):
                pass
        except IOError:
            return False

        return True

    @classmethod
    def _generate_id(cls, action):
        """Return valid path from action name.

        :param action: Action instance
        :type action: Action
        """

        if action.name is None or action.name == '':
            raise Exception('Action has no name!')

        path = ''
        if action.parent is not None:
            path = action.parent.id
        else:
            path = '/'.join([DataAccess.life_prj_path, ACTIONS_DIR])

        import re
        basename = re.sub(r'[^A-Za-z0-9_!@#$%&\-+=\'":;\(\)\[\]\{\},.]', '_', action.name)

        id = '/'.join([path, basename])

        # return filename
        return id


class PlanManager(ModelManager):

    #===================================================================================================================
    # collection methods
    #===================================================================================================================
    @classmethod
    def active(cls):
        return cls._objects.filter(actions__any__status='active')

    @classmethod
    def inactive(cls):
        inactive_list = qlist()
        for plan in cls._objects:
            if not cls.has_active_children(plan):
                inactive_list.append(plan)
        return inactive_list
        # todo: maybe i can come up with a recursive filter operator that will drill down into plans of plans of plans

    @classmethod
    def has_active_children(cls, plan):
        if len(plan.actions.filter(status='active')) > 0:
            return True
        for plan in plan.plans:
            if cls.has_active_children(plan):
                return True

        return False

    #===================================================================================================================
    # public methods - CRUD
    #===================================================================================================================
    @classmethod
    def load(cls, id, parent=None):
        """Load a plan from file.

        If the plan is the child of a plan, a plan instance must be supplied with it for proper relation.
        """

        # load the plan
        instance = m.Plan.load(id, cls._load_from_file("{}/.plan".format(id)), parent=parent)

        # append to internal list
        cls._objects.append(instance)

        return instance

    @classmethod
    def save(cls, plan):
        """Save a plan to file.

        :param plan: Plan instance
        :type plan: Plan
        """
        
        # first time saving it
        if plan.id is None:
            # persist data and set id
            cls._file_create(plan)

            # log creation
            DataAccess.log(plan, 'created', CREATED, None, None)

            # add to internal collection
            cls._objects.append(plan)

        elif plan.id != cls._generate_id(plan):
            cls._file_rename(plan)
            cls._file_write(plan)

        elif plan in DataAccess.changed:
            cls._file_write(plan)

        # write logged changes
        for log in DataAccess.changed_log.filter(obj=plan)[:]:
            DataAccess.log(plan, log.log, log.type, log.progress, log.minutes)
            DataAccess.changed_log.remove(log)

        # remove from collection of changed models
        if plan in DataAccess.changed:
            DataAccess.changed.remove(plan)
        
    @classmethod
    def delete(cls, plan, erase_history=True):
        """Delete an plan from file.

        :param plan: Action instance
        :type plan: Action
        """
        if plan.id is None:
            return

        # purge history from the logs unless explicitly wanted
        if erase_history:
            DataAccess.purge_object_from_logs(plan)

        # remove all references to the plan
        if plan.parent is not None:
            plan.parent.plans.remove(plan)
            plan.parent = None

        # first delete all actions in the plan
        for action in plan.actions:
            DataAccess.actions.delete(action, erase_history=erase_history)

        # now we recursively call delete on our children
        for child in plan.plans:
            DataAccess.plans.delete(child, erase_history=erase_history)

        # remove from interal list
        DataAccess.plans.remove(plan)

        # delete the file
        cls._file_delete(plan)

        DataAccess._print_output("'{}' deleted", plan.name)
        
    #==================================================================================================================
    # internal methods - file system (and eventually git)
    #==================================================================================================================
    @classmethod
    def _file_write(cls, plan):
        if plan.id is None:
            return

        # rewrite file
        with open('{}/.plan'.format(plan.id), 'w') as f:
            f.write(DataAccess._properties_to_json(plan) + '\n')
            for docline in plan.docs:
                f.write(docline + '\n')

    @classmethod
    def _file_delete(cls, plan):

        # delete the file
        import os
        os.remove(plan.id + '/.plan')
        os.rmdir(plan.id)

    @classmethod
    def _file_rename(cls, plan):
        """Rename a file for an plan.

        :param plan: Action instance
        :type plan: Action
        """
        # todo: copy contents to new path and rmtree() old path, or use os.rename()

        id = cls._generate_id(plan)

        import os
        try:
            os.rename(plan.id, id)
        except OSError:
            raise Exception("Cannot rename plan to '{}'. A plan with the same "
                            "name-generated id already exists.".format(plan.name))

        cls._regenerate_ids(plan)

    @classmethod
    def _regenerate_ids(cls, plan):

        plan.id = cls._generate_id(plan)

        for a in plan.actions:
            a.id = DataAccess.actions._generate_id(a)

        for p in plan.plans:
            cls._regenerate_ids(p)

    @classmethod
    def _file_create(cls, plan):
        """Create a file for an plan and sets the id..

        :param plan: Action to create a file for.
        :type plan: Action
        """

        id = cls._generate_id(plan)

        import os
        try:
            os.mkdir(id)
        except IOError:
            raise Exception("Cannot create plan named '{}'. A plan with the same "
                            "name-generated id already exists. Either assign the plan "
                            "to a different plan or change the name.".format(plan.name))

        plan.id = id

        cls._file_write(plan)

    @classmethod
    def _generate_id(cls, plan):
        """Return valid path from plan name.

        :param plan: Action instance
        :type plan: Action
        """

        if plan.name is None or plan.name == '':
            raise Exception('Plan has no name!')

        import re
        path = re.sub(r'[^A-Za-z0-9_!@#$%&\-+=\'":;\(\)\[\]\{\},.]', '_', plan.name)

        parent = plan.parent
        while parent is not None:
            path = '/'.join([re.sub(r'[^A-Za-z0-9_!@#$%&\-+=\'":;\(\)\[\]\{\},.]', '_', parent.name), path])
            parent = parent.parent

        id = '/'.join([DataAccess.life_prj_path, ACTIONS_DIR, path])

        # return filename
        return id


class LogEntryManager(ModelManager):

    #===================================================================================================================
    # public methods - CRUD
    #===================================================================================================================
    @classmethod
    def load(cls, jsonstr, log_file_name):
        instance = m.LogEntry()
        import json
        from dateutil import parser as p
        logdict = json.loads(jsonstr)
        instance.log_file_name = log_file_name
        instance.timestamp =  p.parse(logdict['timestamp'])
        instance.obj = logdict['obj']
        instance.log = logdict['log']
        instance.type = logdict['type']
        instance.progress = logdict['progress']
        instance.minutes = logdict['minutes']
        try:
            instance.logdate = p.parse(instance.log_file_name).date()
        except:
            instance.logdate = p.parse(instance.timestamp).date()

        cls._objects.append(instance)
        return instance

    @classmethod
    def save(cls, logentry):
        """Save a log entry to file.

        :param logentry: LogEntry instance
        :type logentry: LogEntry
        """

    @classmethod
    def create(cls, obj, log, type, progress, minutes, log_file_name):
        instance = m.LogEntry()
        instance.log_file_name = log_file_name
        import datetime
        instance.timestamp = datetime.datetime.now()
        instance.obj = obj
        instance.log = log
        instance.type = type
        instance.progress = progress
        instance.minutes = minutes
        from dateutil import parser as p
        try:
            instance.logdate = p.parse(instance.log_file_name).date()
        except:
            instance.logdate = p.parse(instance.timestamp).date()
        return instance

    @classmethod
    def to_json(cls, log):
        """

        :param log: Log object.
        :type log: m.LogEntry
        """

        import json
        logdict = {}
        from datetime import datetime
        datetime.today().isoformat()
        logdict['timestamp'] = str(log.timestamp)
        logdict['obj'] = log.obj.name
        logdict['log'] = log.log
        logdict['type'] = log.type
        logdict['progress'] = log.progress
        logdict['minutes'] = log.minutes
        dump = json.dumps(logdict)
        return dump


class TargetManager(ModelManager):

    #===================================================================================================================
    # collection methods
    #===================================================================================================================
    @classmethod
    def active(cls):
        return cls._objects.filter(isactive=True)

    @classmethod
    def inactive(cls):
        return cls._objects.filter(isactive=False)

    #===================================================================================================================
    # public methods - CRUD
    #===================================================================================================================
    @classmethod
    def delete(cls, target):
        model = target.model
        target.model.targets.remove(target)
        model.save()


class DataAccess(object):
    """Data access layer"""

    #===================================================================================================================
    # class variables
    #===================================================================================================================
    life_prj_path = None
    log_file_name = None

    #===================================================================================================================
    # initialization methods
    #===================================================================================================================
    def __init__(self, life_path, stdout=None):
        raise Exception("Static class cannot be instantiated.")

    @classmethod
    def setup(cls, life_path, stdout=None, logfilename=None):
        # set up data access
        cls.life_prj_path = life_path

        if logfilename is None:
            import datetime
            cls.log_file_name = datetime.datetime.today().strftime('%Y-%m-%d')

        cls.stdout = stdout

        m.dal = DataAccess

        # connect model data access classes
        cls.actions = ActionManager
        cls.plans = PlanManager
        cls.logentries = LogEntryManager
        cls.targets = TargetManager
        cls.changed = []
        cls.changed_log = qlist()

        # load models
        cls.ignore_changes = True
        cls._load_actions_and_plans('/'.join([cls.life_prj_path, ACTIONS_DIR]))
        cls._load_logs()
        cls.ignore_changes = False

    #===================================================================================================================
    # private methods
    #===================================================================================================================
    @classmethod
    def _load_actions_and_plans(cls, path, plan=None, depth=0):
        import os
        list = os.listdir(path)

        if depth == 0:
            cls.plans._objects = qlist()
            cls.actions._objects = qlist()

        # iterate through files and directories in actions directory
        for d in list:

            # treat directories as plans and files as actions
            if os.path.isdir(path + '/' + d) is True:

                # load plans
                p = cls.plans.load(path + '/' + d, plan)

                # recursively load actions and plans
                cls._load_actions_and_plans(path + '/' + d, p, depth=depth+1)

            else:
                # ignore .plans file, it is processed when loading a plans
                if d != '.plan':
                    # load actions
                    a = cls.actions.load(path + '/' + d, plan)

    @classmethod
    def _load_logs(cls):

        cls.logentries._objects = qlist()

        import os
        list_ = os.listdir('/'.join([cls.life_prj_path, LOGS_DIR]))

        # iterate through files in logs directory
        for d in list_:

            # don't load .changes log files, they are only logged for debug info
            if not d.endswith('.changes') and os.path.isfile('/'.join([cls.life_prj_path, LOGS_DIR, d])):

                with open('/'.join([cls.life_prj_path, LOGS_DIR, d])) as logfile:

                    # load log entry
                    for line in logfile.readlines():

                        # load line into LogEntry instance
                        logentry = cls.logentries.load(line, d)

                        # resolve model reference
                        model = cls.actions.get(name=logentry.obj)
                        if model is None:
                            model = cls.plans.get(name=logentry.obj)

                        # relate logentry to models
                        if model is not None:
                            logentry.obj = model
                            model.history.append(logentry)
                            parent = model.parent
                            while parent is not None:
                                parent.history.append(logentry)
                                parent = parent.parent

    @classmethod
    def _print_output(cls, line, *args):
        if cls.stdout is None:
            return
        try:
            cls.stdout.write('{}\n'.format(line).format(*args))
        except:
            pass  # it's only informational, no need to freak out if something goes awry

    @staticmethod
    def _properties_to_json(model):
        """Return properties in json format.

        :param model: A model instance
        :type model: Model
        """

        # compile a full listing of the command thesaurus
        jsondictionary = {}
        for attr in model.__dict__:
            if attr.startswith('_') and not attr.startswith('__') and attr.endswith('_') and not attr.endswith('__'):
                obj = getattr(model, attr)
                if attr == '_targets_':
                    list_of_serialized_targets = []
                    for target in obj:
                        t = DataAccess._properties_to_json(target)
                        list_of_serialized_targets.append(t)
                    jsondictionary[attr[1:len(attr) - 1]] = list_of_serialized_targets
                elif isinstance(obj, int) or isinstance(obj, float):
                    jsondictionary[attr[1:len(attr) - 1]] = obj
                elif hasattr(obj, '__iter__') and len(obj) > 0:  # tags
                    if isinstance(obj[0], str) or isinstance(obj[0], unicode):
                        jsondictionary[attr[1:len(attr) - 1]] = ' '.join(obj)
                    else:
                        for i, item in enumerate(obj):
                            obj[i] = str(item)
                        jsondictionary[attr[1:len(attr) - 1]] = obj
                elif not hasattr(obj, 'func_name'):  # we don't want functions
                    jsondictionary[attr[1:len(attr) - 1]] = str(obj)

        # we're saving now, so update the persisted values
        model.persisted = jsondictionary
        from json import dumps
        return dumps(jsondictionary)

    #===================================================================================================================
    # logging methods
    #===================================================================================================================
    @classmethod
    def log_file_date_to_datetime(cls):
        import datetime
        return datetime.datetime.strptime(cls.log_file_name, '%Y-%m-%d')

    @classmethod
    def get_log_file_names(cls, history):
        """Return distinct list of log file names within a list of LogEntry objects.

        :param history: List of LogEntry instances.
        :type history: list<LogEntry>
        """

        if len(history) == 0:
            return None

        log_filename_list = []
        for item in history:
            if item.log_file_name not in log_filename_list:
                log_filename_list.append(item.log_file_name)

        return log_filename_list

    @classmethod
    def purge_object_from_logs(cls, obj):
        """Remove all log entries for an action and clear the ``action.history`` property."""

        # get distinct list of log file names from the action history
        log_filenames = cls.get_log_file_names(obj.history)

        # no log history
        if log_filenames is None:
            return

        # loop over a sliced copy of self.logentries to avoid skipping items
        # due to the internal indexing of the iteration
        for logentry in cls.logentries.all()[:]:
            if logentry.obj is obj:
                cls.logentries.remove(logentry)
                if logentry.type == 3 and isinstance(obj, m.Action) and obj.parent is not None:
                    obj.parent.history.remove(logentry)

        # read lines from each logfile and then rewrite the
        # logfile, omitting lines that are for this action
        for log_filename in log_filenames:
            with open('/'.join([cls.life_prj_path, LOGS_DIR, log_filename]), 'r') as logfile:
                lines = logfile.readlines()

            with open('/'.join([cls.life_prj_path, LOGS_DIR, log_filename]), 'w') as logfile:
                for line in lines:
                    if line.find('"obj": "' + obj.name + '"') < 0:
                        logfile.write(line)

        # reset object's history property
        obj.history = qlist()

    @classmethod
    def log(cls, obj, log, type, progress, minutes):

        if not isinstance(obj, m.Action) and not isinstance(obj, m.Plan):
            raise Exception("Expected Action or Plan.")

        if type == 3:
            cls.log_execution(obj, log, progress, minutes)
        else:
            cls.log_changes(obj, log, type, progress, minutes)

    @classmethod
    def log_changes(cls, obj, log, type, progress, minutes):

        openmode = 'a'
        import os
        if not os.path.exists('/'.join([cls.life_prj_path, LOGS_DIR, cls.log_file_name]) + '.changes'):
            openmode = 'w'

        with open('/'.join([cls.life_prj_path, LOGS_DIR, cls.log_file_name]) + '.changes', openmode) as logfile:
            lobj = cls.logentries.create(obj, log, type, progress, minutes, cls.log_file_name)
            logfile.write(cls.logentries.to_json(lobj) + '\n')
            cls._print_output("'{}' {}".format(obj.name, log))

    @classmethod
    def log_execution(cls, obj, log, progress, minutes):

        openmode = 'a'
        import os
        if not os.path.exists('/'.join([cls.life_prj_path, LOGS_DIR, cls.log_file_name])):
            openmode = 'w'

        with open('/'.join([cls.life_prj_path, LOGS_DIR, cls.log_file_name]), openmode) as logfile:
            lobj = cls.logentries.create(obj, log, 3, progress, minutes, cls.log_file_name)
            logfile.write(cls.logentries.to_json(lobj) + '\n')
            obj.history.append(lobj)
            cls.logentries.append(lobj)
            parent = obj.parent
            while parent is not None:
                parent.history.append(lobj)
                parent = parent.parent
            cls._print_output("'{}' {}".format(obj.name, log))

    @classmethod
    def save(cls):
        for model in cls.changed[:]:
            model.save()
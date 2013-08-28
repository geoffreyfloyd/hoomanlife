from hoomanpy import qlist
from datetime import timedelta, datetime, date

dal = None  # data access layer

(CREATED,
 UPDATED,
 DELETED,
 EXECUTED) = range(4)


#=======================================================================================================================
# directly persisted models
#=======================================================================================================================
class BaseModel(object):

    """A named, taggable, history"""

    #===================================================================================================================
    # internal methods
    #===================================================================================================================
    def __init__(self):

        # persistance attrs
        self.ignore_changes = False
        self.persisted = {}
        self.id = None

        # persisted attrs
        self._name_ = None
        self._tags_ = qlist(listener=self._tags_listener, before_add=self._tags_before_add)
        self._targets_ = qlist(listener=self._targets_listener)

        # explicit persistance - not in json
        self._docs = qlist(listener=self._docs_listener)

    def __getattr__(self, item):
        if item in self.persisted:
            return getattr(self, '_{}_'.format(item))
        else:
            raise AttributeError(item)

    def __str__(self):
        if self.name is None:
            return ''

        return self.name

    def __unicode__(self):
        if self.name is None:
            return ''

        return self.name

    def _on_changed(self, logmsg, type, progress, minutes):
        if dal.ignore_changes or self.ignore_changes:
            return
        dal.changed_log.append(LogEntry(self, logmsg, type, progress, minutes))
        if self not in dal.changed:
            dal.changed.append(self)

    def _tags_before_add(self, obj, ismultiple):
        if not ismultiple:
            obj = [obj]

        for tag in obj[:]:
            # validate type
            if not isinstance(tag, str) and not isinstance(tag, unicode):
                raise TypeError("Expected str or unicode object.")
            # exclude duplicates
            if tag in self.tags:
                obj.remove(tag)

        if ismultiple:
            return obj, False
        else:
            if len(obj) == 0:
                return None, True
            else:
                return obj[0], False

    def _tags_listener(self, changelist, change):
        for item in changelist:
            self._on_changed("{} tag '{}'".format(change, item), UPDATED, None, None)

    def _targets_listener(self, changelist, change):
        for item in changelist:
            self._on_changed("{} target '{}'".format(change, item), UPDATED, None, None)
            if change == 'added':
                item.model = self
                dal.targets.append(item)
            elif change == 'removed':
                item.model = None
                dal.targets.remove(item)

    def _docs_listener(self, changelist, change):
        for item in changelist:
            self._on_changed("{} doc line '{}'".format(change, item), UPDATED, None, None)

    def _is_protected_attribute(self, attrname):
        return hasattr(self, attrname) or hasattr(self, '_{}'.format(attrname))

    #===================================================================================================================
    # property methods
    #===================================================================================================================
    @property
    def name(self):
        return self._name_

    @name.setter
    def name(self, value):
        self._name_ = value
        self._on_changed("renamed", UPDATED, None, None)

    @property
    def tags(self):
        return self._tags_

    @tags.setter
    def tags(self, value):
        if not isinstance(value, qlist):
            raise Exception("Collection must be of type qlist.")

        if self._tags_ is not None:
            self._tags_.listener = None
            self._tags_.before_add = None

        self._tags_ = value
        self._tags_.listener = self._tags_listener
        self._tags_.before_add = self._tags_before_add

    @property
    def docs(self):
        return self._docs

    @docs.setter
    def docs(self, value):
        if not isinstance(value, qlist):
            raise Exception("Collection must be of type qlist.")

        if self._docs is not None:
            self._docs.listener = None
            self._docs.before_add = None

        self._docs = value
        self._docs.listener = self._docs_listener
        self._docs.before_add = None

    @property
    def targets(self):
        return self._targets_

    @targets.setter
    def targets(self, value):
        if not isinstance(value, qlist):
            raise Exception("Collection must be of type qlist.")

        if self._targets_ is not None:
            self._targets_.listener = None
            self._targets_.before_add = None

        self._targets_ = value
        self._targets_.listener = self._targets_listener
        self._targets_.before_add = None

    def get_id(self):
        return self.id

    def get_last_execution_date(self):
        list_ = self.history.sort('logdate').flip()
        if len(list_) > 0:
            return list_[0].logdate.strftime('%Y-%m-%d')
        else:
            return 'Never'

    #===================================================================================================================
    # public methods
    #===================================================================================================================
    def add_docs(self, lines):

        # convert to list if str
        if isinstance(lines, str) or isinstance(lines, unicode):
            lines = lines.split('\\n')

        # walk through list and convert items to lists in case newline chars were sent
        for line in lines:
            line = line.split('\\n')
            for linepart in line:
                self.docs.append(linepart)

    def add_target(self, freq, starts, measure, period_target=1, interval=1):
        target = Target(freq, starts, measure, period_target=period_target, interval=interval)
        self.targets.append(target)

    def clear_docs(self):
        self.docs.clear()

    #===================================================================================================================
    # extended attribute methods
    #===================================================================================================================
    def get_attributes(self):
        attr_hasnotes = '_'
        attr_hashistory = '_'
        if len(self.docs) > 0:
            attr_hasnotes = 'N'
        if len(self.history) > 0:
            attr_hashistory = 'H'

        # append da_action attrs to description
        return attr_hasnotes + attr_hashistory

    def set_attribute(self, attrname, value):
        # ensure it is not a protected attribute
        if self._is_protected_attribute(attrname):
            raise Exception("{} is a protected attribute and must be explicitly set.".format(attrname))

        fail = False
        if isinstance(value, str) or isinstance(value, unicode):
            # try cast to float, then to int if float fails
            if '.' in value:
                try:
                    value = float(value)
                except ValueError:
                    try:
                        value = int(value)
                    except ValueError:
                        pass

        # set attribute
        setattr(self, '_{}_'.format(attrname), value)

        self._on_changed("attribute '{}' set to '{}'".format(attrname, str(value)), UPDATED, None, None)

    def remove_attribute(self, attrname):
        # ensure it is not a protected attribute
        if self._is_protected_attribute(attrname):
            raise Exception("{} is a protected attribute and cannot be removed.".format(attrname))

        if hasattr(self, '_{}_'.format(attrname)):
            delattr(self, '_{}_'.format(attrname))

        self._on_changed(self, "removed attribute '{}'".format(attrname), UPDATED, None, None)

    def increment_numeric_attribute(self, attrname, increment):
        # if attribute already exists, then add existing to increment
        if hasattr(self, '_{}_'.format(attrname)):
            increment = increment + getattr(self, '_{}_'.format(attrname))

        # set new attribute value
        self.set_attribute(attrname, increment)


class ActionableModel(BaseModel):

    #===================================================================================================================
    # class variables
    #===================================================================================================================
    status_dict = {
        'active': ['active', 'current'],
        'inactive': ['X', 'x', 'done', 'completed', 'finished', 'inactive'],
        'future': ['>', 'future', 'maybe', 'someday']
    }

    #===================================================================================================================
    # internal methods
    #===================================================================================================================
    def __init__(self):

        super(ActionableModel, self).__init__()

        # non-persisted attrs
        self.history = qlist()
        self._on_logged = None

        # persisted attrs
        self._status_ = 'active'
        self._progress_ = 0
        self._minutes_ = 0
        self._order_ = 0

    #===================================================================================================================
    # property methods
    #===================================================================================================================
    @property
    def minutes(self):
        return self._minutes_

    @minutes.setter
    def minutes(self, value):
        self._minutes_ = value
        self._on_changed('updated minutes to {}'.format(value), UPDATED, None, None)

    @property
    def progress(self):
        return self._progress_

    @progress.setter
    def progress(self, value):

        if isinstance(value, str) or isinstance(value, unicode):
            try:
                value = int(value)
            except:
                raise Exception('Invalid progress (valid is 0-100).')

        if value < 0 or value > 100:
            raise Exception('Invalid progress (valid is 0-100).')

        self._progress_ = value
        self._on_changed('updated progress to {}'.format(value), UPDATED, None, None)

    @property
    def order(self):
        return self._order_

    @order.setter
    def order(self, value):

        if isinstance(value, str) or isinstance(value, unicode):
            try:
                value = int(value)
            except:
                raise Exception('Invalid order (valid is 0+).')

        if value < 0:
            raise Exception('Invalid order (valid is 0+).')

        self._order_ = value
        self._on_changed('updated order to {}'.format(value), UPDATED, None, None)

    @property
    def status(self):
        return self._status_

    @status.setter
    def status(self, value):
        if value not in self.status_dict:
            raise Exception("{} is not a recognized status.".format(str(value)))

        if value == self.status:
            return

        self._status_ = value

        self._on_changed('updated status to ' + value, UPDATED, None, None)

    #===================================================================================================================
    # public methods
    #===================================================================================================================
    def clear_history(self):
        dal.purge_object_from_logs(self)

    def log(self, progress=None, minutes=None):

        diff = None

        if self._progress_ > 0 and progress is None:
            progress == 100

        if progress is not None:
            diff = progress - self.progress
            self._progress_ = progress

        if minutes is not None:
            self._minutes_ += minutes

        self._on_changed('executed', EXECUTED, diff, minutes)

        if self._on_logged is not None:
            self._on_logged(progress=progress, minutes=minutes)


class Action(ActionableModel):

    """Action model."""

    #===================================================================================================================
    # class variables
    #===================================================================================================================
    type_dict = {
        'todo': ['todo', 'do', 'standard'],
        'routine': ['R', 'r', 'routine'],
        'option': ['O', 'o', 'option'],
        'queue': ['^', 'queue']
    }

    #===================================================================================================================
    # object overrides
    #===================================================================================================================
    def __init__(self):
        super(Action, self).__init__()

        # persisted attrs
        self._type_ = None

        # non-persisted attrs
        self._parent = None

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return self.name

    @staticmethod
    def load(id, data, parent=None):
        obj = Action()
        obj.id = id
        obj.ignore_changes = True

        for key, value in data.iteritems():
            if key not in ['targets', 'docs', 'persisted']:
                setattr(obj, "_{}_".format(key), value)

        obj.targets.extend(data['targets'])
        obj.docs.extend(data['docs'])
        #obj.persisted = data['persisted']

        if parent is not None:
            parent.actions.append(obj)

        obj.ignore_changes = False

        return obj

    @staticmethod
    def create(name, type='todo', status=None, parent=None, tags=None):
        obj = Action()
        obj.ignore_changes = True
        obj.name = name
        if type is None and parent is not None and parent.type in ['routine', 'option', 'queue']:
            obj.type = parent.type
            if type == 'queue':
                parent.add_to_queue(obj)
        elif type is None:
            obj.type = 'todo'
        else:
            obj.type = type
        if status is None:
            obj.status = 'active'
        else:
            obj.status = status

        if tags is not None:
            obj.tags.extend(tags)

        if parent is not None:
            parent.actions.append(obj)

        obj.ignore_changes = False
        return obj

    def _on_logged(self, progress=None, minutes=None):
        # inactive and unqueue actions that have been fully completed and are not
        # repeating action types (todo, queue)
        completed = (progress is None and minutes is None) or progress == 100
        if completed:
            if self.type == 'todo':
                self.status = "inactive"
            elif self.type == 'queue' and self.plan is not None:
                self.plan.remove_from_queue(self)

        # end targets that have been met to completion
        for target in self.targets:
            if (target.measure == target.BY_EXECUTION and target.met_after <= len(self.history)) or \
               (target.measure == target.BY_PROGRESS and target.met_after <= self.progress) or \
               (target.measure == target.BY_TIME and target.met_after <= self.minutes):
                target._ends_ = datetime.today().date()
                self._on_changed("Ended target", UPDATED, None, None)

    #===================================================================================================================
    # property methods
    #===================================================================================================================
    @property
    def type(self):
        return self._type_

    @type.setter
    def type(self, value):
        if value not in self.type_dict:
            raise Exception("{} is not a recognized type.".format(str(value)))

        if value == self.type:
            raise Exception("'{}' is already set to '{}'".format(self.name, value))

        if value == 'queue' and self.parent is None:
            raise Exception("Only plans can hold queues. Add '{}' to a plan before queueing.".format(self.name))

        self._type_ = value

        if value == 'queue':
            self.parent.add_to_queue(self)

        self._on_changed('updated type to ' + value, UPDATED, None, None)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if self._parent is value:
            return

        # if self._parent is not None:
        #     self._parent.actions.remove(self)

        self._parent = value

        # if self._parent is not None:
        #     self._parent.actions.append(self)

        self._on_changed('updated parent to ' + str(value), UPDATED, None, None)

    def get_desc(self):

        has_progress = self.progress > 0
        has_minutes = self.minutes > 0
        desc = self.name

        # append progress attrs to description
        if has_progress and has_minutes:
            desc += ' ({}% - {}min)'.format(self.progress, self.minutes)
        elif has_progress:
            desc += ' ({}%)'.format(self.progress)
        elif has_minutes:
            desc += ' ({}min)'.format(self.minutes)

        return desc

    def get_plan_name(self):
        if self.parent is not None:
            return str(self.parent)
        else:
            return ''

    #===================================================================================================================
    # data access methods
    #===================================================================================================================
    def save(self):
        if self not in dal.changed:
            return
        dal.actions.save(self)


class Plan(ActionableModel):

    """Plan model."""

    #===================================================================================================================
    # class variables
    #===================================================================================================================
    type_dict = {
        'focus': ['focus'],
        'todo': ['todo', 'project', 'plan'],
        'routine': ['R', 'r', 'routine'],
        'option': ['O', 'o', 'option', 'curriculum'],
        'queue': ['^', 'queue']
    }

    #===================================================================================================================
    # object overrides
    #===================================================================================================================
    def __init__(self):
        super(Plan, self).__init__()

        # persisted attrs
        self._type_ = None

        # non-persisted attrs
        self._parent = None
        self._actions = qlist(listener=self._actions_listener)
        self._plans = qlist(listener=self._plans_listener)

    def __unicode__(self):
        name = self.name
        parent = self.parent
        while parent is not None:
            name = parent.name + ' > ' + name
            parent = parent.parent
        return name

    def __str__(self):
        if self.name is None:
            return ''

        name = self.name
        parent = self.parent
        while parent is not None:
            name = parent.name + ' > ' + name
            parent = parent.parent
        return name

    @staticmethod
    def load(id, data, parent=None):

        obj = Plan()

        obj.id = id
        obj.ignore_changes = True

        for key, value in data.iteritems():
            if key not in ['targets', 'docs', 'persisted']:
                setattr(obj, "_{}_".format(key), value)

        obj.targets.extend(data['targets'])
        obj.docs.extend(data['docs'])
        #obj.persisted = data['persisted']

        if parent is not None:
            parent.plans.append(obj)

        obj.ignore_changes = False

        return obj

    @staticmethod
    def create(name, type=None, status='active', parent=None, tags=None):
        obj = Plan()

        obj.ignore_changes = True
        obj.name = name
        if type is None and parent is not None and parent.type in ['routine', 'option', 'queue']:
            obj.type = parent.type
        elif type is None:
            obj.type = 'todo'
        else:
            obj.type = type
        if status is None:
            obj.status = 'active'
        else:
            obj.status = status
        obj.status = status

        if tags is not None:
            obj.tags.extend(tags)

        if parent is not None:
            parent.plans.append(obj)

        obj.ignore_changes = False
        return obj

    def _on_logged(self, progress=None, minutes=None):
        # end targets that have been met to completion
        for target in self.targets:
            if (target.measure == target.BY_EXECUTION and target.met_after <= len(self.history)) or \
               (target.measure == target.BY_PROGRESS and target.met_after <= self.progress) or \
               (target.measure == target.BY_TIME and target.met_after <= self.minutes):
                target._ends_ = datetime.today().date()
                self._on_changed("Ended target", UPDATED, None, None)

    def _actions_listener(self, changelist, change):
        for item in changelist:
            self._on_changed("{} action '{}'".format(change, item), UPDATED, None, None)
            if change == 'added':
                item.parent = self
            elif change == 'removed':
                item.parent = None

    def _plans_listener(self, changelist, change):
        for item in changelist:
            self._on_changed("{} plan '{}'".format(change, item), UPDATED, None, None)
            if change == 'added':
                item.parent = self
            elif change == 'removed':
                item.parent = None

    #===================================================================================================================
    # property methods
    #===================================================================================================================
    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self, value):
        if not isinstance(value, qlist):
            raise Exception("Collection must be of type qlist.")

        if self._actions is not None:
            self._actions.listener = None
            self._actions.before_add = None

        self._actions = value
        self._actions.listener = self._actions_listener
        self._actions.before_add = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if self._parent is value:
            return

        # if self._parent is not None:
        #     self._parent.plans.remove(self)

        self._parent = value

        # if self._parent is not None:
        #     self._parent.plans.append(self)

        self._on_changed('updated parent to ' + str(value), UPDATED, None, None)

    @property
    def plans(self):
        return self._plans

    @plans.setter
    def plans(self, value):
        if not isinstance(value, qlist):
            raise Exception("Collection must be of type qlist.")

        if self._plans is not None:
            self._plans.listener = None
            self._plans.before_add = None

        self._plans = value
        self._plans.listener = self._plans_listener
        self._plans.before_add = None

    @property
    def type(self):
        return self._type_

    @type.setter
    def type(self, value):
        if value not in self.type_dict:
            raise Exception("{} is not a recognized type.".format(str(value)))

        if value == self.type:
            raise Exception("'{}' is already set to '{}'".format(self.name, value))

        self._type_ = value

        self._on_changed('updated type to ' + value, UPDATED, None, None)

    #===================================================================================================================
    # public methods - queues
    #===================================================================================================================
    def get_next_in_queue(self):
        list_ = self.actions.filter(status='active', type='queue').sort('name').sort('order')
        if len(list_) == 0:
            return None
        return list_[0]

    def renumber_queue(self):
        list_ = self.actions.filter(status='active', type='queue').sort('name').sort('order')
        if len(list_) == 0:
            return
        queue = 0
        for action in list_:
            queue += 1
            action.order = queue

    def get_max_queue_number(self):
        list_ = self.actions.filter(status='active', type='queue').sort('name').sort('order').flip()
        if len(list_) == 0:
            return 0
        return list_[0].order

    def add_to_queue(self, action):
        action.order = self.get_max_queue_number() + 1

    def remove_from_queue(self, action):
        action.order = 0
        action.status = "inactive"
        self.renumber_queue()

    def move_up_in_queue(self, action):
        if action.order == 1:
            return
        else:
            self.switch_queue_order(action.order, action.order - 1)

    def move_down_in_queue(self, action):
        if action.order == self.get_max_queue_number():
            return
        else:
            self.switch_queue_order(action.order, action.order + 1)

    def switch_queue_order(self, slot1, slot2):
        list_ = self.actions.filter(order__in=[slot1, slot2])
        for action in list_:
            if action.order == slot1:
                action.order = slot2
            elif action.order == slot2:
                action.order = slot1

    #===================================================================================================================
    # data access methods
    #===================================================================================================================
    def save(self):
        if self not in dal.changed:
            return
        dal.plans.save(self)


class Tag(BaseModel):

    """Tag model."""

    #===================================================================================================================
    # class variables
    #===================================================================================================================
    type_dict = {
        'standard': ['none', 'custom'],
        'focus': [''],
        'reason': ['virtue', 'drive', 'logic'],
        'need': ['physiological', 'safety', 'belonging', 'self-esteem', 'self-actualization'],
        'requirement': ['tool', 'environment', 'location']
    }

    #===================================================================================================================
    # object overrides
    #===================================================================================================================
    def __init__(self):
        super(Plan, self).__init__()

        # persisted attrs
        self._type_ = type

        # non-persisted attrs
        self._parent = None
        self._actions = qlist(listener=self._actions_listener)
        self._plans = qlist(listener=self._plans_listener)


#=======================================================================================================================
# indirectly persisted models
#=======================================================================================================================
class LogEntry(object):

    """LogEntry model."""

    #===================================================================================================================
    # internal methods
    #===================================================================================================================
    def __init__(self, obj=None, log=None, type=None, progress=None, minutes=None):
        self.log_file_name = None
        self.logdate = None
        self.timestamp = None

        self.obj = obj
        self.log = log
        self.type = type
        self.progress = progress
        self.minutes = minutes

    def __str__(self):
        return self.timestamp.strftime()


class Target(object):

    """An execution target for an action or plan by executions, progress percentage, or time.

    :ivar freq: The frequency. Can also be a single date for one target occurrence (ie. due date)
                 or a tuple of dates for a single target period.
    :type freq: int|datetime.datetime|tuple<datetime.datetime>
    :ivar starts: The date the target becomes active; the beginning of the first target period.
    :type starts: datetime.datetime
    :ivar measure: The type of target: BY_EXECUTION-0, BY_PROGRESS-1, or BY_TIME-2
    :type measure: int
    :ivar period_target: Depends on measure: BY_EXECUTION - The target number of executions within a single period.
                                             BY_PROGRESS - The target percentage of progress within a single period.
                                             BY_TIME - The target number of minutes spent within a single period.
    :type period_target: int
    :ivar interval: If frequency is recurring, the multiple of the frequency that periods are set at. Ie. Frequency
                     of weekly with an interval of 2 would set target periods at every two weeks.
    :type interval: int|datetime.date|list<datetime.date>
    :ivar met_after: Depends on measure: BY_EXECUTION - Retire target after x num completions.
                                         BY_PROGRESS - Retire target after x percent is complete.
                                         BY_TIME - Retire target after x minutes.
    :type met_after: int
    """

    #===================================================================================================================
    # class variables
    #===================================================================================================================
    freq_dict = {
        0: ['yearly', 'yr', 'yrs', 'year', 'years'],
        1: ['monthly', 'mo', 'mos', 'month', 'months'],
        2: ['weekly', 'wk', 'wks', 'week', 'weeks'],
        3: ['daily', 'day', 'days'],
        4: ['once'],
        5: ['dates']
    }

    measure_dict = {
        0: ['execution'],
        1: ['progress'],
        2: ['time']
    }

    (YEARLY,
     MONTHLY,
     WEEKLY,
     DAILY,
     ONCE,
     DATES) = range(6)

    (BY_EXECUTION,
     BY_PROGRESS,
     BY_TIME) = range(3)

    @staticmethod
    def todate(dateobj):
        if isinstance(dateobj, datetime):
            return dateobj.date()
        elif isinstance(dateobj, date):
            return dateobj
        elif isinstance(dateobj, str) or isinstance(dateobj, unicode):
            from dateutil import parser as p
            return Target.todate(p.parse(dateobj))
        else:
            raise Exception("Unrecognized type.")

    def __init__(self, freq, starts, measure, period_target=None,
                 interval=None, offinterval=0, met_after=None,
                 breakafter=None, breakfreq=None, breakinterval=None):

        # set defaults when nothing is supplied
        if period_target is None:
            if measure == 0:
                period_target = 1
            elif measure == 1:
                period_target = 100
            elif measure == 2:
                period_target = 60

        if interval is None:
            if freq in [0, 1, 2, 3]:
                interval = 1
            elif freq == 4:
                interval = starts
            elif freq == 5:
                interval = [starts]

        # for progress targets, close target after 100% unless otherwise specified
        if measure == 1 and met_after is None:
            met_after = 100

        # initialize instance variables
        self._freq_ = freq
        self._starts_ = Target.todate(starts)
        self._ends_ = None
        self._measure_ = measure
        self._period_target_ = period_target
        self._interval_ = interval
        self._offinterval_ = offinterval
        self._met_after_ = met_after
        self._breakafter_ = breakafter
        self._breakfreq_ = breakfreq
        self._breakinterval_ = breakinterval

        if self.freq < 4:
            if self._offinterval_ >= self._interval_:
                raise Exception("offinterval must be less than interval.")

        # calculate all the periods since this target started
        self.periods = self.calculate_periods(datetime.today().date())

        # specific scheduling details (usually not required)
        # self.wkst = wkst  # project settings should decide what day the week starts on. default to monday.

    def __str__(self):
        return "Target {}".format(self.measuredesc)

    @staticmethod
    def load(freq, starts, measure, period_target=None,
                 interval=None, offinterval=0, met_after=None,
                 breakafter=None, breakfreq=None, breakinterval=None):

        if isinstance(starts, str) or isinstance(starts, unicode):
            starts = Target.todate(starts)
        if isinstance(interval, str) or isinstance(interval, unicode):
            interval = Target.todate(interval)
        elif hasattr(interval, '__iter__'):
            for i, item in enumerate(interval):
                interval[i] = Target.todate(item)

        obj = Target(freq, starts, measure, period_target, interval, offinterval,
                     met_after, breakafter, breakfreq, breakinterval)

        return obj

    #===================================================================================================================
    # standard properties
    #===================================================================================================================
    @property
    def freq(self):
        return self._freq_

    @property
    def starts(self):
        return self._starts_

    @property
    def interval(self):
        return self._interval_

    @property
    def offinterval(self):
        return self._offinterval_

    @property
    def measure(self):
        return self._measure_

    @property
    def met_after(self):
        return self._met_after_

    @property
    def period_target(self):
        return self._period_target_

    @property
    def breakafter(self):
        return self._breakafter_

    @property
    def breakfreq(self):
        return self._breakfreq_

    @property
    def breakinterval(self):
        return self._breakinterval_

    #===================================================================================================================
    # string formatting properties
    #===================================================================================================================
    @property
    def freqdesc(self):
        if self.interval > 1:
            return Target.freq_dict[self.freq][2]
        else:
            return Target.freq_dict[self.freq][1]

    @property
    def measuredesc(self):
        return Target.measure_dict[self.measure][0]

    @property
    def measure_symbol(self):
        if self.measure == 0:
            return ''
        elif self.measure == 1:
            return '%'
        elif self.measure == 2:
            return 'min'

    @property
    def period_target_desc(self):
        if self.measure != 2:
            return "{}{}".format(self.period_target, self.measure_symbol)
        else:
            return Duration.minutes_to_duration(self.period_target)

    @property
    def period_desc(self):
        dtfrom, dtto = self.get_current_period()
        if dtfrom == dtto:
            return str(dtfrom)
        else:
            return "{} - {}".format(dtfrom, dtto)

    @property
    def progress(self):
        history = self.model.history.sort('timestamp').flip()

        period_from, period_to = self.get_period(datetime.today().date())

        count = 0
        progress = 0
        minutes = 0

        for log in history:
            if period_from <= log.logdate <= period_to:
                count += 1
                if log.progress is not None:
                    progress += log.progress
                if log.minutes is not None:
                    minutes += log.minutes
            elif log.logdate < period_from:
                break

        if self.measure == 0:
            return "{}/{}".format(count, self.period_target)
        elif self.measure == 1:
            return "{}/{}{}".format(progress, self.period_target, self.measure_symbol)
        elif self.measure == 2:
            return "{}/{}".format(Duration.minutes_to_duration(minutes),
                                  Duration.minutes_to_duration(self.period_target))

    @property
    def daysleft(self):
        period_from, period_to = self.get_period(datetime.today().date())

        daysleft = (period_to - datetime.today().date()).days + 1  # including today
        dayspassed = (datetime.today().date() - period_from).days
        daystotal = (period_to - period_from).days + 1  # including today
        return "{}/{}/{}".format(dayspassed, daysleft, daystotal)

    #===================================================================================================================
    # calculated properties
    #===================================================================================================================
    @property
    def average(self):

        history = self.model.history.sort('timestamp')

        periods = {}

        target = len(self.periods[:-1]) * self.period_target
        actual = 0

        history_enumerator = enumerate(history)

        try:
            logstepper, log = history_enumerator.next()
        except StopIteration:
            log = None

        for period in self.periods[:-1]:
            dtfrom, dtto = period
            periods[(dtfrom.strftime("%Y-%m-%d"), dtfrom, dtto)] = 0

            while log is not None and log.logdate <= dtto:
                if dtfrom <= log.logdate <= dtto:
                    periods[(dtfrom.strftime("%Y-%m-%d"), dtfrom, dtto)] += self._add_log_progress(log)
                try:
                    logstepper, log = history_enumerator.next()
                except StopIteration:
                    log = None

            actual += periods[(dtfrom.strftime("%Y-%m-%d"), dtfrom, dtto)]

        if actual == 0 or target == 0:
            return "0%"
        else:
            return "{:.2f}%".format((float(actual) / float(target)) * 100)

    @property
    def isactive(self):
        return self._ends_ is None or self._ends_ < datetime.date()

    @property
    def thisperiod(self):

        history = self.model.history.sort('timestamp')
        target = self.period_target
        actual = 0

        history_enumerator = enumerate(history)

        try:
            logstepper, log = history_enumerator.next()
        except StopIteration:
            log = None

        dtfrom, dtto = self.periods[-1]

        while log is not None and log.logdate <= dtto:
            if dtfrom <= log.logdate <= dtto:
                actual += self._add_log_progress(log)
            try:
                logstepper, log = history_enumerator.next()
            except StopIteration:
                log = None

        if actual == 0 or target == 0:
            return "0%"
        else:
            return "{:.2f}%".format((float(actual) / float(target)) * 100)

    #===================================================================================================================
    # calculated methods
    #===================================================================================================================
    def get_period(self, dateobj):

        for period in self.periods:
            dtfrom, dtto = period
            if dtfrom <= dateobj <= dtto:
                return dtfrom, dtto

        # no current periods, get last period
        if len(self.periods) > 0:
            dtfrom, dtto = self.periods[-1]
            return dtfrom, dtto
        else:
            return None, None

    def get_current_period(self):
        period_from, period_to = self.periods[-1]
        return period_from, period_to

    def get_last_execution_date(self):
        return self.model.get_last_execution_date()

    def calculate_periods(self, uptodate):

        periods = []
        periodcount = 0
        dtfrom = self.starts
        dtto = None

        while dtfrom <= uptodate:
            dtfrom, dtto = self.calculate_period(dtfrom, periodcount)

            # returns none when at end of target lifespan
            if dtfrom is None or dtto is None:
                break

            # catch when there are no more periods and it continues passing the last period
            if dtfrom > dtto or (dtfrom, dtto) in periods:
                break

            periods.append((dtfrom, dtto))
            dtfrom = dtto + timedelta(days=1)
            periodcount += 1

        return periods

    def calculate_period(self, relativedate, periodcount):
        periodfrom = relativedate

        if self._ends_ is not None and relativedate > self._ends_:
            return None, None

        # break periods
        if periodcount > 0 and self.breakafter is not None and self.breakafter > 0:
            if self.breakafter % periodcount == 0:
                periodfrom, periodto = self._calculate_period(periodfrom, self.breakfreq, self.breakinterval, 0, periodcount)
                periodfrom = periodto + timedelta(days=1)

        periodfrom, periodto = self._calculate_period(periodfrom, self.freq, self.interval, self.offinterval, periodcount)

        return periodfrom, periodto

    def _calculate_period(self, relativedate, freq, interval, offinterval, periodcount):

        periodfrom = relativedate
        periodto = None

        # push off period based on offinterval
        if offinterval > 0 and periodcount > 0:
            periodfrom, periodto = self._calculate_period(periodfrom, freq, offinterval, 0, periodcount)
            periodfrom = periodto + timedelta(days=1)

        if freq < 4:
            trueinterval = interval - offinterval

        if freq == Target.YEARLY:
            if periodfrom.day != 1 or periodfrom.month != 1:
                periodfrom = Target.todate("{}-{:0>2}-{:0>2}".format(periodfrom.year, 1, 1))
            periodto = Target.todate("{}-{:0>2}-{:0>2}".format(periodfrom.year + (trueinterval - 1), 12, 31))

        elif freq == Target.MONTHLY:
            if periodfrom.day != 1:
                periodfrom = Target.todate("{}-{:0>2}-{:0>2}".format(periodfrom.year, periodfrom.month, 1))
            if periodfrom.month + trueinterval <= 12:
                periodto = Target.todate("{}-{:0>2}-{:0>2}".format(
                    periodfrom.year, periodfrom.month + trueinterval, periodfrom.day))
            else:
                periodto = Target.todate("{}-{:0>2}-{:0>2}".format(
                    periodfrom.year + 1, trueinterval - (12 - periodfrom.month), periodfrom.day))
            periodto -= timedelta(days=1)

        elif freq == Target.WEEKLY:
            if periodfrom.weekday() != 0:
                periodfrom = periodfrom - timedelta(days=periodfrom.weekday())
            periodto = periodfrom + timedelta(weeks=1*trueinterval, days=-1)

        elif freq == Target.DAILY:
            periodto = periodfrom + timedelta(days=trueinterval - 1)

        elif freq == Target.ONCE:
            periodto = self.interval

        elif freq == Target.DATES:
            periodto = self._get_next_date_interval(periodfrom)

        return periodfrom, periodto

    def _get_next_date_interval(self, relativedate):
        for dt in self.interval:
            if dt >= relativedate:
                return dt
        return None

    def _add_log_progress(self, log):

        if self.measure == 0:
            return 1
        elif self.measure == 1 and log.progress is not None:
            return log.progress
        elif self.measure == 2 and log.minutes is not None:
            return log.minutes
        else:
            return 0


#=======================================================================================================================
# other models
#=======================================================================================================================
class Duration(object):

    def __init__(self, tdelta):
        self.days = tdelta.days
        self.hours = 0
        self.minutes = 0
        self.seconds = tdelta.seconds

        if self.seconds > 59:
            self.minutes = self.seconds // 60
            self.seconds %= 60

        if self.minutes > 59:
            self.hours = self.minutes // 60
            self.minutes %= 60

        if self.hours > 23:
            self.days += self.hours // 24
            self.hours %= 24

    def __str__(self):
        string = ''
        if self.days > 0:
            string += "{}d".format(self.days)
        if self.hours > 0:
            string += "{}h".format(self.hours)
        if self.minutes > 0:
            string += "{}m".format(self.minutes)
        if self.seconds > 0:
            string += "{}s".format(self.seconds)

        if string == '':
            string = '-'

        return string

    @staticmethod
    def minutes_to_duration(minutes):

        return Duration(timedelta(minutes=minutes))
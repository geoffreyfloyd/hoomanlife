import hoomanlogic
import hoomancmd
import models as m
import controller as c


#=======================================================================================================================
# HoomanLifeCmd Class
#=======================================================================================================================
class HoomanLifeCmd(hoomancmd.HoomanCmd):

    #===================================================================================================================
    # Hooman Interface
    #===================================================================================================================
    synonyms_add = ['add', 'set', '+', 'new']
    synonyms_all = ['all', 'everything']
    synonyms_remove = ['remove', 'rm', 'rem', '-', 'delete', 'del', 'd']
    synonyms_clear = ['clear', 'clr', 'erase']
    synonyms_property = ['property', 'prop']
    synonyms_properties = ['props', 'props']
    synonyms_history = ['history', 'hist', 'log', 'logs', 'diary', 'journal']
    synonyms_action = ['action', 'task', 'todo']
    synonyms_actions = ['actions', 'a', 'todos', 'tasks']
    synonyms_actions_alone = ['actions', 'todos', 'tasks']
    synonyms_plan = ['plan', 'project', 'curriculum', 'group']
    synonyms_plans = ['plans', 'p', 'projects', 'curriculums', 'groups']
    synonyms_plans_alone = ['plans', 'projects', 'curriculums', 'groups']
    synonyms_tags = ['tags', 't', 'keywords', 'searchterms', 'searchwords', 'labels']
    synonyms_tags_alone = ['tags', 'keywords', 'searchterms', 'searchwords', 'labels']
    synonyms_list = ['list', 'lst', 'l']
    synonyms_view = ['view', 'display', 'show', 'see']
    synonyms_notes = ['docs', 'docs', 'documentation']

    def register_hli(self):
        """Register the human language interface."""

        # extend base class attribute yes and no synonym lists
        hoomancmd.HoomanCmd.synonyms_yes.extend(['uhhuh', 'fosho', 'surely', 'ja', 'sicher',
                                                 'naturlich', 'certainly', 'correct'])
        hoomancmd.HoomanCmd.synonyms_no.extend(['nope', 'nada', 'nein'])

        import hoomanlogic.translation as ev
        import translation as lclev
        from hoomanlogic import ArgumentMediator

        #===============================================================================================================
        # Direct Model Interface Commands
        #===============================================================================================================
        # select
        self.select.translator.synonyms = {'select': ['select', 'choose', 'pick', 'context']}
        self.select.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.select.translator.func_info)]

        # pushbutton
        self.pushbutton.translator.synonyms = {'pushbutton': ['pushbutton', 'dothis', 'do']}
        self.pushbutton.translator.arg_mediators = [
            ArgumentMediator('button', required=True, from_func_info=self.pushbutton.translator.func_info)]

        #===============================================================================================================
        # Listing and Viewing Commands
        #===============================================================================================================
        # actions
        self.actions.translator.synonyms = {
            'actions': hoomanlogic.build_command_words((self.synonyms_actions, self.synonyms_list),
                                                       (self.synonyms_list, self.synonyms_actions),
                                                       self.synonyms_actions_alone),
            'actions all': ['allactions'],
            'actions inactive': ['oldactions'],
            'actions future': ['futureactions']}
        self.actions.translator.arg_mediators = [
            ArgumentMediator('status',
                             rules=(ev.translate_to_dict_key, "Value must be 'active', 'inactive', 'future', 'all'",
                                    {'active': ['current', 'active'],
                                     'inactive': ['old', 'inactive'],
                                     'future': ['future', 'someday', 'maybe'],
                                     'all': ['all', 'everything']}),
                             from_func_info=self.actions.translator.func_info),
            ArgumentMediator('tags', max_count=None, from_func_info=self.actions.translator.func_info)]

        # history
        self.history.translator.synonyms = {'history': self.synonyms_history}
        self.history.translator.arg_mediators = [
            ArgumentMediator('model',
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.history.translator.func_info)]

        # list
        self.list.translator.synonyms = {'list': self.synonyms_list,
                                         'list inactive': ['listold', 'listinactive'],
                                         'list future': ['listfuture', 'listsomeday', 'listmaybe']}
        self.list.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or a plan.',
                                    self.context),
                             from_func_info=self.list.translator.func_info),
            ArgumentMediator('status',
                             rules=(ev.translate_to_dict_key, "Value must be 'active', 'inactive', or 'future'",
                                    {'active': ['current', 'active'],
                                     'inactive': ['old', 'inactive'],
                                     'future': ['future', 'someday', 'maybe']}),
                             from_func_info=self.view.translator.func_info)]

        # plans
        self.plans.translator.synonyms = {
            'plans': hoomanlogic.build_command_words((self.synonyms_plans, self.synonyms_list),
                                                     (self.synonyms_list, self.synonyms_plans),
                                                     self.synonyms_plans_alone),
            'plans inactive': ['oldplans']}
        self.plans.translator.arg_mediators = [
            ArgumentMediator('status',
                             rules=(ev.translate_to_dict_key, "Value must be 'active', 'inactive', 'future', 'all'",
                                    {'active': ['current', 'active'],
                                     'inactive': ['old', 'inactive'],
                                     'future': ['future', 'someday', 'maybe'],
                                     'all': ['all', 'everything']}),
                             from_func_info=self.plans.translator.func_info)]

        # tags
        self.tags.translator.synonyms = {
            'tags': hoomanlogic.build_command_words((self.synonyms_tags, self.synonyms_list),
                                                    (self.synonyms_list, self.synonyms_tags),
                                                    self.synonyms_tags_alone),
            'tags inactive': ['oldtags']}
        self.tags.translator.arg_mediators = [
            ArgumentMediator('status',
                             rules=(ev.translate_to_dict_key, "Value must be 'active', 'inactive', 'future', 'all'",
                                    {'active': ['current', 'active'],
                                     'inactive': ['old', 'inactive'],
                                     'future': ['future', 'someday', 'maybe'],
                                     'all': ['all', 'everything']}),
                             from_func_info=self.tags.translator.func_info)]

        # targets
        self.targets.translator.synonyms = {
            'targets': ['targets'],
            'targets inactive': ['oldtargets']}
        self.targets.translator.arg_mediators = [
            ArgumentMediator('status',
                             rules=(ev.translate_to_dict_key, "Value must be 'active', 'inactive', 'future', 'all'",
                                    {'active': ['current', 'active'],
                                     'inactive': ['old', 'inactive'],
                                     'future': ['future', 'someday', 'maybe'],
                                     'all': ['all', 'everything']}),
                             from_func_info=self.tags.translator.func_info)]

        # view
        self.view.translator.synonyms = {
            'view': self.synonyms_view,
            'view all': hoomanlogic.build_command_words((self.synonyms_view, self.synonyms_all)),
            'view props': hoomanlogic.build_command_words((self.synonyms_view, self.synonyms_properties),
                                                          self.synonyms_properties),
            'view docs': hoomanlogic.build_command_words((self.synonyms_view, self.synonyms_notes),
                                                         self.synonyms_notes)}
        self.view.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or a plan.',
                                    self.context),
                             from_func_info=self.view.translator.func_info,
                             question="Which action or plan would you like to view?"),
            ArgumentMediator('mode',
                             rules=(ev.translate_to_dict_key, "Value must be 'docs', 'all', or 'props'",
                                    {'docs': self.synonyms_notes,
                                     'all': self.synonyms_all,
                                     'props': self.synonyms_properties}),
                             from_func_info=self.view.translator.func_info)]

        #===============================================================================================================
        # Modifier Commands
        #===============================================================================================================
        # addaction
        self.addaction.translator.synonyms = {
            'addaction': hoomanlogic.build_command_words((self.synonyms_add, self.synonyms_action))}
        self.addaction.translator.arg_mediators = [
            ArgumentMediator('parent', argument_prefixer=['in', 'inside', 'into'],
                             rules=(lclev.translate_plan, 'Value must reference a plan.', self.context)),
            ArgumentMediator('status',
                             rules=(ev.translate_to_dict_key, 'Value must be a valid action status.',
                                    m.Action.status_dict.copy()),
                             from_func_info=self.addaction.translator.func_info),
            ArgumentMediator('type',
                             rules=(ev.translate_to_dict_key, 'Value must be a valid action type.',
                                    m.Action.type_dict.copy()),
                             from_func_info=self.addaction.translator.func_info),
            ArgumentMediator('name', required=True, from_func_info=self.addaction.translator.func_info),
            ArgumentMediator('tags', max_count=None, from_func_info=self.addaction.translator.func_info)]

        # adddocs
        self.adddocs.translator.synonyms = {
            'adddocs': hoomanlogic.build_command_words((self.synonyms_add, self.synonyms_notes))}
        self.adddocs.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.adddocs.translator.func_info),
            ArgumentMediator('docs', required=True, max_count=None,
                             from_func_info=self.adddocs.translator.func_info)]

        # addplan
        self.addplan.translator.synonyms = {
            'addplan': hoomanlogic.build_command_words((self.synonyms_add, self.synonyms_plan))}
        self.addplan.translator.arg_mediators = [
            ArgumentMediator('parent', argument_prefixer=['in', 'inside', 'into'],
                             rules=(lclev.translate_plan, 'Value must reference a plan.', self.context)),
            ArgumentMediator('name', required=True, from_func_info=self.addplan.translator.func_info),
            ArgumentMediator('tags', max_count=None, from_func_info=self.addplan.translator.func_info)]

        # addtarget
        from datetime import date
        self.addtarget.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.addtarget.translator.func_info),
            ArgumentMediator('freq', required=True,
                             rules=(ev.translate_to_dict_key, 'Value must be a valid frequency.',
                                    m.Target.freq_dict.copy()),
                             from_func_info=self.addtarget.translator.func_info),
            ArgumentMediator('measure', required=True,
                             rules=(ev.translate_to_dict_key, 'Value must be a valid measurement.',
                                    m.Target.measure_dict.copy()),
                             from_func_info=self.addtarget.translator.func_info),
            ArgumentMediator('target', required=True,
                             rules=(ev.translate_to_first_type, 'Value must be an integer.', [int]),
                             from_func_info=self.addtarget.translator.func_info),
            ArgumentMediator('starts', required=True,
                             rules=(ev.translate_date, 'Value must be a date.', None),
                             from_func_info=self.addtarget.translator.func_info),
            ArgumentMediator('interval', argument_prefixer=['every', 'interval'],
                             rules=(ev.translate_to_first_type, 'Value must be an integer.', [int]),
                             from_func_info=self.addtarget.translator.func_info),
            ArgumentMediator('duedate', argument_prefixer=['due'],
                             rules=(ev.translate_date, 'Value must be a date.', None),
                             from_func_info=self.addtarget.translator.func_info),
            ArgumentMediator('listdates', argument_prefixer=['for'],
                             rules=(ev.translate_list_to_first_type, 'Value must be a list of dates.', [date]),
                             from_func_info=self.addtarget.translator.func_info)]

        # clearhistory
        self.clearhistory.translator.synonyms = {
            'clearhistory': hoomanlogic.build_command_words((self.synonyms_clear, self.synonyms_history))}
        self.clearhistory.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.clearhistory.translator.func_info)]

        # clearnotes
        self.clearnotes.translator.synonyms = {
            'clearnotes': ['clearnotes']}
        self.clearnotes.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.clearnotes.translator.func_info)]

        # delete
        self.delete.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_plan_target_or_tag,
                                    'Value must reference an action, plan, target, or tag.',
                                    self.context),
                             from_func_info=self.rmprop.translator.func_info)]
        # log
        self.log.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.log.translator.func_info),
            ArgumentMediator('progress',
                             rules=((ev.translate_to_first_type, 'Value must be an integer.', [int]),
                                    (ev.validate_int_is_in_range, 'Value must be between 0 and 100.', (0, 100))),
                             from_func_info=self.log.translator.func_info),
            ArgumentMediator('minutes', rules=(ev.translate_duration_to_minutes,
                                               'Value must be a duration of time.', None),
                             from_func_info=self.log.translator.func_info)]

        # mark
        self.mark.translator.synonyms = {'mark': ['mark', 'setstatus', 'set']}
        self.mark.translator.arg_mediators = [
            ArgumentMediator('status', required=True,
                             rules=(ev.translate_to_dict_key, 'Value must be a valid status.',
                                    m.Action.status_dict.copy()),
                             from_func_info=self.mark.translator.func_info),
            ArgumentMediator('action', required=True,
                             rules=(lclev.translate_action, 'Value must reference an action.', self.context),
                             from_func_info=self.mark.translator.func_info)]

        # move
        self.move.translator.arg_mediators = [
            ArgumentMediator('action', required=True,
                             rules=(lclev.translate_action, 'Value must reference an action.', self.context),
                             from_func_info=self.move.translator.func_info),
            ArgumentMediator('direction',
                             rules=(ev.translate_to_dict_key, 'Value must be a valid direction.',
                                    {"up": ["up", "u"], "down": ["down", "d"]}),
                             from_func_info=self.move.translator.func_info)]

        # put
        self.put.translator.arg_mediators = [
            ArgumentMediator('into', argument_prefixer='into',
                             rules=(lclev.translate_plan, 'Value must reference a plan.',
                                    self.context),
                             from_func_info=self.put.translator.func_info),
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or a plan.',
                                    self.context),
                             from_func_info=self.put.translator.func_info)]

        # rename
        self.rename.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_plan_or_tag,
                                    'Value must reference an action, plan, or tag.',
                                    self.context),
                             from_func_info=self.rmprop.translator.func_info),
            ArgumentMediator('name', required=True, from_func_info=self.rename.translator.func_info)]

        # rmprop
        self.rmprop.translator.synonyms = {
            'rmprop': hoomanlogic.build_command_words((self.synonyms_remove, self.synonyms_property))}
        self.rmprop.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.rmprop.translator.func_info),
            ArgumentMediator('property_name', required=True, from_func_info=self.rmprop.translator.func_info)]

        # setprop
        self.setprop.translator.synonyms = {
            'setprop': hoomanlogic.build_command_words((self.synonyms_add, self.synonyms_property))}
        self.setprop.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.setprop.translator.func_info),
            ArgumentMediator('property_name', required=True,
                             from_func_info=self.setprop.translator.func_info),
            ArgumentMediator('value', required=True, from_func_info=self.setprop.translator.func_info)]

        # tag
        self.tag.translator.synonyms = {'tag': ['tag']}
        self.tag.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.tag.translator.func_info),
            ArgumentMediator('tags', required=True, max_count=None, from_func_info=self.tag.translator.func_info)]

        # untag
        self.untag.translator.synonyms = {'untag': ['untag']}
        self.untag.translator.arg_mediators = [
            ArgumentMediator('model', required=True,
                             rules=(lclev.translate_action_or_plan, 'Value must reference an action or plan.',
                                    self.context),
                             from_func_info=self.untag.translator.func_info),
            ArgumentMediator('tags', required=True, max_count=None,
                             from_func_info=self.untag.translator.func_info)]

        #===============================================================================================================
        # Environment Commands
        #===============================================================================================================
        # setlogfile
        self.setlogfile.translator.synonyms = {
            'setlogfile': hoomanlogic.build_command_words((['set'], ['log'], ['file']))}
        self.setlogfile.translator.arg_mediators = [
            ArgumentMediator('logfilename', required=True,
                             from_func_info=self.setlogfile.translator.func_info)]

    class Context(object):
        def __init__(self):
            self.controller = None
            self.index_mode = None
            self.index = None
            self.selected_interface = None

    #===================================================================================================================
    # object Overrides
    #===================================================================================================================
    def __init__(self, completekey='tab', stdin=None, stdout=None, prompt='>> ', enable_match_suggestion=True):

        # base class initialization
        hoomancmd.HoomanCmd.__init__(self, completekey, stdin, stdout, prompt, enable_match_suggestion)

        # controller and data-layer injection
        self.controller = c.HoomanLifeController('/home/owner/life', self.stdout)

        # set context object
        self.context = HoomanLifeCmd.Context()
        self.context.controller = self.controller

    def __str__(self):
        return "Command-line interface"

    #===================================================================================================================
    # Cmd Overrides
    #===================================================================================================================
    def postloop(self):
        self.print_line("Goodbye!")

    #===================================================================================================================
    # Menu Displays and Indexing
    #===================================================================================================================
    def display_action_list(self, list_, subtitle='', mode='action', status='active'):

        if len(list_) == 0:
            self.print_line('No actions to list.')
            return

        i = 0  # index counter
        action_index = {}

        if status == 'active':
            table = [['{=|fill}'], ['={Active Actions' + subtitle + '|center}='], ['{=|fill}']]
        elif status == 'inactive':
            table = [['{=|fill}'], ['={Inactive Actions' + subtitle + '|center}='], ['{=|fill}']]
        elif status == 'future':
            table = [['{=|fill}'], ['={Future Actions' + subtitle + '|center}='], ['{=|fill}']]
        elif status == 'all':
            table = [['{=|fill}'], ['={All Actions' + subtitle + '|center}='], ['{=|fill}']]
        else:
            raise Exception("Unrecognized status.")

        if mode == 'action':  # indicative of listing a plan

            partial = list_.filter(progress__gt=0, type='todo').sort('name')
            todo = list_.filter(progress=0, type='todo').sort('name')
            routine = list_.filter(type='routine').sort('name')
            next_in_queue = list_.filter(type='queue', order=1)
            option_plans = list_.filter(type='option', actions__count__gt=0)

            if len(partial) > 0:
                table.append(['#', '##', 'In Progress Action', 'Plan'])
                table.append(['{-|fill}'])
                for a in partial:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_plan_name()])
                table.append(['{-|fill}'])

            if len(todo) > 0:
                table.append(['#', '##', 'To Do Action', 'Plan'])
                table.append(['{-|fill}'])
                for a in todo:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_plan_name()])
                table.append(['{-|fill}'])

            if len(routine) > 0:
                table.append(['#', '##', 'Routine Action', 'Plan'])
                table.append(['{-|fill}'])
                for a in routine:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_plan_name()])
                table.append(['{-|fill}'])

            if len(option_plans) > 0:
                table.append(['#', '##', 'Option Plans', 'Plan'])
                table.append(['{-|fill}'])
                for a in option_plans:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.name, ''])
                table.append(['{-|fill}'])

            if len(next_in_queue) > 0:
                table.append(['#', '##', 'Next In Queue Action', 'Plan'])
                table.append(['{-|fill}'])
                for a in next_in_queue:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_plan_name()])
                table.append(['{-|fill}'])

        elif mode == 'plan':

            partial = list_.filter(progress__gt=0, type='todo').sort('name')
            todo = list_.filter(progress=0, type='todo').sort('name')
            routine = list_.filter(type='routine').sort('name')
            option = list_.filter(type='option', status='active').sort('name').sort('order')
            queued = list_.filter(type='queue', status='active').sort('name').sort('order')

            if len(partial) > 0:
                table.append(['#', '##', 'In Progress Action', 'Last Executed'])
                table.append(['{-|fill}'])
                for a in partial:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc()])
                table.append(['{-|fill}'])

            if len(todo) > 0:
                table.append(['#', '##', 'To Do Action', 'Last Executed'])
                table.append(['{-|fill}'])
                for a in todo:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_last_execution_date()])
                table.append(['{-|fill}'])

            if len(routine) > 0:
                table.append(['#', '##', 'Routine Action', 'Last Executed'])
                table.append(['{-|fill}'])
                for a in routine:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_last_execution_date()])
                table.append(['{-|fill}'])

            if len(option) > 0:
                table.append(['#', '##', 'Option Action', 'Last Executed'])
                table.append(['{-|fill}'])
                for a in option:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_last_execution_date()])
                table.append(['{-|fill}'])

            if len(queued) > 0:
                table.append(['#', '##', 'Queued Action', 'Last Executed'])
                table.append(['{-|fill}'])
                for a in queued:
                    i += 1
                    action_index[str(i)] = a
                    table.append([i, a.get_attributes(), a.get_desc(), a.get_last_execution_date()])
                table.append(['{-|fill}'])

        table.append([''])

        self.context.index_mode = 'actions'
        self.context.index = action_index

        self.print_table(table, col_justify=[1])

    def display_plan_list(self, list_):

        if len(list_) == 0:
            self.print_line('No plans to list.')
            return

        i = 0
        plan_index = {}

        table = []
        table.append(['{=|fill}'])
        table.append(['={Plans|center}='])
        table.append(['{=|fill}'])
        table.append(['#', '##', 'Plan'])
        table.append(['{-|fill}'])
        for p in list_:
            i += 1
            plan_index[str(i)] = p
            table.append([i, p.get_attributes(), p])
        table.append([''])

        self.context.index_mode = 'plans'
        self.context.index = plan_index

        # print the table
        self.print_table(table, col_justify=[1])

    def display_tag_list(self, list_):

        if len(list_) == 0:
            self.print_line('No tags to list.')
            return

        # beginning of table listing
        table = []
        table.append(['{=|fill}'])
        table.append(['={Tags|center}='])
        table.append(['{=|fill}'])
        table.append(['#', 'Tag'])
        table.append(['{-|fill}'])

        # build tag index and table listing
        i = 0
        tag_index = {}

        for t in list_:
            i += 1
            tag_index[str(i)] = t
            table.append([str(i), str(t)])
        table.append([''])

        self.context.index_mode = 'tags'
        self.context.index = tag_index

        # print the table
        self.print_table(table, col_justify=[1])

    def display_target_list(self, list_):

        if len(list_) == 0:
            self.print_line('No targets to list.')
            return

        # beginning of table listing
        table = []
        table.append(['{=|fill}'])
        table.append(['={Targets|center}='])
        table.append(['{=|fill}'])
        table.append(['#', 'Action or Plan', 'Progress', 'Days', 'Period', 'Current', 'Average'])
        table.append(['{-|fill}'])

        # build tag index and table listing
        i = 0
        target_index = {}

        for t in list_:
            i += 1
            target_index[str(i)] = t
            table.append([str(i), str(t.model), t.progress, t.daysleft, t.period_desc, t.thisperiod, t.average])
        table.append([''])

        self.context.index_mode = 'targets'
        self.context.index = target_index

        # print the table
        self.print_table(table, col_justify=[1])

    #===================================================================================================================
    # Direct Model Interface Commands
    #===================================================================================================================
    @hoomanlogic.translator(code_alert=2)
    def select(self, model):
        """Select an item from the last list presented as the context.

        :param model: Action or Plan to select for interfacing.
        :type model: models.Action, models.Plan
        """
        self.context.selected_interface = model
        if self.context is not None:
            self.tell_operator("Selected '{}'".format(str(self.context.selected_interface)))

    @hoomanlogic.translator(code_alert=2)
    def pushbutton(self, button):
        """Run a function of the currently selected context (Action or Plan).

        :param button: Name of the function.
        :type button: str
        """
        if self.context.selected_interface is None:
            self.context.selected_interface = self

        try:
            func = getattr(self.context, button)
        except AttributeError:
            self.tell_operator("'{}' is not a button for '{}'.".format(button,
                                                                       str(self.context.selected_interface)))
            return

        if func is not None:
            try:
                func()
            except TypeError:
                self.tell_operator("'{}' is not a button for '{}'.".format(button,
                                                                           str(self.context.selected_interface)))
            except Exception:
                self.tell_operator("Sorry, the '{}' button for '{}' is malfunctioning.".format(
                    button, str(self.context.selected_interface)))

    #===================================================================================================================
    # Listing and Viewing Commands
    #===================================================================================================================
    @hoomanlogic.translator()
    def actions(self, status='active', tags=None):
        """List active actions, optionally filtering by a list of tags to include.

        :param tags: A list of tags to filter the active actions to.
        :type tags: list<str>
        """
        list_ = self.controller.get_actions(status=status, tags=tags)
        self.display_action_list(list_, mode='action', status=status)

    @hoomanlogic.translator()
    def history(self, model=None):
        """List log history.

        If index is not supplied, the entire contents of the current log file will be listed.

        :param index: The action, plan, or tag to list history for.
        :type index: models.Action|models.Plan|str
        """

        # check if Index was supplied
        table = []
        if model is not None:
            if isinstance(model, m.Action):
                justify = [-1, 1, 1]
                header = "={History for '" + model.name + "'|center}="
                subheader = ["Date", "Progress", "Minutes"]
                for logentry in model.history.sort('logdate').flip():
                    table.append([logentry.logdate, logentry.progress, logentry.minutes])

            elif isinstance(model, m.Plan):
                justify = [-1, 1, 1]
                header = "={History for '" + model.name + "'|center}="
                subheader = ["Date", "Action", "Progress", "Minutes"]
                for logentry in model.history.sort('logdate').flip():
                    if isinstance(logentry.obj, str) or isinstance(logentry.obj, unicode):
                        name = logentry.obj
                    else:
                        name = logentry.obj.name
                    table.append([logentry.logdate, name, logentry.progress, logentry.minutes])

            else:  # tags
                justify = [-1, -1, 1, 1]
                header = "={History for actions tagged #" + model + "|center}="
                subheader = ["Date", "Action", "Progress", "Minutes"]
                for logentry in self.controller.get_log_entries().sort('logdate').flip():
                    if isinstance(logentry.obj, m.Action) or isinstance(logentry.obj, m.Plan) and model in logentry.obj.tags:
                        table.append([logentry.logdate, logentry.obj.name, logentry.progress, logentry.minutes])

        else:  # for no model given, just return all of the history
            justify = [-1, -1, 1, 1]
            header = "={History|center}="
            subheader = ["Date", "Action", "Progress", "Minutes"]
            for logentry in self.controller.get_log_entries().sort('logdate').flip():
                if isinstance(logentry.obj, m.Action):
                    objname = logentry.obj.name
                else:
                    objname = logentry.obj
                table.append([logentry.logdate, objname, logentry.progress, logentry.minutes])

        table.reverse()
        table.append(["{-|fill}"])
        table.append(subheader)
        table.append(["{=|fill}"])
        table.append([header])
        table.append(["{=|fill}"])
        table.reverse()
        self.print_table(table, col_justify=justify)

    @hoomanlogic.translator()
    def list(self, model, status='active'):
        """List actions assigned to the plan or tag.

        :param model: Plan or tag to list actions of.
        :type model: models.Plan|str
        """
        if self.context.index_mode == 'plans':
            self.display_action_list(model.actions.filter(status=status), subtitle=' For \'' + str(model) + '\'',
                                     mode='plan', status=status)
        elif self.context.index_mode == 'tags':
            list_ = self.controller.get_actions_assigned_to_tags([model], status=status)
            self.display_action_list(list_, subtitle=' For #' + str(model), status=status)

    @hoomanlogic.translator()
    def plans(self, status='active'):
        """List plans."""
        self.display_plan_list(self.controller.get_plans(status=status))

    @hoomanlogic.translator()
    def tags(self, status='active'):
        """List tags."""
        self.display_tag_list(self.controller.get_tags(status=status))

    @hoomanlogic.translator()
    def targets(self, status='active'):
        """List targets."""
        list_ = self.controller.get_targets(status=status)
        self.display_target_list(list_)

    @hoomanlogic.translator()
    def view(self, model, mode='docs'):
        """View the details of an action or a plan.

        :param model: An Action or Plan instance.
        :type model: _hoomanlife.models.Action, _hoomanlife.models.Plan
        :param mode: The view mode: 'all' for props and docs, 'props' for props, and 'docs' for docs.
        :type mode: str
        :rules mode: in ['all', 'props', 'docs']
        """
        self.tell_operator(self.controller.get_model_info(model, mode), no_formatting=True)

    #===================================================================================================================
    # Modifier Commands
    #===================================================================================================================
    @hoomanlogic.translator(code_alert=1)
    def addaction(self, name, parent=None, status=None, type=None, tags=None):
        """Create a new action.

        :param parent: The index-reference number for a plan to assign the action to.
        :type parent: models.Plan
        :param status: The status to mark the action.
        :type status: str
        :param tags: The tags to assign to the new action.
        :type tags: list<str>
        """
        # create the action
        a = m.Action.create(name=name, type=type, status=status, parent=parent, tags=tags)
        try:
            a.save()
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=1)
    def adddocs(self, model, docs):
        model.add_docs(docs)
        model.save()

    @hoomanlogic.translator(code_alert=1)
    def addtarget(self, model, freq, measure, target, starts, interval=None, duedate=None, listdates=None):
        """Create a new target.

        :param model: The action or plan to add a target for.
        :type model: models.Action|models.Plan
        :param freq: The parent plan to assign the plan to.
        :type freq: datetime.datetime|datetime.date|int
        :param starts: The date the target starts.
        :type starts: datetime.datetime
        :param measure: The type of measurement (o-BY_EXECUTIONS, 1-BY_PROGRESS, 2-BY_TIME).
        :type measure: int
        :param period_target: The target to reach per period.
        :type period_target: int
        :param interval: The frequency interval.
        :type interval: int
        """
        if freq == 4:
            interval = duedate
        elif freq == 5:
            interval = listdates

        model.add_target(freq, starts, measure, period_target=target, interval=interval)
        model.save()

    @hoomanlogic.translator(code_alert=1)
    def addplan(self, name, parent=None, tags=None):
        """Create a new plan.

        :param name: The name of the new plan.
        :type name: str
        :param parent: The parent plan to assign the plan to.
        :type parent: models.Plan
        :param tags: The tags to assign to the new plan.
        :type tags: list<str>
        """
        # create the plan
        p = m.Plan.create(name=name, status='active', parent=parent, tags=tags)
        try:
            p.save()
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=2)
    def clearhistory(self, model):
        """Clear an action or plan's log history.

        :param model: The action or plan to clear the history of.
        :type model: models.Action|models.Plan
        """
        model.clear_history()

    @hoomanlogic.translator(code_alert=2)
    def clearnotes(self, model):
        """Clear an action's notes.

        :param model: The action or plan to clear the history of.
        :type model: models.Action|models.Plan
        """
        model.clear_docs()

    @hoomanlogic.translator(code_alert=2)
    def delete(self, model, erase_history=True):
        """Delete an action, plan, target, or tag.

        :param model: An action, plan, or tag.
        :type model: models.Action, models.Plan, str
        :param erase_history: Decides whether historical logs for the action should be erased.
        :type erase_history: bool
        """

        if isinstance(model, m.Action):
            self.controller.delete_action(model, erase_history=erase_history)
        elif isinstance(model, m.Plan):
            self.controller.delete_plan(model, erase_history=erase_history)
        elif isinstance(model, m.Target):
            self.controller.delete_target(model)
        else:
            self.controller.delete_tag(model)

    @hoomanlogic.translator()
    def log(self, model, progress=None, minutes=None):
        """Log execution of an action or plan.

        :param model: Action or plan to log.
        :type model: models.Action|models.Plan
        :param progress: The approximate completed percent of the action (0 to 100).
        :type progress: int
        :rules progress: validate_int_is_in_range::0-100
        :param minutes: The minutes spent on the action to be added to the action's actual minutes property.
        :type minutes: int
        :rules minutes: translate_duration_to_minutes
        """
        if isinstance(model, m.Plan):
            list_ = model.actions
            self.display_action_list(list_, subtitle=" - Log Actions", mode='plan')
            line = raw_input("Would you like to log any of these actions in place of logging the plan?\n>> ")
            if line is not None and line not in ['', 'n', 'no']:
                for arg in line.split():
                    parts = arg.split(':')
                    submodel = self.context.index[parts[0]]
                    progress = None
                    minutes = None
                    if len(parts) > 1 and parts[1] != '':
                        progress = int(parts[1])
                    if len(parts) > 2 and parts[2] != '':
                        minutes = int(parts[2])
                    submodel.log(progress, minutes)
                    submodel.save()
            else:
                model.log(progress, minutes)
        else:
            model.log(progress, minutes)
        try:
            model.save()
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=1)
    def mark(self, action, status):
        """Log execution of an action.

        :param action: Action instance.
        :type action: models.Action
        :param status: The status to set the action to ('active', 'inactive', 'future').
        :type status: str
        """
        action.status = status
        try:
            action.save()
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator()
    def move(self, action, direction):
        """Move an action up or down in the queue list.

        :param action: The action to move.
        :type action: models.Action
        :param direction: The direction to move the action within the queue list ('up', 'down').
        :type direction: str
        """
        if action.parent is None:
            return

        if direction == 'up':
            action.parent.move_up_in_queue(action)
        else:
            action.parent.move_down_in_queue(action)
        try:
            self.controller.save_all()
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=1)
    def put(self, model, into=None):
        """Put an action or plan into a plan or take it out.

        :param model: The action or plan to move into or out of a plan.
        :type model: models.Action|models.Plan|str
        :param into: The plan to move the action or plan into, or None to put it in the root.
        :type into: models.Plan
        """
        if model.parent is not None:
            model.parent.remove(model)

        if into is not None:
            if isinstance(model, m.Action):
                into.actions.append(model)
            elif isinstance(model, m.Plan):
                into.plans.append(model)

        try:
            model.save()
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=1)
    def rename(self, model, name):
        """Rename an action, plan, or tag.

        :param model: The action, plan, or tag to be renamed.
        :type model: models.Action, models.Plan, str
        :param name: The new name to assign to the action, plan, or tag.
        :type name: str
        """
        if isinstance(model, m.Action) or isinstance(model, m.Plan):
            model.name = name
            try:
                model.save()
            except Exception, e:
                self.tell_operator(e.message)
        else:
            self.controller.rename_tag(model, name)

    @hoomanlogic.translator(code_alert=1)
    def rmprop(self, model, property_name):
        """Remove a property of an action or plan.

        :param model: The action or plan to remove an attribute of.
        :type model: models.Action|models.Plan
        :param property_name: The property to remove.
        :type property_name: str
        """
        try:
            model.remove_attribute(property_name)
            model.save()
            self.tell_operator(self.controller.get_model_info(model, 'props'))
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=1)
    def setprop(self, model, property_name, value):
        """Set a value for a property of an action or plan.

        :param model: The action or plan to remove an attribute of.
        :type model: models.Action|models.Plan
        :param property_name: The property to set a value for.
        :type property_name: str
        :param value: The value to set the property to.
        :type value: str|int
        """
        try:
            model.set_attribute(property_name, value)
            self.tell_operator(self.controller.get_model_info(model, 'props'))
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=1)
    def tag(self, model, tags):
        """Tag an action or plan.

        :param model: The action or plan to tag.
        :type model: models.Action|models.Plan
        :param tags: The tags to add.
        :type tags: str|list<str>
        """
        try:
            model.tags.extend(tags)
            model.save()
        except Exception, e:
            self.tell_operator(e.message)

    @hoomanlogic.translator(code_alert=1)
    def untag(self, model, tags):
        """Untag an action or plan.

        :param model: The action or plan to untag.
        :type model: models.Action|models.Plan
        :param tags: The tags to remove.
        :type tags: str|list<str>
        """
        try:
            model.tags.contract(tags)
            model.save()
        except Exception, e:
            self.tell_operator(e.message)

    #===================================================================================================================
    # Environment Commands
    #===================================================================================================================
    @hoomanlogic.translator()
    def setlogfile(self, logfilename):
        self.controller.set_log_filename(logfilename)
        self.tell_operator("Now logging to {}...".format(logfilename))


#=======================================================================================================================
# Main
#=======================================================================================================================
def main():
    cmdShell = HoomanLifeCmd()
    operator = hoomanlogic.Operator(message_user_func=cmdShell.print_line)
    operator.register_interface(cmdShell)

    import sys
    if len(sys.argv) > 1:
        # run a single command
        for i in range(2, len(sys.argv)):
            sys.argv[i] = '"{}"'.format(sys.argv[i])
        cmdShell.onecmd(' '.join(sys.argv[1:]))
    else:
        # autoset to testlog for now and send to devnull
        # import os
        # with open(os.devnull, 'w') as f:
        #     cmdShell.stdout = f
        #     cmdShell.setlogfile('testlog')
        #     cmdShell.stdout = sys.stdout

        # start command loop
        cmdShell.cmdloop('Welcome to HoomanLife!\n'
                         'Currently logging to {}...'.format(cmdShell.controller.get_log_filename()))

if __name__ == '__main__':
    main()
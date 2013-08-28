from hoomanpy import qlist
from data import DataAccess as dal  # data access layer


class HoomanLifeController(object):

    def __init__(self, life_path, stdout):
        dal.setup(life_path='/home/owner/life', stdout=stdout)

    def delete_action(self, action, erase_history=True):
        dal.actions.delete(action, erase_history=erase_history)

    def delete_plan(self, plan, erase_history=True):
        dal.plans.delete(plan, erase_history=erase_history)

    def delete_tag(self, tag):
        for action in dal.actions.all():
            for t in action.tags:
                if t == tag:
                    action.untag(tag)
                    action.save()

        for plan in dal.plans.all():
            for t in plan.tags:
                if t == tag:
                    plan.untag(tag)
                    plan.save()

    def delete_target(self, target):
        dal.targets.delete(target)

    def get_actions(self, status='all', plan=None, tags=None):
        """Return a list of actions.

        :param status: Status to include (active, inactive, future, or all).
        :type status: str
        :param plan: Plan to filter actions to.
        :type plan: models.Plan
        :param tags: Tags to filter the list of actions by.
        :type tags: str, list<str>
        :returns: A list of actions.
        :rtype: hoomanpy.qlist
        """

        if plan is not None:
            list_ = plan.actions
        else:
            list_ = qlist()
            list_.extend(dal.actions.all())
            list_.extend(dal.plans.filter(type='option', actions__count__gt=0))

        if status in ('active', 'inactive', 'future'):
            list_ = list_.filter(status=status)

        if tags is not None:
            if not hasattr(tags, '__iter__'):
                tags = [tags]
            list_ = list_.filter(tags__in=tags)

        return list_

    def get_log_entries(self):
        return dal.logentries.all()

    def get_log_filename(self):
        return dal.log_file_name

    def get_model_info(self, model, mode='docs'):
        """View the details of an action or a plan.

        :param model: An Action or Plan instance.
        :type model: _hoomanlife.models.Action, _hoomanlife.models.Plan
        :param mode: The view mode: 'all' for properties and docs, 'props' for properties, and 'docs' for docs.
        :type mode: str
        :rules mode: in ['all', 'props', 'docs']
        """

        if mode == 'props':
            return dal._properties_to_json(model)
        elif mode == 'docs':
            return '\n'.join(model.docs)
        else:
            output = dal._properties_to_json(model)
            output += '\n' + '\n'.join(model.docs)
            return output

    def get_plans(self, status='all'):
        if status == 'active':
            return dal.plans.active()
        elif status == 'inactive':
            return dal.plans.inactive()
        else:
            return dal.plans.all()

    def get_tags(self, status='all'):
        """Return a distinct, alphetically-sorted list of tags assigned.

        :param status: 'all', 'active', 'inactive', or 'notinuse' to Return tags assigned to actions and plans that
                       have the given status. 'old' will return tags that are assigned only to inactive actions
                       and plans.
        :type status: str
        :return: A distinct list of tags.
        :rtype: hoomanpy.qlist
        """

        if status == 'all':
            tags = dal.actions.all().distinct('tags')
            tags.extend(dal.plans.all().distinct('tags'))
        elif status == 'active':
            tags = dal.actions.active().distinct('tags')
            tags.extend(dal.plans.active().distinct('tags'))
        elif status == 'inactive':
            old = self.get_tags('inactive')
            new = self.get_tags('active')
            a = set(old)
            b = set(new)
            c = a - b
            tags = qlist()
            tags.extend(c)
        else:
            raise AttributeError("{} is not a supported status argument. Must be 'all', 'active', or 'inactive'")

        return tags.sort().distinct()

    def get_targets(self, status='all'):
        """Return a distinct, alphetically-sorted list of targets assigned.

        :param status: 'all', 'active', 'inactive', or 'notinuse' to Return tags assigned to actions and plans that
                       have the given status. 'old' will return tags that are assigned only to inactive actions
                       and plans.
        :type status: str
        :return: A distinct list of tags.
        :rtype: hoomanpy.qlist
        """

        if status == 'all':
            targets = dal.targets.all()
        elif status == 'active':
            targets = dal.targets.active()
        elif status == 'inactive':
            targets = dal.targets.inactive()
        else:
            raise AttributeError("{} is not a supported status argument. Must be 'all', 'active', or 'inactive'")

        return targets.sort()

    def rename_tag(self, tag, newname):

            for action in self.controller.get_actions():
                for t in action.tags:
                    if t == tag:
                        action.untag(tag)
                        action.tag(newname)
                        action.save()

            for plan in self.controller.get_plans():
                for t in plan.tags:
                    if t == tag:
                        plan.untag(tag)
                        plan.tag(newname)
                        plan.save()

    def save_all(self):
        dal.save()

    def set_log_filename(self, logfilename):
        dal.log_file_name = logfilename
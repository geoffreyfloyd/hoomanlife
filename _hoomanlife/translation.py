import hoomancmd
import data as dl
from hoomanpy import qlist


def translate_index_to_model(hooman_input, context=None):
    # index format
    try:
        int(hooman_input)
    except ValueError:
        return False, None

    try:
        model = context.index[hooman_input]
    except KeyError:
        return False, None

    return True, model


def translate_id_to_action(hooman_input, context=None):
    if '/' in hooman_input:
        model = context.controller.get_actions().get(id=hooman_input)

        if model is not None:
            return True, model

    return False, None


def translate_id_to_plan(hooman_input, context=None):
    if '/' in hooman_input:
        model = context.controller.get_plans().get(id=hooman_input)

        if model is not None:
            return True, model

    return False, None


def translate_action_or_plan(hooman_input, context=None):
    """Translate string to a model reference.

    :param hooman_input: String input
    :type hooman_input: str
    """
    # index translation
    if context.index_mode in ['actions', 'plans']:
        translated, model = translate_index_to_model(hooman_input, context)
        if translated:
            return True, model

    # model id translation
    translated, model = translate_id_to_action(hooman_input, context)
    if translated:
        return True, model

    translated, model = translate_id_to_plan(hooman_input, context)
    if translated:
        return True, model

    # model name translation
    # build list of matches
    matches = qlist()
    action_matches = context.controller.get_actions().filter(name__contains=hooman_input)
    plan_matches = context.controller.get_plans().filter(name__contains=hooman_input)
    if action_matches is not None:
        matches.extend(action_matches)
    if plan_matches is not None:
        matches.extend(plan_matches)
    if len(matches) == 1:
        return True, matches[0]
    # todo: implement Match Certainty to notify user we aren't sure this is what they wanted
    elif len(matches) > 1:
        closest_match = None
        len_diff = 1000
        for item in matches:
            if len_diff > len(item.name) - len(hooman_input):
                len_diff = len(item.name) - len(hooman_input)
                closest_match = item

        if len_diff < 2:
            return True, closest_match

    return False, None


def translate_action_plan_target_or_tag(hooman_input, context=None):
    """Translate string to a model reference.

    :param hooman_input: String input
    :type hooman_input: str
    """
    # index translation
    if context.index_mode in ['actions', 'plans', 'targets', 'tags']:
        translated, model = translate_index_to_model(hooman_input, context)
        if translated:
            return True, model

    # model id translation
    translated, model = translate_id_to_action(hooman_input, context)
    if translated:
        return True, model

    translated, model = translate_id_to_plan(hooman_input, context)
    if translated:
        return True, model

    # tag name translation
    if hooman_input.startswith('#'):  # tag format
        tags = context.controller.get_tags().filter(name__contains=hooman_input)
        if len(tags) == 1:
            return True, tags[0]

    # model name translation
    # build list of matches
    matches = qlist()
    action_matches = context.controller.get_actions().filter(name__contains=hooman_input)
    plan_matches = context.controller.get_plans().filter(name__contains=hooman_input)
    if action_matches is not None:
        matches.extend(action_matches)
    if plan_matches is not None:
        matches.extend(plan_matches)
    if len(matches) == 1:
        return True, matches[0]

    return False, None


def translate_action_plan_or_tag(hooman_input, context=None):
    """Translate string to a model reference.

    :param hooman_input: String input
    :type hooman_input: str
    """
    # index translation
    if context.index_mode in ['actions', 'plans', 'tags']:
        translated, model = translate_index_to_model(hooman_input, context)
        if translated:
            return True, model

    # model id translation
    translated, model = translate_id_to_action(hooman_input, context)
    if translated:
        return True, model

    translated, model = translate_id_to_plan(hooman_input, context)
    if translated:
        return True, model

    # tag name translation
    if hooman_input.startswith('#'):  # tag format
        tags = context.controller.get_tags().filter(name__contains=hooman_input)
        if len(tags) == 1:
            return True, tags[0]

    # model name translation
    # build list of matches
    matches = qlist()
    action_matches = context.controller.get_actions().filter(name__contains=hooman_input)
    plan_matches = context.controller.get_plans().filter(name__contains=hooman_input)
    if action_matches is not None:
        matches.extend(action_matches)
    if plan_matches is not None:
        matches.extend(plan_matches)
    if len(matches) == 1:
        return True, matches[0]

    return False, None


def translate_plan_or_tag(hooman_input, context=None):
    """Translate string to a model reference.

    :param hooman_input: String input
    :type hooman_input: str
    """
    # index translation
    if context.index_mode in ['plans', 'tags']:
        translated, model = translate_index_to_model(hooman_input, context)
        if translated:
            return True, model

    # model id translation
    translated, model = translate_id_to_plan(hooman_input, context)
    if translated:
        return True, model

    # tag name translation
    if hooman_input.startswith('#'):  # tag format
        tags = context.controller.get_tags().filter(name__contains=hooman_input)
        if len(tags) == 1:
            return True, tags[0]

    # plan name translation
    # build list of matches
    plan_matches = context.controller.get_plans().filter(name__contains=hooman_input)
    if len(plan_matches) == 1:
        return True, plan_matches[0]

    return False, None


def translate_action(hooman_input, context=None):
    """Translate string to a model reference.

    :param hooman_input: String input
    :type hooman_input: str
    """
    # index translation
    if context.index_mode == 'actions':
        translated, model = translate_index_to_model(hooman_input, context)
        if translated:
            return True, model

    # model id translation
    translated, model = translate_id_to_action(hooman_input, context)
    if translated:
        return True, model

    # name format
    # build list of matches
    action_matches = context.controller.get_actions().filter(name__contains=hooman_input)
    if len(action_matches) == 1:
        return True, action_matches[0]

    return False, None


def translate_plan(hooman_input, context=None):
    """Translate string to a model reference.

    :param hooman_input: String input
    :type hooman_input: str
    """
    # index translation
    if context.index_mode == 'plans':
        translated, model = translate_index_to_model(hooman_input, context)
        if translated:
            return True, model

    # model id translation
    translated, model = translate_id_to_plan(hooman_input, context)
    if translated:
        return True, model

    # name format
    # build list of matches
    plan_matches = context.controller.get_plans().filter(name__contains=hooman_input)
    if len(plan_matches) == 1:
        return True, plan_matches[0]

    return False, None
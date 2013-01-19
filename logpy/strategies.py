from logpy.util import interleave
from logpy.core import goaleval, EarlyGoalError, fail


def bindearly(stream, *goals):
    """ Bind* that intelligently handles EarlyGoalErrors """
    return bindstarstrat(stream, goals, [earlysafe], interleave)

def bindstarstrat(stream, goals, strats, joiner=interleave):
    """ Strategic bind* """
    return joiner(bindstrat(s, goals, strats) for s in stream)

def bindstrat(s, goals, strats, joiner=interleave):
    """ Strategic bind """
    if not goals:
        return (s,)
    for strat in strats:
        goals = strat(s, goals)
    stream = goaleval(goals[0])(s)
    return bindstarstrat(stream, goals[1:], strats, joiner)

def earlysafe(s, goals):
    """ Place first goal at end if it raises an EarlyGoalError """
    if not goals:
        return goals
    goal = goaleval(goals[0])
    try:
        goal(s)
        return goals
    except EarlyGoalError:
        regoals = goals[1:] + (goals[0],)
        return earlysafe(s, regoals)

def anyfail(s, goals):
    """ Short circuit if any of the goals fail """
    if any(goaleval(goal) is fail for goal in goals):
        return (fail,)
    if any(goaleval(goal)(s) is () for goal in goals):
        return (fail,)
    else:
        return goals

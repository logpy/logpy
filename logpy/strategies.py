from logpy.util import interleave
from logpy.core import goaleval, EarlyGoalError


def bindearly(stream, *goals):
    return interleave(earlysafe(s, goals) for s in stream)

def earlysafe(s, goals):
    if not goals:
        return (s,)
    goal = goaleval(goals[0])
    try:
        substream = goal(s)
        return bindearly(substream, *goals[1:])
    except EarlyGoalError:
        regoals = goals[1:] + (goals[0],)
        return earlysafe(s, regoals)


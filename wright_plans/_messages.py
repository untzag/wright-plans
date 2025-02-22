import bluesky
from bluesky.utils import make_decorator
from typing import List

def inject_set_position_except_wrapper(plan, device, exceptions: List[str]):

    def _inject_set_position_except(msg):
        if msg.command == "set" and msg.obj == device:
            kwargs = msg.kwargs
            kwargs["exceptions"] = exceptions
            return bluesky.Msg("set", msg.obj, *msg.args, run=msg.run, **kwargs)
        return msg

    return (yield from bluesky.preprocessors.msg_mutator(plan, _inject_set_position_except))

inject_set_position_except = make_decorator(inject_set_position_except_wrapper)

def register_set_except(RE):
    return
    RE.register_command(
        "set_except",
        lambda msg: msg.obj.set_position_except(*msg.args, exceptions=msg.kwargs["exceptions"]),
    )


def set_relative_to_func_wrapper(plan, dic):
    def _set_relative(msg):
        if msg.command == "set" and msg.obj in dic:
            args = list(msg.args)
            args[0] += dic[msg.obj]()
            return bluesky.Msg("set", msg.obj, *args, run=msg.run, **msg.kwargs)
        return msg
    return (yield from bluesky.preprocessors.msg_mutator(plan, _set_relative))

set_relative_to_func = make_decorator(set_relative_to_func_wrapper)

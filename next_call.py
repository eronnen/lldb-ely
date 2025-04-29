import lldb

class NextCall(object):
    """
    Thread plan to step until a call instruction is reached, or returning from the function.
    """

    def __init__(self, thread_plan: lldb.SBThreadPlan, dict: dict):
        self._thread_plan = thread_plan
        self._thread_plan_stepover = None
        if not self._should_step_in():
            self._queue_next_plan()
        self._reason = "Reached call instruction"

    def _should_step_in(self):
        return False

    def _queue_next_plan(self):
        frame: lldb.SBFrame = self._thread_plan.GetThread().GetFrameAtIndex(0)
        pc: lldb.SBAddress = frame.GetPCAddress()
        target: lldb.SBTarget = self._thread_plan.GetThread().GetProcess().GetTarget()
        inst: lldb.SBInstruction = target.ReadInstructions(pc, 1)[0]
        self._thread_plan_stepover = self._thread_plan.QueueThreadPlanForStepOverRange(pc, inst.GetByteSize())

    def explains_stop(self, _event):
        return self._thread_plan_stepover is None and self._thread_plan.GetThread().GetStopReason() == lldb.eStopReasonTrace

    def should_stop(self, _event):
        if self._thread_plan_stepover is not None and not self._thread_plan_stepover.IsPlanComplete():
            return False

        frame: lldb.SBFrame = self._thread_plan.GetThread().GetFrameAtIndex(0)
        pc: lldb.SBAddress = frame.GetPCAddress()
        target: lldb.SBTarget = self._thread_plan.GetThread().GetProcess().GetTarget()
        inst: lldb.SBInstruction = target.ReadInstructions(pc, 1)[0]
        flow_kind = inst.GetControlFlowKind(target)
        if lldb.eInstructionControlFlowKindCall == flow_kind:
            self._thread_plan.SetPlanComplete(True)
            return True
        elif lldb.eInstructionControlFlowKindReturn == flow_kind:
            self._thread_plan.SetPlanComplete(True)
            self._reason = "Reached return"
            return True
            
        if self._thread_plan_stepover is not None:
            self._queue_next_plan()
        return False

    def should_step(self):
        return True
    
    def stop_description(self, stream):
        stream.Print(self._reason)


class NextCallWithStepIn(NextCall):
    def _should_step_in(self):
        return True


def __lldb_init_module(debugger, internal_dict):
    """
    Initialize the module and add the command to LLDB.
    """
    debugger.HandleCommand('command alias nc thread step-scripted -C next_call.NextCall')
    debugger.HandleCommand('command alias nci thread step-scripted -C next_call.NextCallWithStepIn')

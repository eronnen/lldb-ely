import lldb

def step_until_call(debugger: lldb.SBDebugger, command: str, exe_ctx: lldb.SBExecutionContext, result: lldb.SBCommandReturnObject, internal_dict: dict):
    """
    Step until a branch instruction is reached.
    """
    target: lldb.SBTarget = debugger.GetSelectedTarget()
    process: lldb.SBProcess = target.GetProcess()
    thread: lldb.SBThread = process.GetSelectedThread()

    while True:
        thread.StepInstruction(True)
        pc: lldb.SBFrame = thread.GetFrameAtIndex(0).GetPCAddress()
        inst: lldb.SBInstruction = target.ReadInstructions(pc, 1)[0]
        if inst is None:
            print("No instruction found at the current PC.")
            return

        flow_kind = inst.GetControlFlowKind(target)
        if lldb.eInstructionControlFlowKindCall == flow_kind:
            # Exit cleanly by broadcasting the last stop event
            stop_id: int = process.GetStopID()
            event: lldb.SBEvent = process.GetStopEventForStopID(stop_id)
            broadcaster: lldb.SBBroadcaster = process.GetBroadcaster()
            broadcaster.BroadcastEvent(event)
            return


def __lldb_init_module(debugger, internal_dict):
    """
    Initialize the module and add the command to LLDB.
    """
    debugger.HandleCommand('command script add -f step_until_call.step_until_call_old nb')

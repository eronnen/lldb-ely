import lldb

CALL_INSTRUCTIONS = [
    "call"
]

def step_until_call(debugger, command, result, internal_dict):
    """
    Step until a branch instruction is reached.
    """
    target = debugger.GetSelectedTarget()
    thread = target.GetProcess().GetSelectedThread()

    while True:
        thread.StepOver()
        pc = thread.GetFrameAtIndex(0).GetPCAddress()
        inst = target.ReadInstruction(pc, 1)[0]
        inst_name = inst.GetMnemonic().lower()
        if inst_name in CALL_INSTRUCTIONS:
            debugger.HandleCommand(f'disassemble -s {pc.GetLoadAddress()} -c 1')
            return


def _lldb_init_module(debugger, internal_dict):
    """
    Initialize the module and add the command to LLDB.
    """
    debugger.HandleCommand('command script add -f step_until_call.step_until_call nb')

import lldb

CALL_INSTRUCTIONS = [
    "callq",
]

def step_until_call(debugger, command, result, internal_dict):
    """
    Step until a branch instruction is reached.
    """
    target = debugger.GetSelectedTarget()
    thread = target.GetProcess().GetSelectedThread()

    while True:
        thread.StepInstruction(True)
        pc = thread.GetFrameAtIndex(0).GetPCAddress()
        inst = target.ReadInstructions(pc, 1)[0]
        inst_name = inst.GetMnemonic(target).lower()
        if inst_name in CALL_INSTRUCTIONS:
            debugger.HandleCommand(f'disassemble -s {pc.GetLoadAddress(target)} -c 1')
            return


def __lldb_init_module(debugger, internal_dict):
    """
    Initialize the module and add the command to LLDB.
    """
    debugger.HandleCommand('command script add -f step_until_call.step_until_call nb')

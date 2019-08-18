# ---------------------------- #
#    Hooks injection events    #
# ---------------------------- #
g_inject_loads = XModLib.HookUtils.HookEvent()
g_inject_basis = XModLib.HookUtils.HookEvent()
g_inject_hooks = XModLib.HookUtils.HookEvent()
g_inject_ovrds = XModLib.HookUtils.HookEvent()

# ---------------------------- #
#    Hooks injection chains    #
# ---------------------------- #
g_inject_stage_init = XModLib.HookUtils.HookChain()
g_inject_stage_main = XModLib.HookUtils.HookChain()
p_inject_stage_init = XModLib.HookUtils.HookChain()
p_inject_stage_main = XModLib.HookUtils.HookChain()

# -------------------------------- #
#    Hooks injection main stage    #
# -------------------------------- #
@XModLib.HookUtils.methodHookExt(g_inject_loads, gameplay.delegator.GameplayLogic, 'start', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
def new_GameplayLogic_start(*args, **kwargs):
	g_inject_stage_main()
	p_inject_stage_main()
	return


def prop_BT(csp, newVar=None):  # BACKTRACKING PROPAGATOR
    if not newVar:
        return True, []
    for c in csp.getConstraintsWithVariables(newVar):
        if c.getNumberOfUnassignedVars() == 0:
            vals = []
            vars = c.getScope()
            for var in vars:
                vals.append(var.getAssignedValue())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):  # FORWARD CHECKING PROPAGATOR
    pruned = []
    isDeadEnd = False

    if not newVar:
        cons = csp.getAllConstraints()
        for con in cons:
            scope = con.getScope()
            if len(scope) == 1:
                result = FCCheck(con, scope[0])
                pruned.extend(result[1])
                if not result[0]:
                    isDeadEnd = True
                    break

    cons = csp.getAllConstraints()
    for con in cons:
        scope = con.getScope()
        if con.getNumberOfUnassignedVars() == 1:
            result = FCCheck(con, con.getUnassignedVars()[0])
            pruned.extend(result[1])
            if not result[0]:
                isDeadEnd = True
                break
    if isDeadEnd:
        return False, pruned
    return True, pruned


def FCCheck(C, x):  # FORWARD CHECKING ALGORITHM
    pruned = []
    cur_dom = x.getCurDomain()

    for val in cur_dom:
        if not C.hasSupport(x, val):
            x.pruneValue(val)
            pruned.append((x, val))

    if not x.getCurDomainSize():
        return False, pruned
    return True, pruned


def prop_GAC(csp, newVar=None):  # GENERALIZED ARC CONSISTENCY PROPAGATOR
    queue = []
    pruned = []
    cons = csp.getAllConstraints()

    if not newVar:
        queue = cons.copy()
    else:
        queue = csp.getConstraintsWithVariables(newVar).copy()

    count = 0
    while count < len(queue):

        con = queue[count]
        scope = con.getScope()

        for i in range(len(scope)):
            var = scope[i]
            curDomain = var.getCurDomain()
            found = False
            for val in curDomain:
                if con.hasSupport(var, val):
                    continue
                else:
                    found = True
                    var.pruneValue(val)
                    pruned.append((var, val))
                    if not var.getCurDomainSize():
                        queue = []
                        return False, pruned

            if found:
                cons = csp.getConstraintsWithVariables(var)
                for c in cons:
                    if c not in queue[count:]:
                        queue.append(c)
        count += 1

    return True, pruned

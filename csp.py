# import time


class Variable:
    def __init__(self, name, domain=None):
        if domain is None:
            domain = []
        self.name = name
        self.dom = list(domain)
        self.curDomain = [True] * len(domain)
        self.assignedValue = None

    def addDomainValues(self, values):
        for val in values:
            self.dom.append(val)
            self.curDomain.append(True)

    def getDomainSize(self):
        """Return the size of the domain"""
        return len(self.dom)

    def domain(self):
        """return the variable's domain"""
        return list(self.dom)

    def pruneValue(self, value):
        """Remove value from curDomain"""
        self.curDomain[self.getValueIndex(value)] = False

    def depruneValue(self, value):
        """Restore value to curDomain"""
        self.curDomain[self.getValueIndex(value)] = True

    def getCurDomain(self):
        """return list of values in curDomain"""
        vals = []
        if self.isAssigned():
            vals.append(self.getAssignedValue())
        else:
            for i, val in enumerate(self.dom):
                if self.curDomain[i]:
                    vals.append(val)
        return vals

    def isInCurDomain(self, value):
        """check if value is in curDomain, if assigned only assigned
        value is viewed as being in curDomain"""
        if value not in self.dom:
            return False
        if self.isAssigned():
            return value == self.getAssignedValue()
        else:
            return self.curDomain[self.getValueIndex(value)]

    def getCurDomainSize(self):
        """Return the size of the variables domain"""
        if self.isAssigned():
            return 1
        else:
            return sum(1 for v in self.curDomain if v)

    def restoreCurDomain(self):
        """return all values back into curDomain"""
        for i in range(len(self.curDomain)):
            self.curDomain[i] = True

    def isAssigned(self):
        return self.assignedValue is not None

    def assign(self, value):
        """When we assign we remove all other values from curDomain."""
        if self.isAssigned() or not self.isInCurDomain(value):
            print("ERROR: trying to assign variable", self,
                  "that is already assigned or illegal value (not in curdom)")
            return

        self.assignedValue = value

    def unassign(self):
        """Unassign and restore old curDomain"""
        if not self.isAssigned():
            print("ERROR: trying to unassign variable", self, " not yet assigned")
            return
        self.assignedValue = None

    def getAssignedValue(self):
        return self.assignedValue

    def getValueIndex(self, value):
        """Return the index in the domain list of a variable value"""
        return self.dom.index(value)

    def __repr__(self):
        return "Var-{}".format(self.name)

    def __str__(self):
        return "Var--{}".format(self.name)


class Constraint:
    def __init__(self, name, scope):
        self.scope = list(scope)
        self.name = name
        self.sat_tuples = dict()
        self.sup_tuples = dict()

    def addSatisfyingTuples(self, tuples):
        """We specify the constraint by adding its complete list of satisfying tuples."""
        for x in tuples:
            t = tuple(x)
            if t not in self.sat_tuples:
                self.sat_tuples[t] = True

            for i, val in enumerate(t):
                var = self.scope[i]
                if not (var, val) in self.sup_tuples:
                    self.sup_tuples[(var, val)] = []
                self.sup_tuples[(var, val)].append(t)

    def getScope(self):
        """get list of variables the constraint is over"""
        return list(self.scope)

    def check(self, vals):
        return tuple(vals) in self.sat_tuples

    def getNumberOfUnassignedVars(self):
        """return the number of unassigned variables in the constraint's scope"""
        n = 0
        for v in self.scope:
            if not v.isAssigned():
                n = n + 1
        return n

    def getUnassignedVars(self):
        """return list of unassigned variables in constraint's scope."""
        vs = []
        for v in self.scope:
            if not v.isAssigned():
                vs.append(v)
        return vs

    def hasSupport(self, var, val):
        if (var, val) in self.sup_tuples:
            for t in self.sup_tuples[(var, val)]:
                if self.tupleIsValid(t):
                    return True
        return False

    def tupleIsValid(self, t):
        """Check if every value in tuple is still in corresponding variable domains"""
        for i, var in enumerate(self.scope):
            if not var.isInCurDomain(t[i]):
                return False
        return True

    def __str__(self):
        return "{}({})".format(self.name, [var.name for var in self.scope])


class CSP:
    def __init__(self, name, variables=None):
        if variables is None:
            variables = []
        self.name = name
        self.vars = []
        self.cons = []
        self.vars_to_cons = dict()
        for v in variables:
            self.addVariable(v)

    def addVariable(self, v):
        if not type(v) is Variable:
            print("Trying to add non variable ", v, " to CSP object")
        elif v in self.vars_to_cons:
            print("Trying to add variable ", v, " to CSP object that already has it")
        else:
            self.vars.append(v)
            self.vars_to_cons[v] = []

    def addConstraint(self, c):
        if not type(c) is Constraint:
            print("Trying to add non constraint ", c, " to CSP object")
        else:
            for v in c.scope:
                if v not in self.vars_to_cons:
                    print("Trying to add constraint ", c, " with unknown variables to CSP object")
                    return
                self.vars_to_cons[v].append(c)
            self.cons.append(c)

    def getAllConstraints(self):
        """return list of all constraints in the CSP"""
        return self.cons

    def getConstraintsWithVariables(self, var):
        """return list of constraints that include var in their scope"""
        return list(self.vars_to_cons[var])

    def getAllVariables(self):
        """return list of variables in the CSP"""
        return list(self.vars)

    def printAll(self):
        print("CSP", self.name)
        print("   Variables = ", self.vars)
        print("   Constraints = ", self.cons)

    def printSolution(self):
        print("CSP", self.name, " Assignments = ")
        for v in self.vars:
            print(v, " = ", v.getAssignedValue(), "    ", end='')
        print("")


##################################
###### Backtracking Routine ######
##################################

def restoreValues(prunes):
    """Restore list of values to variable domains
       each item in prunes is a pair (var, val)"""
    for var, val in prunes:
        var.depruneValue(val)


class BT:
    def __init__(self, csp):
        self.unassignedVars = []
        self.csp = csp
        self.nDecisions = 0

        self.nPrunes = 0
        self.TRACE = False
        self.runtime = 0

    def traceOn(self):
        """Turn search trace on"""
        self.TRACE = True

    def traceOff(self):
        """Turn search trace off"""
        self.TRACE = False

    def clearStatistics(self):
        """Initialize counters"""
        self.nDecisions = 0
        self.nPrunes = 0
        self.runtime = 0

    def printStatistics(self):
        print("Search made {} variable assignments and pruned {} variable values".format(
            self.nDecisions, self.nPrunes))

    def restoreAllVariableDomains(self):
        """Reinitialize all variable domains"""
        for var in self.csp.vars:
            if var.isAssigned():
                var.unassign()
            var.restoreCurDomain()

    def restoreUnassignedVar(self, var):
        """Add variable back to list of unassigned vars"""
        self.unassignedVars.append(var)

    ##################################
    ###### BACKTRACKING SEARCH #######
    ##################################

    def backtrackingSearch(self, propagator):
        self.clearStatistics()

        # sTime = time.process_time()

        for v in self.csp.vars:
            if not v.isAssigned():
                self.unassignedVars.append(v)

        status, prunes = propagator(self.csp)  # initial propagate no assigned variables.
        self.nPrunes = self.nPrunes + len(prunes)

        if self.TRACE:
            print(len(self.unassignedVars), " unassigned variables at start of search")
            print("Root Prunes: ", prunes)

        if not status:
            print("CSP{} detected contradiction at root".format(
                self.csp.name))
        else:
            status = self.backtrackingRecursion(propagator, 1)  # now do recursive search

        restoreValues(prunes)
        if not status:
            print("CSP{} unsolved. Has no solutions".format(self.csp.name))

        # sTime = sTime - time.process_time()
        return self.nDecisions

    def backtrackingRecursion(self, propagator, level):
        """ Return true if found solution. False if still need to search."""
        if self.TRACE:
            print('  ' * level, "bt_recurse level ", level)

        if not self.unassignedVars:
            return True
        else:
            var = self.extractVariable()
            if not var:
                return True
            if self.TRACE:
                print('  ' * level, "bt_recurse var = ", var)

            for val in var.getCurDomain():

                if self.TRACE:
                    print('  ' * level, "bt_recurse trying", var, "=", val)

                var.assign(val)
                self.nDecisions = self.nDecisions + 1

                status, prunes = propagator(self.csp, var)
                self.nPrunes = self.nPrunes + len(prunes)

                if self.TRACE:
                    print('  ' * level, "bt_recurse prop status = ", status)
                    print('  ' * level, "bt_recurse prop pruned = ", prunes)

                if status:
                    if self.backtrackingRecursion(propagator, level + 1):
                        return True

                if self.TRACE:
                    print('  ' * level, "bt_recurse restoring ", prunes)
                restoreValues(prunes)
                var.unassign()

            self.restoreUnassignedVar(var)
            return False

    def extractVariable(self):
        """Remove variable from list of unassigned vars."""
        for var in self.unassignedVars:
            if var.getCurDomainSize() == 1:
                self.unassignedVars.remove(var)
                return var

        for con in self.csp.getAllConstraints():
            if con.getNumberOfUnassignedVars() == 0:
                continue
            if con.getNumberOfUnassignedVars() == 1:
                mv = con.getUnassignedVars()[0]
                self.unassignedVars.remove(mv)
                return mv
        return None

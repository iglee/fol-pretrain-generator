"""
Script for generating FOL rule sets. This script randomly picks variables and operators to generate at varying depths of parse.
Running this script `python fol_generator.py` generates and pickles a rule set.
"""

import sympy as sp
from sympy import Symbol
from sympy.logic.boolalg import And, Or, Not, Implies, simplify_logic
import random
from tqdm import tqdm
import pickle

# Function to generate a random first-order logic formula
def random_formula(symbols, depth=3, max_variables=5, count=0):
    # Base case: If depth is 0, return a random variable
    if depth == 0:
        return random.choice(symbols), count + 1

    # Randomly choose an operator
    op = random.choice([And, Or, Not, Implies])

    # If the operator is NOT, apply it to a subexpression
    if op == Not:
        expr, count = random_formula(symbols, depth - 1, max_variables, count)
        return op(expr, evaluate=False), count + 1

    # Otherwise, create two subexpressions
    left_expr, count = random_formula(symbols, depth - 1, max_variables, count)
    right_expr, count = random_formula(symbols, depth - 1, max_variables, count)

    return op(left_expr, right_expr, evaluate=False), count + 1


def calculate_circuit_complexity(expression):
    # Base case: Atomic values count as 1
    if (
        isinstance(expression, (str, bool))
        or hasattr(expression, "is_Atom")
        and expression.is_Atom
    ):
        return 1

    # Recursive case: count the operator and all subexpressions
    if hasattr(expression, "args"):
        return 1 + sum(calculate_circuit_complexity(arg) for arg in expression.args)

    # Fallback for unsupported types
    raise TypeError(f"Unsupported expression type: {type(expression)}")

def generate_variables(num_variables=5):
    greek_unicode = ['α', 'β', 'γ', 'δ', 'ε']
    return sp.symbols(' '.join(greek_unicode[:num_variables]))


# Print with Unicode, for uniform formatting of FOL
def print_formula(formula):
    return sp.printing.pretty(formula, use_unicode=True)


# Function to search and simplify a subexpression with depth < 2
def simplify_subexpression(formula, d=2):

    def get_depth(expr):
        if isinstance(expr, (And, Or, Implies)):
            return 1 + max(get_depth(sub_expr) for sub_expr in expr.args)
        elif isinstance(expr, Not):
            return 1 + get_depth(expr.args[0])
        return 0

    simplified_once = False
    complexity_count = 0  

    def traverse_and_simplify(expr, d):
        nonlocal simplified_once, complexity_count
        complexity_count += 1

        if simplified_once:
            return expr

        if get_depth(expr) < d:
            
            for i in range(d):
                if i < 2:
                    simplified_expr = simplify_logic(expr, deep=False)
                else:
                    simplified_expr = traverse_and_simplify(expr, d=i)

                if simplified_expr != expr:
                    simplified_once = True
                #simplified_expr = simplified_expr.subs({True: BooleanTrue(evaluate=False), False: BooleanFalse(evaluate=False)})
                #simplified_expr = simplified_expr.subs({True: Symbol('True', real=True, evaluate=False), False: Symbol('False', real=True, evaluate=False)})

                return simplified_expr

        elif isinstance(expr, Not):
            if expr.args[0] == sp.true:
                #print("Negation: evaluate bools, true -> false")
                simplified_once = True
                return sp.false
            
            if expr.args[0] == sp.false:
                #print("Negation: evaluate bools, false -> true")
                simplified_once = True
                return sp.true

            if isinstance(expr.args[0], Not):
                #print("Double Negation Simplified", expr, expr.args[0].args[0])
                simplified_once = True
                return expr.args[0].args[0]

            if isinstance(expr.args[0], Or):
                #print("Negation: de Morgans OR simplified")
                simplified_once = True
                tmp = expr.args[0].args
                tmp = [Not(x, evaluate = False) for x in tmp]
                return And(*tmp, evaluate=False)

            if isinstance(expr.args[0], And):
                #print("Negation: de Morgans AND simplified")
                simplified_once = True
                tmp = expr.args[0].args
                tmp = [Not(x, evaluate = False) for x in tmp]
                return Or(*tmp, evaluate=False)

            new_arg = traverse_and_simplify(expr.args[0], d=2)
            return Not(new_arg, evaluate=False)

        elif isinstance(expr, Implies):
            #print(expr, expr.args[0].is_Atom, expr.args[1].is_Atom)
            if expr.args[0] == expr.args[1]:
                #print("Implies: Tautology, expressions the same")
                simplified_once = True
                return sp.true

            if expr.args[0].is_Atom and expr.args[1].is_Atom:
                possible_simplification = Implies(expr.args[0], expr.args[1], evaluate=True)
                if possible_simplification != expr:
                    #print("Implies simplified: is atom", expr)
                    simplified_once = True
                    return possible_simplification

            if get_depth(expr) < 5:
                #print("Implies simplified: identity rule", expr, "->",  Or(Not(expr.args[0], evaluate=False), expr.args[1], evaluate=False))
                simplified_once = True
                return Or(Not(expr.args[0], evaluate=False), expr.args[1], evaluate=False)
            
            
            if traverse_and_simplify(expr.args[0], d=2) != expr.args[0]:
                return Implies(traverse_and_simplify(expr.args[0], d=d), expr.args[1], evaluate=False)
            else:
                return Implies(expr.args[0], traverse_and_simplify(expr.args[1], d=d), evaluate=False)
        

        elif isinstance(expr, (And, Or)):
            args = list(expr.args)
            tmp = args[:]
            

            for i in range(len(tmp)):
                
                if get_depth(tmp[i]) < 2:
                    simplified_arg = simplify_logic(tmp[i], deep=False)
                    if simplified_arg != tmp[i]:
                        tmp[i] = simplified_arg
                        return expr.func(*tmp, evaluate=False)     
            

            new_args = []
            for i in range(0, len(args), 2):  # Process 2 arguments at a time
                subset = args[i:i+2]
                simplified_subset = [traverse_and_simplify(arg, d=2) for arg in subset]

                if simplified_subset != subset:
                    # Simplification occurred; stop early and extend with the rest of original args
                    new_args.extend(simplified_subset)
                    new_args.extend(args[i+2:])  # Append the remaining original args
                    return expr.func(*new_args, evaluate=False)

                new_args.extend(simplified_subset)
            
            # for distributive/associative rules for FOL, but for the most part ignore, cause it takes a really long time recursively
            """
            new_args = []
            for i in range(0, len(args), 2):  # Process 2 arguments at a time
                subset = args[i:i+2]
                if len(subset) < 2:
                    continue
                if get_depth(subset[0]) < 3 and get_depth(subset[1]) < 3:
                    tmp = simplify_logic(expr.func(*subset, evaluate=False))
                    new_args.append(tmp)
                    #print(subset, tmp.args)
                    if sorted(tmp.args, key=str) != sorted(subset, key=str):
                        new_args.extend(args[i+2:])
                        #print("And/Or simplification", subset, " -> ",tmp)
                        #print(new_args)
                        return expr.func(*new_args, evaluate=False)
            """
            
            return expr.func(*new_args, evaluate=False)

        return expr

    simplified_formula = traverse_and_simplify(formula, d)
    return simplified_formula, complexity_count


def count_unique_operators_and_variables(expr):
    operators = set()
    variables = set()

    def traverse(expr):
        if isinstance(expr, sp.Symbol):
            variables.add(expr)
            return

        if isinstance(expr, (sp.And, sp.Or, sp.Not, sp.Implies)):
            operators.add(type(expr))
            for arg in expr.args:
                traverse(arg)
            return

        if isinstance(expr, sp.Not):
            traverse(expr.args[0])
        elif isinstance(expr, (sp.And, sp.Or, sp.Implies)):
            for arg in expr.args:
                traverse(arg)

    traverse(expr)

    return len(operators), len(variables)


def generate_datum():

    # Determine the number of variables randomly
    num_variables = random.randint(2, 4)
    symbols = generate_variables(num_variables)
    depth_exp = random.randint(1, 4)

    # Generate a random formula
    formula, complexity = random_formula(
        symbols=symbols, depth=depth_exp, max_variables=num_variables
    )

    cnt_o, cnt_v = count_unique_operators_and_variables(formula)

    # Print the generated formula
    # print(
    #    f"Generated Formula: {print_formula(formula)}, Complexity: {complexity}, Number of Variables: {cnt_v}, Number of Operators: {cnt_o}, Depth of expression: {depth_exp}"
    # )

    depth = 2
    cnt = 0

    datum = {
        "program_complexity": complexity,
        "original_depth": depth_exp,
        "original_complexity": complexity + cnt_v + cnt_o,
    }

    # Hard coded the max number of iterations.. Prob not the best way to do this.. :/
    cnt_max = 20

    complexity_by_step = [calculate_circuit_complexity(formula) ]
    num_ops_by_steps = [cnt_o]
    num_vars_by_steps = [cnt_v]
    steps = [print_formula(formula)]
    elimination_complexity = []
    simplified_final = simplify_logic(formula)

    while cnt < cnt_max:

        if formula == formula.atoms():
            break

        if formula == True or formula == False:
            break

        if formula == simplified_final:
            break

        if depth > 4:
            break

        simplified_formula, simplify_complexity = simplify_subexpression(formula, depth)
        print_formula(simplified_formula)

        if formula == simplified_formula:
            depth += 1
            #print("did not simplify:", depth, cnt)
            cnt += 1
        else:
            #print("--")
            #print(f"Depth {depth-1}, Original Formula: {print_formula(formula)}")
            #print(
            #   f"Depth {depth-1}, Simplified Formula: {print_formula(simplified_formula)}, Complexity: {simplify_complexity}"
            #)

            formula = simplified_formula
            cnt_o, cnt_v = count_unique_operators_and_variables(formula)
            steps.append(print_formula(formula))
            complexity_by_step.append(
                calculate_circuit_complexity(formula)
            )
            num_ops_by_steps.append(cnt_o)
            num_vars_by_steps.append(cnt_v)
            elimination_complexity.append(simplify_complexity)
            depth = 1

    
    datum["exprs"] = steps
    datum["complexity_by_step"] = complexity_by_step
    datum["elimination_complexity"] = elimination_complexity
    datum["num_var"] = num_vars_by_steps
    datum["num_ops"] = num_ops_by_steps


    if simplify_logic(formula) != simplified_final:
        #print("DID NOT MATCH: ")
        #print(formula)
        #print(simplify_logic(formula))
        #print("correct: ", simplified_final)
        #print("\n\n\n======")
        return None





    # print(steps)
    # print(complexity_by_step)
    # print(
    #    "Number of operators: {}, Number of variables: {}".format(
    #        *count_unique_operators_and_variables(last_formula)
    #    )
    # )
    # print("final complexity: {}".format(calculate_circuit_complexity(last_formula)))

    return datum


dataset = []
unique_exprs = set()


N = 2500000
pbar = tqdm(total=N, desc="Generating unique expressions")

while len(unique_exprs) < N:
    datum = generate_datum()
    if datum == None:
        continue
    exprs = datum["exprs"]

    # if the expression is already the simplest and there's no simplifications to be made, do not add to data.
    if len(exprs) < 2:
        continue

    complexity = datum["original_complexity"] + sum(datum["elimination_complexity"])
    expr = " \u21D4 ".join(["(" + x + ")" for x in exprs])

    if expr not in unique_exprs:
        
        #print(datum['exprs'])
        dataset.append((expr, complexity, datum))
        unique_exprs.add(expr)
        pbar.update(1)
    #print("\n\n\n==============")
    

pbar.close()

with open("unique_fol_rules.pkl", "wb") as f:
    pickle.dump(dataset, f)

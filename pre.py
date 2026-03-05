import networkx as nx

def reverse_postorder(node_succs, start):
    G = nx.DiGraph()
    for u, succs in node_succs.items():
        for v in succs:
            G.add_edge(u, v)

    postorder = list(nx.dfs_postorder_nodes(G, start))
    return list(reversed(postorder))


node_succs = {0: [1], 
                1: [2, 3], 
                2: [22], 
                22: [4], 
                3: [32], 
                32: [4], 
                4: [5], 
                5: [6, 7], 
                6: [62],
                62: [8], 
                7: [10, 11], 
                8: [9, 12], 
                9: [92],
                92: [9], 
                10: [13], 
                11: [15], 
                12: [122, 18], 
                122: [17], 
                13: [14, 16], 
                14: [13], 
                15: [152], 
                152: [17], 
                16: [162], 
                162: [17], 
                17: [18],
                18: []
}

node_preds = {key: [] for key in node_succs}
for key, value in node_succs.items():
    for v in value:
        node_preds[v].append(key)

print(f"node_preds: {node_preds}")

e_use_B = {2: {"a + b"}, 4: {"a + b"}, 9: {"a + b"}, 13: {"a + b"}, 15: {"a + b"}, 17: {"a + b"}}

e_kill_B = {1: {"a + b"}, 5: {"a + b"}, 11: {"a + b"}}

U = {"a + b"}

anticipated_in = {key: U.copy() for key in node_succs.keys()}
anticipated_in[18] = set()
anticipated_out = {key: set() for key in anticipated_in.keys()}

rpo = reverse_postorder(node_succs, start=0)
print(rpo)

changes = True
while changes:
    changes = False
    for B in reversed(rpo):
        value = anticipated_in[B]
        print(f"key: {B}, value: {value}, anticipated_out[B]: {anticipated_out[B]}")
        new_out = set()
        if node_succs[B]:
            new_out = set.intersection(*(anticipated_in[S] for S in node_succs[B]))
        if new_out != anticipated_out[B]:
            anticipated_out[B] = new_out
            changes = True

        use = e_use_B.get(B, set())
        kill = e_kill_B.get(B, set())

        new_in = use.union(anticipated_out[B] - kill)
        if new_in != anticipated_in[B]:
            anticipated_in[B] = new_in
            changes = True


print(f"anticipated_in: {anticipated_in}")
print(f"anticipated_out: {anticipated_out}")

available_out = {key: U.copy() for key in node_succs.keys()}
available_out[0] = set()
available_in = {key: U.copy() for key in node_succs.keys()}

changes = True
while changes:
    changes = False
    for B in rpo:
        value = available_in[B]
        print(f"key: {B}, value: {value}, available_out[B]: {available_out[B]}")
        new_in = set()
        if node_preds[B]:
            new_in = set.intersection(*(available_out[P] for P in node_preds[B]))
        if new_in != available_in[B]:
            available_in[B] = new_in
            changes = True

        kill = e_kill_B.get(B, set())

        new_out = (anticipated_in[B].union(available_in[B])) - kill
        if new_out != available_out[B]:
            changes = True
            available_out[B] = new_out

print(f"available_in: {available_in}")
print(f"available_out: {available_out}")

earliest = {key: (anticipated_in[key] - available_in[key]) for key in node_succs}

print(f"earliest: {earliest}")

postponable_out = {key: U.copy() for key in node_succs.keys()}
postponable_out[0] = set()
postponable_in = {key: U.copy() for key in node_succs.keys()}

changes = True
while changes:
    changes = False
    for B in rpo:
        value = postponable_in[B]
        print(f"key: {B}, value: {value}, postponable_out[B]: {postponable_out[B]}")
        new_in = set()
        if node_preds[B]:
            new_in = set.intersection(*(postponable_out[P] for P in node_preds[B]))
        if new_in != postponable_in[B]:
            postponable_in[B] = new_in
            changes = True

        use = e_use_B.get(B, set())

        new_out = (earliest[B].union(postponable_in[B])) - use
        if new_out != postponable_out[B]:
            changes = True
            postponable_out[B] = new_out


print(f"postponable_in: {postponable_in}")
print(f"postponable_out: {postponable_out}")

latest = {}
for B in node_succs:
    print(f"B: {B}")
    use = e_use_B.get(B, set())
    first = set.union(earliest[B], postponable_in[B])
    second = set()
    if node_succs[B]:
        second = set.union(use, U - set.intersection(*(set.union(earliest[S], postponable_in[S]) for S in node_succs[B])))
    else:
        # second = set.union(use, U.copy())
        # vacuous meet?
        second = use
    latest[B] = set.intersection(first, second)

print(f"latest: {latest}")

used_in = {key: set() for key in node_succs.keys()}
used_out = {key: set() for key in node_succs.keys()}

changes = True
while changes:
    changes = False
    for B in reversed(rpo):
        value = used_out[B]
        print(f"key: {B}, value: {value}, used_out[B]: {used_out[B]}")
        new_out = set()
        if node_succs[B]:
            new_out = set.union(*(used_in[S] for S in node_succs[B]))
        if new_out != used_out[B]:
            used_out[B] = new_out
            changes = True

        use = e_use_B.get(B, set())

        new_in = (set.union(use, used_out[B])) - latest[B]
        if new_in != used_in[B]:
            used_in[B] = new_in
            changes = True

print(f"latest: {latest}")

print(f"used_in: {used_in}")
print(f"used_out: {used_out}")

blocks = []
for B in node_preds:
    myset = set.intersection(latest[B], used_out[B])
    # print(f"myset: {myset}")
    if "a + b" in myset:
        blocks.append(B)

print(f"blocks: {blocks}")

replace = []
for B in node_preds:
    use = e_use_B.get(B, set())
    myset = set.intersection(use, set.union(U - latest[B], used_out[B]))
    if "a + b" in myset:
        replace.append(B)

print(f"replace: {replace}")
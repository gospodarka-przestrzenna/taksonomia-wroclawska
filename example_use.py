from .graph import Node, Edge, Graph
from .bmst2 import Bmst

g=Graph(is_directed=True)

n1=Node()
n2=Node()
n3=Node()
n4=Node()
n5=Node()
n1['id']=1
n2['id']=2
n3['id']=3
n4['id']=4
n5['id']=5

e1=Edge({"weight": 9})
e2=Edge({"weight": 9})
e3=Edge({"weight": 1})
e4=Edge({"weight": 1})
e5=Edge({"weight": 2})
e6=Edge({"weight": 2})
e7=Edge({"weight": 3})
e8=Edge({"weight": 3})
e9=Edge({"weight": 2})
e10=Edge({"weight": 2})

g.add_node(n1)
g.add_node(n2)
g.add_node(n3)
g.add_node(n4)
g.add_node(n5)


g.add_edge(n1,n2,e1)
g.add_edge(n2,n1,e2)
g.add_edge(n2,n3,e3)
g.add_edge(n3,n2,e4)
g.add_edge(n3,n4,e5)
g.add_edge(n4,n3,e6)
g.add_edge(n4,n5,e7)
g.add_edge(n5,n4,e8)
g.add_edge(n5,n1,e9)
g.add_edge(n1,n5,e10)

g.order_by("weight")

#print(g)
#bmst_wynik = Bmst(g,"weight","sup","phase")
#print(bmst_wynik)
#print(g[5],[prefix+"bmst_supernode"])
#print(bmst_wynik.next_phase)

#,prefix+"weight")

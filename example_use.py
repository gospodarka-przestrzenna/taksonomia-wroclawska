from bmst import Node, Edge, Graph, Bmst

n1=Node()
n2=Node()
n3=Node()
n4=Node()
n5=Node()

e1=Edge(n1,n2, properties = {"weight": 9})
e2=Edge(n2,n1, properties = {"weight": 9})
e3=Edge(n2,n3, properties = {"weight": 1})
e4=Edge(n3,n2, properties = {"weight": 1})
e5=Edge(n3,n4, properties = {"weight": 2})
e6=Edge(n4,n3, properties = {"weight": 2})
e7=Edge(n4,n5, properties = {"weight": 3})
e8=Edge(n5,n4, properties = {"weight": 3})
e9=Edge(n5,n1, properties = {"weight": 2})
e10=Edge(n1,n5, properties = {"weight": 2})

g=Graph()

g.add_node(n1)
g.add_node(n2)
g.add_node(n3)
g.add_node(n4)
g.add_node(n5)

g.add_edge(e1)
g.add_edge(e2)
g.add_edge(e3)
g.add_edge(e4)
g.add_edge(e5)
g.add_edge(e6)
g.add_edge(e7)
g.add_edge(e8)
g.add_edge(e9)
g.add_edge(e10)

bmst_wynik = Bmst(g,"weight")

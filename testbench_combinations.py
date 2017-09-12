import preprocessingstep as p
l1=[1,2]
l2=[]
a=list(p.permutations(l1))
print(a)
b=list(p.onoff(l2))
print(b)
c=p.concatstepslists(a,b)
print(list(c))

#Sofia Wyetzner, March 2015
#English Syntax Analyzer
#Created for Univeristy of Chicago course CMSC 16200 - Honors Introduction to Programming II
#pos.py

import nltk
import re
import random

def pos(t):
	"""
	Function: tokenizes and tags text with parts of speech
	Parameters: string of text
	Returns: list of tuples: [(word,tag)...]
	"""
	text = nltk.word_tokenize(t)
	tags = nltk.pos_tag(text)
	return tags

# List of complex pos contained in universal types
nountypes = ["EX","NN","NNS","NNPS","PRP","WP","VBG"]
verbtypes = ["MD","VB","VBD","VBP","VBZ"]
adjtypes = ["CD","JJ","JJR","JJS","VBN","WP$","PDT"]
advtypes = ["RB","RBR","RBS","WRB"]
preptypes = ["IN","POS"]
dettypes = ["DT","PRP$"]
conjtypes = ["CC"]
punctuation = [".",",",";","?","!"]

class Node(object):
	"""
	Class: represents tree node 
	Parameters: part of speech tag or phrase tag that becomes the head
	"""
	def __init__(self, typ):
		self.head = typ
		self.nodes = []
		self.root = None
		self.isLeaf = False
	def addNodes(self,nodes):
		self.nodes = nodes
		for n in nodes:
			n.root = self
	def __str__(self):
		nodes = ""
		for n in self.nodes:
			nodes = nodes + "("+n.__str__()+")"
		return self.head +" "+ "("+ nodes + ")"

class Leaf(Node):
	"""
	Class: represents leaf of tree with word and part of speech tag 
	Parameters: part of speech and word
	"""
	def __init__(self, typ, word):
		self.head = typ
		self.word = word
		self.root = None
		self.isLeaf = True
	def __str__(self):
		return self.head +","+ self.word


class Rule(object):
	"""
	Class: parses phrase structure rules and can say if nodes satisy the rule
	Parameters: phrase structure rule string
	"""
	def __init__(self,r):
		s = r.split("->")
		s[1] = s[1].split()
		s[0] = s[0].split()
		if len(s[0]) > 1:
			self.communal = True
		else:
			self.communal = False
		self.head = s[0][0]
		self.items = s[1]
	def satisfy(self, tokens):
		items = self.items
		i = 0
		j = 0
		while i < len(items) and j < len(tokens):
			if items[i][0] == '(':
				if not tokens[j].head == items[i][1:-1]:
					i += 1
				else:
					i += 1
					j += 1
			elif not tokens[j].head == items[i]:
				return None
			else:
				i += 1
				j += 1
		if i < len(items):
			return None
		else:
			return tokens[:j]

# Rule lists based on Precedence -> all left associative
# (_) indicates optional
rules1 = [
Rule("N -> N Conj. N"),
Rule("V -> V Conj. V"),
Rule("P -> P Conj. P"),
Rule("A -> A Conj. A"),
Rule("NP -> NP Conj. NP"),
Rule("PP -> PP Conj. PP"),
Rule("AP -> AP Conj. AP"),
Rule("VP -> VP Conj. VP")
]

rules2 = [
Rule("NP -> N N"),
Rule("NP -> (D) N"),
Rule("INF -> TO V"),
Rule("PP -> AV P"),
Rule("PP -> P A"),
Rule("AP -> (A) A"),
Rule("NP -> AP NP"),
Rule("VP -> V A"),
Rule("VP -> AV V"),
Rule("VP -> V V"),
Rule("VP -> WDT VP")
]

rules3 = [
Rule("NP -> D NP"),
Rule("VP -> VP RP"),
Rule("PP -> P (AV) NP"),
Rule("VP -> VP (INF) NP"),
Rule("AP -> AV AP"),
Rule("VP -> AV VP"),
Rule("VP -> VP (INF) PP"),
Rule("PP -> PP PP"),
Rule("NP -> A NP"),
Rule("NP -> NP RP"),
Rule("PP -> PP VP"),
Rule("VP -> (AV) V NP"),
Rule("VP -> V VP"),
Rule("VP -> (AV) VP NP"),
Rule("NP -> TO NP"),
Rule("PP -> PP PP"),
Rule("C -> WDT NP VP"),
Rule("NP -> NP NP"),
Rule("VP -> VP VP")
]

rules4 = [
Rule("S -> (PP) NP VP (PP) C"),
Rule("S -> (PP) NP VP")
]

def getType(word):
	"""
	Function: replaces complex ntlk tags with universal ones
	Parameters: tuple of word and pos
	Returns: string with universal type or original if unknown
	"""
	type = word[1]
	if type in nountypes:
		return "N"
	elif type in verbtypes:
		return "V"
	elif type in adjtypes:
		return "A"
	elif type in advtypes:
		return "AV"
	elif type in preptypes:
		return "P"
	elif type in dettypes:
		return "D"
	elif type in conjtypes:
		return "Conj."
	else:
		return type


def makeLeaves(tokens):
	"""
	Function: takes word tuples and creates a list of leaves
	Parameters: list of word tuples
	Returns: list of leaves
	"""
	leaves = []
	t = 0
	while t < len(tokens):
		if t+1 < len(tokens) and tokens[t][1] == tokens[t+1][1]:
			l = Leaf(getType(tokens[t]), tokens[t][0])
			l2 = Leaf(getType(tokens[t+1]), tokens[t+1][0])
			n = Node(getType(tokens[t]))
			n.addNodes([l,l2])
			leaves.append(n)
			t += 2
		else:
			l = Leaf(getType(tokens[t]), tokens[t][0])
			leaves.append(l)
			t += 1
	return leaves


def reduce(leaves,i,rules):
	"""
	Function: checks beginning of a sublist of leaves against rules list and replaces nodes with head phrases
	Parameters: leaves list, start index, rules list
	Returns: nodes list
	"""
	sentence = leaves
	for r in rules:
		if r.satisfy(sentence[i:]):
			n = Node(r.head)
			n.addNodes(r.satisfy(sentence[i:]))
			sentence = sentence[:i] + [n] + sentence[len(n.nodes)+i:]
	return sentence

def iterred(leaves):
	"""
	Function: uses reduce to build tree, first using only rules1 and rules2
	Parameters: leaves list
	Returns: nodes list
	"""
	sentence = leaves
	newsent = []
	while sentence != newsent:
		i = 0
		newsent = sentence
		while i < len(sentence):
			sentence = reduce(sentence,i,rules1)
			sentence = reduce(sentence,i,rules2)
			i += 1
	return sentence

def iterred2(leaves):
	"""
	Function: uses reduce to build tree, first using all rules
	Parameters: leaves list
	Returns: [fulll tree]
	"""
	sentence = leaves
	newsent = []
	while sentence != newsent:
		i = 0
		newsent = sentence
		while i < len(sentence):
			sentence = reduce(sentence,i,rules1)
			sentence = reduce(sentence,i,rules2)
			sentence = reduce(sentence,i,rules3)
			if len(reduce(sentence,i,rules4)) == 1:
				sentence = reduce(sentence,i,rules4)
			i += 1
	return sentence

def printTree(text):
	"""
	Function: creates and prints tree
	Parameters: text string
	Returns: N/A
	"""
	test = makeLeaves(pos(text))
	for x in iterred2(iterred(test)):
		print x

def printSentence(tree):
	"""
	Function: recursively prints sentence from tree
	Parameters: sentence node
	Returns: N/A
	"""
	if tree.isLeaf:
		print tree.word,
	else:
		for n in tree.nodes:
			printSentence(n)

def combine(sent1, sent2):
	"""
	Function: randomly chooses a depth=1 phrase of one sentence and replaces of phrase of the same type in a second sentence
	Parameters: 2 sentence nodes
	Returns: new sentence node
	"""
	if not sent1[0].isLeaf and not sent2[0].isLeaf:
		nodes1 = sent1[0].nodes
		nodes2 = sent2[0].nodes
	else:
		combine(sent1,sent2)
	a = nodes2[random.randint(0,len(nodes2) -1)]
	for i,n in enumerate(nodes1):
		if n.head == a.head:
			nodes1[i] = a
			return iterred2(nodes1)
	combine(nodes1,nodes2)


# Demonstration -- prints trees for famous first sentences
printTree("In my younger and more vulnerable years my father gave me some advice that I've been turning over in my mind ever since")
print "---"
printTree("The things you own end up owning you")
print "---"
printTree("It is a truth universally acknowledged that a single man in possession of a good fortune must be in want of a wife")

# Demonstration -- prints combined sentence for 1 and 3
test1 = iterred2(iterred(makeLeaves(pos("In my younger and more vulnerable years my father gave me some advice that I've been turning over in my mind ever since"))))

test2 = iterred2(iterred(makeLeaves(pos("The things you own end up owning you"))))

test3 = iterred2(iterred(makeLeaves(pos("It is a truth universally acknowledged that a single man in possession of a good fortune must be in want of a wife"))))

print "---"
for x in combine(test1,test2):
	printSentence(x)

if len(argv) == 2:
	print ("\n")
	printTree(sys.argv[1])

if len(argv) == 3:
	print ("\n")
	sent1 = iterred2(iterred(makeLeaves(pos(sys.argv[1]))))
	sent2 = iterred2(iterred(makeLeaves(pos(sys.argv[2]))))
	for x in combine(sent1, sent2):
		printSentence(x)

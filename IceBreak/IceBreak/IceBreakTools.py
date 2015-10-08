import requests
from scrapy.http import TextResponse
import re
import csv
import collections

def strip_text(data):
    '''return a list from an html string of the html tags'''
    p = re.compile('<.*?>')
    return p.findall(data)

def strip_tags(data):
	'''strips tags from an html string.'''
	p = re.compile('<.*?>')
	return p.sub("",data)

def strip_meta(tags):
	'''strips metadata (classes, attributes etc) from list of html tags'''
	cleantags = [];
	p = re.compile("""\A\<[a-z | A-Z]*\ """)
	for tag in tags:
		if (tag[1]=="!"):
			pass
		else:
			new_tag = p.findall(tag)
			if new_tag==[]: cleantags.append(tag)
			else: cleantags.append(new_tag[0][:-1]+">")
	return cleantags

def sanitise(raw_tags,codex):
	'''
	take tags and replace by an string character alphabet. codex is "tags4"
	'''
	reader = csv.reader(open(codex, 'rb'))
	tag_dict= dict((x[0],x[1]) for x in reader)
	sanitised_list = []
	for item in raw_tags:
		try:
			sanitised = tag_dict[item]
			sanitised_list.append(sanitised)
		except:
			pass
	return "".join(sanitised_list)


def most_common(lst):
	'''
	find the most common member of a list
	'''
	data = collections.Counter(lst)
	return data.most_common(1)[0][0]

def get_bigrams(s):
	'''
	Takes a string and returns a list of bigrams
	'''
	return [s[i:i+2] for i in xrange(len(s) - 1)]

def similarity(str1, str2):
	'''
	strike a match algorithm!
    http://www.catalysoft.com/articles/StrikeAMatch.html
    http://stackoverflow.com/questions/653157/a-better-similarity-ranking-algorithm-for-variable-length-strings
	Perform bigram comparison between two strings
	and return a percentage match in decimal form
	'''
	if (str1=="" or str2==""): 
		score = 0.0
	else: 
		pairs1 = get_bigrams(str1)
		pairs2 = get_bigrams(str2)
		union  = len(pairs1) + len(pairs2)
		hit_count = 0
		for x in pairs1:
			for y in pairs2:
				if x == y:
					hit_count += 1
					pairs2.remove(y)
					break
		if union == 0:
			score = 0.
		else: 
			score = (2.0 * hit_count) / union
	return score

def layer_report(r,thresholds):
    '''
    analyse a selector r, return a boolean if the selector represents a data collection
    and a list of the the similarity between the selector children and the most common child.
    '''
    st = thresholds["similarity_threshold"]
    nt = thresholds["node_threshold"]
    ast = thresholds["average_similarity_threshold"]
    pt = thresholds["proportion_threshold"]
    structures = []
    sims = []
    for mem in r.xpath("*"):
		raw_tags = strip_meta(strip_text(mem.extract()))
		san = sanitise(raw_tags,'IceBreak/tags4.csv')
		structures.append(san)
    mc = most_common(structures)
    for s in structures:
		sims.append(similarity(s,mc))
    ave_sim = sum(sims)/len(sims)
    node_count = len(r.xpath("*"))
    qual_nodes = sum([st<=x<=1 for x in sims])
    proportion = qual_nodes/float(node_count)
    done = (
        (qual_nodes>=nt) and 
        (proportion>=pt) and 
        (node_count>=nt) and
        (ave_sim>=ast)
    )
    print("average similarity: " + str(ave_sim))
    print("node count: " + str(node_count))
    print("qualifying nodes: "+str(qual_nodes))
    print("proportion of records similar: " + str(proportion))
    print("Am I done? : " + str(done) )
    return (done,sims)


def select_cube(r):
    '''
    select the selector r's child with most descendents.
    '''
    cubes = r.xpath("*")
    sizes = [len(c.xpath("descendant::*")) for c in cubes]
    ind = sizes.index(max(sizes))
    print(
        "returning node:" + str(ind) +
        " with descendents: "+ str(sizes[ind])
    )
    return (cubes[ind])


def crush_ice(r):
    '''
    iterate through a selectors children to find data collection within it.
    Follows child with most descendents unless heuristic conditions fulfilled.
    saves the data to file.
    '''
    (layer,sims) = layer_report(r)
    if not layer:
        return crush_ice(select_cube(r))
    else:
        return serve_drink(r,sims)


def serve_drink(r,sims,thresholds):
    '''
    consume the children of r, processing only those with high enough similarity in "sims"
    '''
    cubes = r.xpath("*")
    print("preparing to Consume data. Total records: " + str(len(sims)))
    for ind in range(len(cubes)):
        if sims[ind]>=thresholds["similarity_threshold"]:
    	    print("*"*10+"Recording Record number: "+str(ind)+"*"*10)
    	    print(cubes[ind].extract())
    return("finished")
import requests
from scrapy.http import TextResponse
import re
import IceBreakTools as ibt

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
		raw_tags = ibt.strip_meta(ibt.strip_text(mem.extract()))
		san = ibt.sanitise(raw_tags,'tags4.csv')
		structures.append(san)
    mc = ibt.most_common(structures)
    for s in structures:
		sims.append(ibt.similarity(s,mc))
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
    new_node ='/*['+str(ind+1)+']'
    return new_node


def crush_ice(r,xp,thresholds,response):
    '''
    iterate through a selectors children to find data collection within it.
    Follows child with most descendents unless heuristic conditions fulfilled.
    saves the data to file.
    '''
    (layer,sims) = layer_report(r,thresholds)
    if not layer:
        xp = xp+select_cube(r)
        r = response.xpath(xp)
        xp = crush_ice(r,xp,thresholds,response)
    return xp
  
def main(link,thresholds = {"similarity_threshold": 0.6,"node_threshold": 50,"average_similarity_threshold":0.7,"proportion_threshold":0.7}):
    r = requests.get(link)
    response = TextResponse(r.url, body=r.text, encoding='utf-8')
    bd = "//body"
    xp = crush_ice(response.xpath(bd),bd,thresholds,response)
    return xp
    
print(main('http://ora.ox.ac.uk/search/detailed?q=%2A%3A%2A&truncate=450&rows=500&sort=timestamp%20desc'))

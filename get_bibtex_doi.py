#from scholarly import scholarly
#search_query = scholarly.search_pubs(s)
#scholarly.pprint(next(search_query))
#pub = next(search_query)
#scholarly.bibtex(pub)
from habanero import Crossref
from fuzzywuzzy import fuzz
import sys

print(sys.argv)
try:
    if ".bib" in sys.argv[1]:
        fname = sys.argv[1]
    else:
        print("First argument should be bibtex file filename.bib and not", sys.argv[1])
        raise IndexError
except IndexError:
    print("Expected usage: \n python3 get_bibtex_doi.py filename.bib")
    quit()

cr = Crossref()

#Create a new bibtex file which will have DOI in it
with open("doi_"+fname, "w+") as g:
    with open(fname, 'r') as f:
        #Go through bibtex file and make a copy
        for l in f:
            g.write(l)
            #For title entries, clean up syntax
            if "title" in l.lower():
                s = l.strip()
                for r in ['title','Title', '=', '"', ',', '{', '}', '\t', '\n' ]:
                    s = s.replace(r,"")
                print(s)
        
                #Use crossref API to get DOI based on title
                try:
                    sr = cr.works(query_title = s)
                #Skip if failure to search
                except requests.exceptions.HTTPError: 
                    print("HTTP ERROR - CANNOT FIND INFO, SKIPPING", s)
                    continue
                results = sr['message']['items']

                #Loop over all results until title looks about right
                c = 0
                for r in results:
                    checktitle = r['title']
                    doi = r['DOI']
                    fzratio = fuzz.ratio(checktitle[0], s)
                    print(s, checktitle, fzratio, doi)
                    #If title agreement is greater than 90%, write the DOI
                    if fzratio > 90:
                        extraline = "doi = {" + doi + "},\n"
                        print("Adding DOI=",extraline)
                        g.write(extraline)
                        break
                    #Give up after first 20 elements
                    elif c > 20:
                        break

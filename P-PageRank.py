#!/usr/bin/env python
import os
import sys
from StringIO import StringIO
from collections import defaultdict
import operator
    
class DBLPnetwork_P_PageRank:
    """Use dictionaries to build directed DBLPnetwork_P_PageRank to conduct P-PageRank
       analysis for a specific author using meta-path: APVPA and APTPA respectively
       by initilize DBLPnetwork and call either find_top_10_similar_authors_APVPA or 
       find_top_10_similar_authors_APTPA function.
    """
    def __init__(self, author, venue, paper, term, relation):
        """Build a DBMLnetwork by parsing 
           @param: the author, venue, paper, term, and realtion.txt
           @return: author_dict, venue_dict, paper_dict, term_dict, relation_dict
                    author_paper_dict, paper_venue_dict
        """
        # self-defined parameters, can be updated according to data
        self.teleport_constant = 0.15
        self.random_walk_iterations = 2
        self.quadratic_error = 0.001
        self.threshold_to_discard = 0.5
        
        # program variables
        self.total_nodes = 0
        self.initial_distribution = 0
        self.distribution_dict = {} # key: author/venue/paper/term name, value: distribution
        self.author_dict = {}  # key: author id, value: author name
        self.venue_dict = {}   # key: venue  id, value: venue  name
        self.paper_dict = {}   # key: paper  id, value: paper  name
        self.term_dict = {}    # key: term   id, value: term   name
        self.relation_dict = defaultdict(list)
        self.author_paper_dict = defaultdict(list)
        self.paper_venue_dict = defaultdict(list)
        self.paper_term_dict = defaultdict(list)
        self.APV_dict = defaultdict(list)
        self.APT_dict = defaultdict(list)
        self.AV_dict= {}
        self.AT_dict = {}
        self.AA_dict_APVPA = defaultdict(list)
        self.AA_dict_APTPA = defaultdict(list)
        
        self._file_to_dict(author, venue, paper, term, relation)
        self._build_paths()
        self._build_APV_APT_path()

    def _file_to_dict(self,author, venue, paper, term, relation):
        """ Parse txt files to dictionaries by calling each txt file's read function.
            @param: txt files with two (key, value) colmns
            @return: a dictionary for each input txt file.
        """
        self._read_relation(relation)
        self._read_author(author)
        self._read_venue(venue)
        self._read_paper(paper)
        self._read_term(term)
               
        
    def _read_relation(self, relation):
        """"
        Input: the relation file
        Output: relation_dict a dictionary with paper id as key,
                venue, author, or term id as value
        """
        numlines = 0
        with open(relation) as r:
            for line in r:
                numlines += 1
                (key, val, none) = line.split()
                self.relation_dict[key].append(val)
        print "number of undirected edges is: %d" % numlines
        print "Relation Length : %d" % len(self.relation_dict)

    def _read_author(self, author):
        """"
        Input: the author file
        Output: author_dict a dictionary with author id as key and
                author name as value
        """
        with open(author) as a:
            for line in a:
                splitLine = line.split()
                self.author_dict[splitLine[0]] = ' '.join(splitLine[1:])
        self.total_nodes += len(self.author_dict)
        print "Author Length : %d" % len(self.author_dict)
  
    def _read_venue(self, venue):
        """"
        Input: the venue file
        Output: author_dict a dictionary with venue id as key and
                venue name as value
        """
        with open(venue) as v:
            for line in v:
                splitLine = line.split()
                self.venue_dict[splitLine[0]] =  ' '.join(splitLine[1:])
        print "Venue Length : %d" % len(self.venue_dict)

    def _read_paper(self, paper):
        """"
        Input: the paper file
        Output: paper_dict a dictionary with paper id as key and
                paper name as value
        """
        with open(paper) as p:
            for line in p:
                splitLine = line.split()
                self.paper_dict[splitLine[0]] = ' '.join(splitLine[1:])
        print "Paper Length : %d" % len(self.paper_dict)

    def _read_term(self, term):
        """"
        Input: the term file
        Output: term_dict a dictionary with term id as key and
                term as value
        """
        with open(term) as t:
            for line in t:
                (key, value) = line.split()
                self.term_dict[key] = value
        print "Term Length : %d" % len(self.term_dict)

    def _build_paths(self):
        """Search through the relation_dict. If the value can be found in xxx_dict keys,
           add the xxx name into edges_dict for both direction.
           @input: relation_dict - extract values with xxx id
                   paper_dict, author_dict, venue_dict, and term_dict
           @output: edges_dict with xxx name as key and paper name as value
                    edges_dict with paper name as key and xxx name as value
        """
        for paperid, ids in self.relation_dict.iteritems():
            if self.paper_dict.has_key(paperid):
                paper = self.paper_dict.get(paperid)
            else:
                break
                  
            for i in ids:
                # Build author paper paths in the edges_dict
                if self.author_dict.has_key(i):
                    author = self.author_dict.get(i)
                    self.author_paper_dict[author].append(paper) 
                # Build paper venue paths in the edges_dict 
                elif self.venue_dict.has_key(i):
                    venue = self.venue_dict.get(i)
                    self.paper_venue_dict[paper].append(venue)
                # Build paper term path in the paper_term_dict
                elif self.term_dict.has_key(i):
                    term = self.term_dict.get(i)
                    self.paper_term_dict[paper].append(term)
        
    def _build_APV_APT_path(self):
        """Search through the author_paper_dict. If the paper can be found in paper_venue_dict or paper_term_dict
           add the venue or term name into APV_dict or APT_dict.
           @input: author_paper_dict, paper_venue_dict, and paper_term_dict
           @output: APV_dict with author name as key and (paper, venue) pair as value
                    APT_dict with author name as key and (paper, term) pair as value
                    AV_dict with (author, venue) pair as key and number of paths from author to venue as value
                    AT_dict with (author, term) pair as key and number of paths from author to term as value
        """
        for author,papers in self.author_paper_dict.iteritems():
            for paper in papers:
                # Build APV path (author_paper_venue)
                if self.paper_venue_dict.has_key(paper):
                    venues = self.paper_venue_dict.get(paper)
                    for venue in venues:
                        # APV path
                        self.APV_dict[author].append((paper, venue))
                        # AV path
                        if (self.AV_dict.has_key((author, venue))):
                            val = self.AV_dict.get((author, venue)) + 1
                            self.AV_dict[(author, venue)]  = val
                        else:
                            self.AV_dict[(author, venue)] = 1
                        
                # Build APT path (author_paper_term)
                if self.paper_term_dict.has_key(paper):
                    terms = self.paper_term_dict.get(paper)
                    for term in terms:
                        # APT path
                        self.APT_dict[author].append((paper, term))
                        # AT path
                        if (self.AT_dict.has_key((author, term))):
                            val = self.AT_dict.get((author, term)) + 1
                            self.AT_dict[(author, term)]  = val
                        else:
                            self.AT_dict[(author, term)] = 1
    
    def _find_venues_for_an_author(self, an_author):
        """Find a list of venues for one author
           @input: AV_dict with (author, venue) as key, number of paths from author to venue as value
                   venue_dict with venue id as key, venue name as value
                   author name
           @output: ret_dict with venue name as key and number of paths from author to venue as value
        """
        ret_dict = {}
        for venueid, venuename in self.venue_dict.iteritems():
            if (self.AV_dict.has_key((an_author, venuename))):
                ret_dict[venuename] = self.AV_dict.get((an_author, venuename))
        return ret_dict
        
    def _find_terms_for_an_author(self, an_author):
        """Find a list of terms for one author
           @input: AT_dict with (author, term) as key, number of paths from author to term as value
                   term_dict with term id as key, term name as value
                   author name
           @output: ret_dict with term name as key and number of paths from author to term as value
        """
        ret_dict = {}
        for termid, termname in self.term_dict.iteritems():
            if (self.AT_dict.has_key((an_author, termname))):
                ret_dict[termname] = self.AT_dict.get((an_author, termname))
        return ret_dict
         
    def _build_AA_dict_APVPA(self):
        """Find paths from an_author to all other authors using APVPA path by calling _find_venues_for_an_author
           @input: AV_dict with (author, venue) as key, number of paths from author to venue as value
                   author_dict
           @output: ret_dict with venue name as key and number of paths from author to venue as value
        """
        for authorid, an_author in self.author_dict.iteritems():
            venuedict = self._find_venues_for_an_author(an_author)
            venuelist = venuedict.keys()
            for (author, venue), num_to_author in self.AV_dict.iteritems():
                if venue in venuelist:
                    num_from_an_author = venuedict.get(venue)
                    num_paths = num_from_an_author * num_to_author   
                    self.AA_dict_APVPA[an_author].append((author, num_paths))
                    
    def _build_AA_dict_APTPA(self):
        """Find paths from an_author to all other authors using APTPA path by calling _find_terms_for_an_author
           @input: AT_dict with (author, term) as key, number of paths from author to venue as value
                   author_dict
           @output: ret_dict with venue name as key and number of paths from author to venue as value
        """
        for authorid, an_author in self.author_dict.iteritems():
            termdict = self._find_terms_for_an_author(an_author)
            termlist = termdict.keys()
            for (author, term), num_to_author in self.AT_dict.iteritems():
                if term in termlist:
                    num_from_an_author = termdict.get(term)
                    num_paths = num_from_an_author * num_to_author 
                    # Because of the APTPA author network is too dense, I decide to use a normalized score
                    # for APTPA.
                    # normalized_num_paths = num_paths/20
                    # if normalized_num_paths > 0:
                    #     self.AA_dict_APTPA[an_author].append((author, normalized_num_paths))
                    self.AA_dict_APTPA[an_author].append((author, num_paths))
                      
    def _set_initial_distribution(self, an_author):
        """Set initial distribution for each node by going through each node in
           author_dict, paper_dict, venue_dict, and term_dict. 
           For PageRank, the inital distribution should be (1-teleport_constant)/total_nodes. 
           For Personalized PageRank, the initial distribution is the same for all other nodes
           besides the interested node(s), an author in this project. 
           This author's initial distribution would be
           (1-teleport_constant)/number of total nodes + teleport_constant
           @input: teleport_constant, total_nodes, 
                   author_dict, paper_dict, venue_dict, and term_dict
           @output: distribution_dict with initial_distribution
        """
        self.initial_distribution = (1-self.teleport_constant)/self.total_nodes
        for authorid, author in self.author_dict.iteritems():
            self.distribution_dict[author] = self.initial_distribution
            if author == an_author:
                self.distribution_dict[author] += self.teleport_constant
        
    def _one_step_random_walk(self, an_author, lastiteration, path):
        """Conduct random walk along each edge in the network to obtain a
           distribution surface that each distribution means the possibility
           to randomly walk to that node.
           Note: As the provided case is a connected graph with undirected edges,
           there won't be any sink node needs to distribute a teleport_constant
           probability to randomly jump to all other nodes.
           Only the node of interest (an_author) will add a teleport_constant probability
           to be randomly jumped to for each source node that we go through.
           @input: AA_dict_APVPA
        """
        count = 0
        for source, sinks in self.AA_dict_APTPA.iteritems():
            num_out = 0
            count += 1
            for (sink, num_paths) in sinks:
                num_out += num_paths
            distribution = self.distribution_dict[source]/num_out
            distribution_to_neighbor = (1-self.teleport_constant)*distribution
            distribution_to_interest = self.teleport_constant*distribution
            # Random walk to neighbors
            for (sink, num_paths) in sinks:
                self.distribution_dict[sink] += distribution_to_neighbor
            # Random jump to node of interest
            self.distribution_dict[an_author] += distribution_to_interest
              
            # if not in the last iteration and if not the last one in AA_dict
            # update the source to 0. Otherwise, keep the original value
            if not (lastiteration and count == self.total_nodes):
                self.distribution_dict[source] = 0
                   
    def find_top_10_similar_authors(self, an_author, path):
        """Find top 10 similar authors using PathSim algorithm with APVPA path by building AA_dict using APTPA.
           @input: an author name
           @output: a list of 10 authors
        """
        if path == "APTPA":
            self._build_AA_dict_APTPA()
        elif path == "APVPA":
            self._build_AA_dict_APVPA()
            
        self._set_initial_distribution(an_author)
        for i in range(0, self.random_walk_iterations-1):
            self._one_step_random_walk(an_author, 0, path)
        self._one_step_random_walk(an_author, 1, path)
        sorted_distribution_dict = sorted(self.distribution_dict.items(), key=operator.itemgetter(1), reverse=True)[:10]
        ret_list = []
        for author,distribution in sorted_distribution_dict:
            ret_list.append(author)
        return ret_list
        
        
    def print_dict(self, dict):
        """ Print normal dict with value as a string for debug purpose.
            In this program, dict should be author_dict, paper_dict, venue_dict,
            or term_dict.
        """
        for key, value in dict.iteritems():
            print key + ':' + str(value)            
 
    def print_dict_tuple_key(self, dict):
        """ Print dict with values as a list of string tuples for debug purpose.
            In this program, dict should be AV_dict or AT_dict.
        """
        for (k1, k2), value in dict.iteritems():
            print k1 +"," + k2 + ":"+ str(value)
            
    def print_defaultdict(self, dict):
        """ Print dict with values as a list of string for debug purpose.
            In this program, dict should be relation_dict, author_paper_dict,
            paper_venue_dict, or paper_term_dict.
        """
        for key, values in dict.iteritems():
            print key + ':' + ', '.join(values)
    
    def print_defaultdict_tuple_value(self, dict):
        """ Print dict with values as a list of string tuples for debug purpose.
            In this program, dict should be APV_dict, APT_dict, AA_dict_APVPA, or AA_dict_APTPA
        """
        for key,values in dict.iteritems():
            print key
            print values
            print '--------------------------------------------'
            #print key + ':' + ', '.join(str(i) for i in values)
            print len(values)
        
def main():
    dblp = DBLPnetwork_P_PageRank('author.txt', 'venue.txt', 'paper.txt', 
                       'term.txt', 'relation.txt')
  
    print "============================================================="
    print "============  Results using P-PageRank  ====================="
    print "=============================================================\n"
    
    print "========Top 10 using APVPA for Christos Faloutsos============"
    CFlist_APVPA = dblp.find_top_10_similar_authors("Christos Faloutsos", "APVPA")
    for author in CFlist_APVPA:
        print author

    print "============Top 10 using APVPA for AnHai Doan================="
    ADlist_APVPA = dblp.find_top_10_similar_authors("AnHai Doan", "APVPA")
    for author in ADlist_APVPA:
        print author

    print "===========Top 10 using APTPA for Xifeng Yan=================="
    XYlist_APTPA = dblp.find_top_10_similar_authors("Xifeng Yan", "APTPA")
    for author in XYlist_APTPA:
        print author

    print "===========Top 10 using APTPA for Jamie Callan=================="      
    JClist_APTPA = dblp.find_top_10_similar_authors("Jamie Callan", "APTPA")
    for author in JClist_APTPA:
        print author
    
if __name__ == "__main__":
    main()
        
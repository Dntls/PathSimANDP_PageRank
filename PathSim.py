# coding=UTF-8
#!/usr/bin/env python
import os
import sys
from StringIO import StringIO
from collections import defaultdict
import operator

"""
03/06/2016 by Youshan
Run the code by having author.txt, venue.txt, paper.txt, term.txt, and relation.txt in the
same folder with PathSim.py and typing 'python PathSim.py'. The results will be in the console.
"""


class DBLPnetwork_PathSim:
    """Use dictionaries to build directed DBLPnetwork_PathSim to conduct PathSim simialrity 
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
        self.author_dict = {}
        self.venue_dict = {}
        self.paper_dict = {}
        self.term_dict = {}
        self.relation_dict = defaultdict(list)
        self.author_paper_dict = defaultdict(list)
        self.paper_author_dict = defaultdict(list)
        self.paper_venue_dict = defaultdict(list)
        self.venue_paper_dict = defaultdict(list)
        self.paper_term_dict = defaultdict(list)
        self.APV_dict = defaultdict(list)
        self.APT_dict = defaultdict(list)
        self.VPA_dict = defaultdict(list)
        self.AV_dict = {}
        self.AT_dict = {}
        self.VA_dict = {}
        self.AA_dict_APVPA = {}
        self.AA_dict_APTPA = {}
        self.AA_dict_AVA = {}
        self.AA_dict_VPAPV = {}
        self._file_to_dict(author, venue, paper, term, relation)
        self._build_paths()
        self._build_APV_APT_VPA_path()

    def _file_to_dict(self, author, venue, paper, term, relation):
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
        with open(relation) as r:
            for line in r:
                (key, val, none) = line.split()
                self.relation_dict[key].append(val)
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
                self.venue_dict[splitLine[0]] = ' '.join(splitLine[1:])
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
           add the xxx name into xxx_paper_dict or paper_xxx_dict. xxx is author, venue, or term
           @input: relation_dict - extract values with xxx id
                   paper_dict, author_dict, venue_dict, and term_dict
           @output: xxx_paper_dict with xxx name as key and paper name as value
                    paper_xxx_dict with paper name as key and xxx name as value
        """
        for paperid, ids in self.relation_dict.iteritems():
            if self.paper_dict.has_key(paperid):
                paper = self.paper_dict.get(paperid)
            else:
                break

            for i in ids:
                # Build author paper path in the author_paper_dict
                if self.author_dict.has_key(i):
                    author = self.author_dict.get(i)
                    self.author_paper_dict[author].append(paper)
                    self.paper_author_dict[paper].append(author)
                # Build paper venue path in the venue_paper_dict 
                elif self.venue_dict.has_key(i):
                    venue = self.venue_dict.get(i)
                    self.paper_venue_dict[paper].append(venue)
                    self.venue_paper_dict[venue].append(paper)
                # Build paper term path in the paper_term_dict
                elif self.term_dict.has_key(i):
                    term = self.term_dict.get(i)
                    self.paper_term_dict[paper].append(term)

        print "author-paper Length : %d" % len(self.author_paper_dict)
        print "paper_venue Length : %d" % len(self.paper_venue_dict)
        print "paper_term Length : %d" % len(self.paper_term_dict)

    def _build_APV_APT_VPA_path(self):
        """Search through the author_paper_dict. If the paper can be found in paper_venue_dict or paper_term_dict
           add the venue or term name into APV_dict or APT_dict.
           @input: author_paper_dict, paper_venue_dict, and paper_term_dict
           @output: APV_dict with author name as key and (paper, venue) pair as value
                    APT_dict with author name as key and (paper, term) pair as value
                    AV_dict with (author, venue) pair as key and number of paths from author to venue as value
                    AT_dict with (author, term) pair as key and number of paths from author to term as value
        """
        for author, papers in self.author_paper_dict.iteritems():
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
                            self.AV_dict[(author, venue)] = val
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
                            self.AT_dict[(author, term)] = val
                        else:
                            self.AT_dict[(author, term)] = 1
        for venue, papers in self.venue_paper_dict.iteritems():
            for paper in papers:
                # Build VPA path (venue_paper_author)
                if self.paper_author_dict.has_key(paper):
                    authors = self.paper_author_dict.get(paper)
                    for author in authors:
                        # VPA path
                        self.VPA_dict[venue].append((paper, author))
                        # VA path
                        if (self.VA_dict.has_key((venue, author))):
                            val = self.VA_dict.get((venue, author)) + 1
                            self.VA_dict[(venue, author)] = val
                        else:
                            self.VA_dict[(venue, author)] = 1

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

    def _find_authors_for_an_venue(self, an_venue):
        """Find a list of venues for one author
           @input: AV_dict with (author, venue) as key, number of paths from author to venue as value
                   venue_dict with venue id as key, venue name as value
                   author name
           @output: ret_dict with venue name as key and number of paths from author to venue as value
        """
        ret_dict = {}
        for authorid, authorname in self.author_dict.iteritems():
            if (self.VA_dict.has_key((an_venue, authorname))):
                ret_dict[authorname] = self.VA_dict.get((an_venue, authorname))
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

    def get_self_to_self(self, num_paths):
        return num_paths * num_paths

    def build_AA_dict_APVPA(self, an_author):
        """Find paths from an_author to all other authors using APVPA path by calling _find_venues_for_an_author
           @input: AV_dict with (author, venue) as key, number of paths from author to venue as value
                   author name
           @output: ret_dict with venue name as key and number of paths from author to venue as value
        """

        venuedict = self._find_venues_for_an_author(an_author)
        venuelist = venuedict.keys()
        for (author, venue), num_to_author in self.AV_dict.iteritems():
            if venue in venuelist:
                num_from_an_author = venuedict.get(venue)  # 指定作者在该领域的paper数
                an_author_self_paths = self.get_self_to_self(num_from_an_author)  # 数量平方
                author_self_paths = self.get_self_to_self(num_to_author)  # 其他作者到这个领域的paper数
                self.AA_dict_APVPA[author] = 2.00 * num_from_an_author * num_to_author / (
                            an_author_self_paths + author_self_paths)
        return self.AA_dict_APVPA

    def build_AA_dict_AVA(self, an_author):
        """Find paths from an_author to all other authors using APVPA path by calling _find_venues_for_an_author
           @input: AV_dict with (author, venue) as key, number of paths from author to venue as value
                   author name
           @output: ret_dict with venue name as key and number of paths from author to venue as value
        """

        paperlist = self.author_paper_dict.get(an_author)
        num_from_an_author = len(paperlist)
        an_author_self_paths = self.get_self_to_self(num_from_an_author)
        for paper in paperlist:
            authorlist = self.paper_author_dict.get(paper)

            if authorlist is not None:
                for other_author in authorlist:
                    other_paperlist = self.author_paper_dict.get(other_author)
                    author_self_paths = self.get_self_to_self(len(other_paperlist))
                    if self.AA_dict_AVA.get(other_author) is None:
                        self.AA_dict_AVA[other_author] = 2.00 / (
                            an_author_self_paths + author_self_paths)
                    else:
                        self.AA_dict_AVA[other_author] += 2.00 / (
                                an_author_self_paths + author_self_paths)
        return self.AA_dict_AVA

    def build_AA_dict_APTPA(self, an_author):
        """Find paths from an_author to all other authors using APTPA path by calling _find_terms_for_an_author
           @input: AT_dict with (author, term) as key, number of paths from author to term as value
                   author name
           @output: ret_dict with term name as key and number of paths from author to term as value
        """

        termdict = self._find_terms_for_an_author(an_author)
        termlist = termdict.keys()
        for (author, term), num_to_author in self.AT_dict.iteritems():
            if term in termlist:
                num_from_an_author = termdict.get(term)
                an_author_self_paths = self.get_self_to_self(num_from_an_author)
                author_self_paths = self.get_self_to_self(num_to_author)
                self.AA_dict_APTPA[author] = 2.00 * num_from_an_author * num_to_author / (
                            an_author_self_paths + author_self_paths)
        return self.AA_dict_APTPA
    def build_AA_dict_VPAPV(self, an_venue):
        """Find paths from an_author to all other authors using APVPA path by calling _find_venues_for_an_author
           @input: AV_dict with (author, venue) as key, number of paths from author to venue as value
                   author name
           @output: ret_dict with venue name as key and number of paths from author to venue as value
        """

        authordict = self._find_authors_for_an_venue(an_venue)
        authorlist = authordict.keys()
        for (venue, author), num_to_venue in self.VA_dict.iteritems():
            if author in authorlist:
                num_from_an_venue = authordict.get(author)  # 指定作者在该领域的paper数
                an_venue_self_paths = self.get_self_to_self(num_from_an_venue)  # 数量平方
                author_self_paths = self.get_self_to_self(num_to_venue)  # 其他作者到这个领域的paper数
                if(self.AA_dict_VPAPV.get(venue) is None):
                    self.AA_dict_VPAPV[venue] = 2.00 * num_from_an_venue * num_to_venue / (
                   an_venue_self_paths + author_self_paths)
                else:
                    self.AA_dict_VPAPV[venue] += 2.00 * num_from_an_venue * num_to_venue / (
                            an_venue_self_paths + author_self_paths)

        return self.AA_dict_VPAPV

    def find_top_10_similar_authors_AVA(self, an_author):
        """Find top 10 similar authors using PathSim algorithm with APVPA path.
           @input: an author name
           @output: a list of 10 authors
        """
        self.build_AA_dict_AVA(an_author)
        sorted_AA_dict_AVA = sorted(self.AA_dict_AVA.items(), key=operator.itemgetter(1), reverse=True)[:40]
        ret_list = []
        for key, value in sorted_AA_dict_AVA:
            ret_list.append(key)
        return ret_list
    def find_top_10_similar_venues_VPAPV(self, an_venue):
        """Find top 10 similar authors using PathSim algorithm with VPAPV path.
           @input: an venue name
           @output: a list of 10 venues
        """
        self.build_AA_dict_VPAPV(an_venue)
        sorted_AA_dict_VPAPV = sorted(self.AA_dict_VPAPV.items(), key=operator.itemgetter(1), reverse=True)[:11]
        ret_list = []
        for key, value in sorted_AA_dict_VPAPV:
            ret_list.append(key)
        return ret_list
    def find_top_10_similar_authors_APVPA(self, an_author):
        """Find top 10 similar authors using PathSim algorithm with APVPA path.
           @input: an author name
           @output: a list of 10 authors
        """
        self.build_AA_dict_APVPA(an_author)
        sorted_AA_dict_APVPA = sorted(self.AA_dict_APVPA.items(), key=operator.itemgetter(1), reverse=True)[:40]
        ret_list = []
        for key, value in sorted_AA_dict_APVPA:
            ret_list.append(key)
        return ret_list

    def find_top_10_similar_authors_APTPA(self, an_author):
        """Find top 10 similar authors using PathSim algorithm with APTPA path.
           @input: an author name
           @output: a list of 10 authors
        """
        self.build_AA_dict_APTPA(an_author)
        sorted_AA_dict_APTPA = sorted(self.AA_dict_APTPA.items(), key=operator.itemgetter(1), reverse=True)[:40]
        ret_list = []
        for key, value in sorted_AA_dict_APTPA:
            ret_list.append(key)
        return ret_list

    def print_dict(self, dict):
        """ Print normal dict with value as a string for debug purpose.
            In this program, dict should be author_dict, paper_dict, venue_dict,
            term_dict, AA_dict_APVPA, or AA_dict_APTPA.
        """
        for key, value in dict.iteritems():
            print key + ':' + str(value)

    def print_dict_tuple_key(self, dict):
        for (k1, k2), value in dict.iteritems():
            print k1 + "," + k2 + ":" + str(value)

    def print_defaultdict(self, dict):
        """ Print dict with values as a list of string for debug purpose.
            In this program, dict should be relation_dict, author_paper_dict,
            paper_venue_dict, or paper_term_dict.
        """
        for key, values in dict.iteritems():
            print key + ':' + ', '.join(values)

    def print_defaultdict_tuple_value(self, dict):
        """ Print dict with values as a list of string tuples for debug purpose.
            In this program, dict should be APV_dict or APT_dict.
        """
        for line in dict.iteritems():
            print line
            # print key + ':' + ', '.join(str(i) for i in values)


def main():
    dblp = DBLPnetwork_PathSim('author.txt', 'venue.txt', 'paper.txt',
                               'term.txt', 'relation.txt')

    # print "========Top 10 using APVPA for Christos Faloutsos============"
    # CFlist_APVPA = dblp.find_top_10_similar_authors_APVPA("Christos Faloutsos")
    # for author in CFlist_APVPA:
    #     print author
    #
    # print "============Top 10 using APVPA for AnHai Doan================="
    # ADlist_APVPA = dblp.find_top_10_similar_authors_APVPA("AnHai Doan")
    # for author in ADlist_APVPA:
    #     print author
    #
    # print "============Top 10 using APTPA for Xifeng Yan=================="
    # XYlist_APTPA = dblp.find_top_10_similar_authors_APTPA("Xifeng Yan")
    # for author in XYlist_APTPA:
    #     print author
    #
    # print "===========Top 10 using APTPA for Jamie Callan=================="
    # JClist_APTPA = dblp.find_top_10_similar_authors_APTPA("Jamie Callan")
    # for author in JClist_APTPA:
    #     print author

    # print "===========Top 40 using AVA for Jamie Callan=================="
    # JClist_AVA = dblp.find_top_10_similar_authors_AVA("Jiawei Han")
    # for author in JClist_AVA:
    #     print author
    # print "============Top 40 using APVPA for AnHai Doan================="
    # ADlist_APVPA = dblp.find_top_10_similar_authors_APVPA("Jiawei Han")
    # for author in ADlist_APVPA:
    #     print author
    # print "===========Top 10 using APTPA for Jamie Callan=================="
    # JClist_APTPA = dblp.find_top_10_similar_authors_APTPA("Jiawei Han")
    # for author in JClist_APTPA:
    #     print author
    print "===========Top 10 using VPAPV for SIGMOD Conference=================="
    JClist_VPAPV = dblp.find_top_10_similar_venues_VPAPV("SIGMOD Conference")
    for venue in JClist_VPAPV:
        print venue
if __name__ == "__main__":
    main()

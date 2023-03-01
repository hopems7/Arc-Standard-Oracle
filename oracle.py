#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import nltk
from collections import deque

nltk.data.path.append('/corpora/nltk/nltk-data')

def transition(trans, stack, buffer1, arc_tup):
	if trans=='SH':
		stack.insert(0, arc_tup.pop(0))		
		buffer1.pop(0)
	else:
		if trans=='RA':
			del stack[0]
			#print(stack)
		elif trans=='LA':
			del stack[1]
			#print(stack)
		
	return arc_tup, buffer1, stack
		
def oracle(stack, sequenceFile, arc_tup):

	if len(stack)<=1:					#catches first few instances in which the stack is empty
		transition='SH'
		sequenceFile.write("SHIFT\n")	
		
	elif stack[0][0] == stack[1][3]:		#if top of stack is head of 2nd in stack:
		transition=('LA')
		sequenceFile.write("(LEFTARC,"+str(stack[1][2])+")\n")
	elif stack[1][0] == stack[0][3] and attachment(stack, arc_tup) == True: 		#if 2nd in stack is head of top of stack AND all children of top of stack are attached
		transition=('RA')		
		sequenceFile.write("(RIGHTARC,"+str(stack[0][2])+")\n")
	else:							#shift in all other instances
		transition='SH'
		sequenceFile.write("SHIFT\n")	
	return transition
	
#function to check if all children have been attached
def attachment(stack, arc_tup):
	#print("right arc check")
	match =0
	for item in arc_tup:
		#print(item)
		if stack[0][0] == item[3]:
			#print(str(stack[0])+"="+str(item))
			#print("MATCH FOUND!")
			match+=1	
		#else:
			#print("NO MATCH FOUND")
			
	if match > 0:
		return False		#if match found, right arc not possible yet
	else:
		return True			#no match found, right arc possible
	if not arc_tup:
		return False		#return false if there is nothing left in arc_tup
	
def main():
	inp=sys.argv[1]
	#dep_out=sys.argv[2]
	seq_out=sys.argv[3]
	outSeqFile=open(seq_out, 'w')
	p_stack=deque()		
	word_buffer=[]
	words_index=[]
	dependency_rels=[]		
	head_index=[]
	arc_tup=[]
	arc_tup2=[]
	
	#configure
	with open(inp, 'r') as inputParses:		
		for line in inputParses:
			if line.strip() or line=='':		#if line not blank
				line=line.strip().split('\t')
				words_index.append(line[0])
				word_buffer.append(line[1])			
				dependency_rels.append(line[2])	
				head_index.append(line[3])
				arc_tup.append(line)
				
			else: 							#if break point hit, run sentence through oracle
				for item in arc_tup:
					arc_tup2.append(item)
				flag=1
				while word_buffer and p_stack != "ROOT" :		
					if flag == 1:
						p_stack.insert(0, "ROOT")
						flag=0
					oracle_trans=oracle(p_stack, outSeqFile, arc_tup)
					arc_tup, word_buffer, p_stack=transition(oracle_trans, p_stack, word_buffer, arc_tup)
					
				while p_stack:
					if len(p_stack) ==2:
						outSeqFile.write("(RIGHTARC,ROOT)\n\n")	
						del p_stack[0]
						del p_stack[0]
					else:
						oracle_trans=oracle(p_stack, outSeqFile, arc_tup)
						arc_tup, word_buffer, p_stack=transition(oracle_trans, p_stack, word_buffer, arc_tup)
					
				#clear lists for next parse
				word_index=[]
				word_buffer=[]
				dependency_rels=[]
				head_index=[]
				arc_tup=[]
				arc_tup2=[]
		#catches if there is no extra line
		for item in arc_tup:
			arc_tup2.append(item)
		#print(arc_tup2)
		flag=1
		while word_buffer and p_stack != "ROOT" :
			if flag == 1:
				p_stack.insert(0, "ROOT")
				flag=0
			oracle_trans=oracle(p_stack, outSeqFile, arc_tup)
			arc_tup, word_buffer, p_stack=transition(oracle_trans, p_stack, word_buffer, arc_tup)
		while p_stack:
			if len(p_stack) ==2:	
				outSeqFile.write("(RIGHTARC,ROOT)\n\n")		
				del p_stack[0]
				del p_stack[0]
			else:
				oracle_trans=oracle(p_stack, outSeqFile, arc_tup)
				arc_tup, word_buffer, p_stack=transition(oracle_trans, p_stack, word_buffer, arc_tup)
					
		#clear lists for next parse
		word_index=[]
		word_buffer=[]
		dependency_rels=[]
		head_index=[]
		arc_tup=[]
		arc_tup2=[]		
	inputParses.close()
	outSeqFile.close()
	
if __name__=="__main__":
	main()

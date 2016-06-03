#coding:utf-8

import re
from util import *

def readToken(filename):
	inToken = []
	pattern = re.compile(r'\S+\s*(?P<token>\S+)\s*\w+')
	for line in open(filename):
		match = pattern.search(line[:-1])
		if match is None:
			print 'Fail to read token file:', filename
			return False, inToken
		token = match.group('token')
		inToken.append(token)
	return True, inToken


def parser():
	filename = raw_input('please enter filename for Syntax\n')
	# filename = 'syntax.txt'
	isll, start,vn_set, vt_set, productions ,forseen = util(filename)
	if not isll:
		# print 'The Syntax is not LL(1).'
		return
	flag,inStr = readToken('token_table.txt')
	inStr.append('~')
	# if not flag:
	# 	return
	# for token in inToken:
	# 	print token

	# inStr = ['int', 'id', '(', ')', '{', 'int', 'id',  ';', '}', '~']

	"""对输入串instr预测分析"""
	"""分析栈用list实现"""
	def stack_push(stack, ele):
		stack.append(ele)
	def stack_pop(stack):
		stack.pop(len(stack)-1)
	def stack_top(stack):
		return stack[len(stack) - 1]

	analysis_stack = []
	stack_push(analysis_stack, '~')
	stack_push(analysis_stack, start)

	flag = False
	pos = 0
	step = 0
	while pos < len(inStr):
		step += 1
		print '=========', step, inStr[pos], '=========='
		print analysis_stack
		v = stack_top(analysis_stack)
		if inStr[pos] == '~' and  v == '~':
			flag = True
			break
		"""
		如果分析栈中是终结符，看终结符和输入待输入字符是否相等，不等匹配失败
		成功则分析栈pop, 输入字符右边一个
		"""
		if v in vt_set:
			if v == inStr[pos]:
				print v,'MATCH'
				stack_pop(analysis_stack)
				pos += 1
				continue
			else:
				print 'FAILED TO MATCH'
				break
		"""
		如果分析栈中是非终结符，找forseen[v]里面有没有inStr[pos]为键的值，
		没有匹配失败
		"""
		if v in vn_set:
			si = forseen[v]
			if inStr[pos] not in si:
				print 'FAILED TO MATCH'
				break
			"""
			可以用产生式推导，非终结符出栈，产生式右边倒序进栈
			输入字符不变
			"""
			right = si[inStr[pos]]
			print right,'MATCH'
			stack_pop(analysis_stack)
			if right[0] == '$':
				continue
			j = len(right) - 1
			while j >= 0:
				stack_push(analysis_stack, right[j])
				j -= 1

	if flag:
		print 'YES'
	else:
		print 'NO'

if __name__ == '__main__':
	parser()
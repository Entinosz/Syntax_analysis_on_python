#coding:utf-8
import re
def readSyntax(filename):
	start = None
	vn_set = set()
	vt_set = set()
	productions = []
	pattern = re.compile(r'^(?P<left>\w+)\s*=\s*(?P<right>.*?)$')
	lineNo = 0
	for line in open(filename):
		"""vt given"""
		lineNo += 1
		if lineNo == 1:
			vt_set = set(line[:-1].split(' '))
			continue
		if lineNo == 2:
			start = line[:-1]
			continue
		match = pattern.search(line[:-1])
		if match is None:
			print '%s cannot be recognized' %(line[:-1])
			continue
		left = match.group('left')
		right = match.group('right').split(' ')
		# if len(right) == 1 and right[0] == '$':
		# 	right = ['']
		vn_set.add(left)
		productions.append({'left':left, 'right':right})
	return start, vn_set, vt_set, productions

def preSolve(start, vn_set, vt_set, productions):
	prods_by_vn = {}
	num_of_prods = {}
	vn_to_null = {}
	cur_prods = []
	first = {}
	follow = {}
	forseen = {}
	#-1: notsure, 0: no, 1: yes
	# print '=========productions=========='
	# print len(productions)
	# for p in productions:
	# 	print p['left'], ':', p['right']
	
	for p in productions:
		left = p['left']
		right = p['right']
		if left not in prods_by_vn:
			prods_by_vn[left] = []
		prods_by_vn[left].append(right)
	
	notSure = len(vn_set)
	for vn in vn_set:
		num_of_prods[vn] = len(prods_by_vn[vn])
		vn_to_null[vn] = -1
		
	def remove_vn_prods(vn, prods):
		for p in prods:
			 if p['left'] == vn:
				print p
				prods.remove(p)
		
	def remove_v_in_p(v, p):
		p['right'].remove(v)

	def is_right_null(p):
		if len(p['right']) == 0:
			return True
		return False

	def is_v_to_null(v):
		if v == '$':
			return True
		if v in vt_set:
			return False
		elif vn_to_null[v] == 0:
			return False
		return True

	"""判断非终结符是否能推到空"""

	cur_prods = productions[:]
	# print '=========productions=========='
	# for p in productions:
	# 	print p['left'], ':', p['right']
	# print '=========cur_prods=========='
	# print len(cur_prods)
	# for p in cur_prods:
	# 	print p['left'], ':', p['right']


	"""在cur_prods中除去右边有终结符的产生式， productions中不能变"""
	for p in productions:
		"""v in right is vt, remove the prod"""
		left = p['left']
		right = p['right']
		# print '=========cur_prods=========='
		# print p['left'], ':', p['right']
		for v in right:
			if v not in vt_set:
				continue
			else:
				cur_prods.remove(p)
				num_of_prods[left] -=1
				# print p['left'], ':', p['right']
				break
	# print '>>>>>>>>>>>>>step 1<<<<<<<<<<<<<<<'
	# print '=========productions=========='
	# print len(productions)
	# for p in productions:
	# 	print p['left'], ':', p['right']
	# print '=========cur_prods=========='
	# for p in cur_prods:
	# 	print p['left'], ':', p['right']

	"""如果非终结符在左边的产生式没有了，这个产生式不能推到空"""
	for vn in vn_set:
		if num_of_prods[vn] == 0:
			vn_to_null[vn] = 0
			notSure -= 1

	"""删除右边是空的产生式"""
	tmp_prods = cur_prods[:]
	for p in tmp_prods:
		left = p['left']
		right = p['right']
		if right[0] == '$':
			cur_prods.remove(p)
			vn_to_null[left] = 1
			notSure -= 1
	
	# print '>>>>>>>>>>>>>step 2<<<<<<<<<<<<<<<'
	# print '=========productions=========='
	# print len(productions)
	# for p in productions:
	# 	print p['left'], ':', p['right']
	# print '=========cur_prods=========='
	# for p in cur_prods:
	# 	print p['left'], ':', p['right']

	"""
	在剩下来的产生式中，根据产生式右边的情况做判断
	如果右边有不能推到空的，左边也不能推到空
	否则，即右边都能推到空，左边也能推到空
	PS：
		书上将右边能推到空的都去掉了，这里没有去掉，如果去了，会改变产生式内容
	"""
	for p in cur_prods:
		p['right'] = list(p['right'])
	while notSure > 0:
		tmp_prods = cur_prods[:]
		for p in tmp_prods:
			left = p['left']
			right = p['right']
			null = 0
			for v in right:
				if vn_to_null[v] == 0:
					vn_to_null[left] = 0
					notSure -= 1
					break
				if vn_to_null[v] == -1:
					continue
				if vn_to_null[v] == 1:
					null += 1
			if null == len(right):
				vn_to_null[left] = 1
				notSure -= 1

	# print '>>>>>>>>>>>>>step 3<<<<<<<<<<<<<<<'
	# print '=========productions=========='
	# print len(productions)
	# for p in productions:
	# 	print p['left'], ':', p['right']

	# print '>>>>>>>>>>>>>vn_to_null<<<<<<<<<<<<<'
	# for vn in vn_set:
	# 	print vn, vn_to_null[vn]

	"""算FIRST集"""
	def get_first():
		for vt in vt_set:
			first[vt] = set([vt])
		first['$'] = '$'

		def get_first_vn(pre, vn):
			# print vn, prods_by_vn[vn]
			if vn in first:
				return True
			first[vn] = set()
			for right in prods_by_vn[vn]:
				for v in right:
					if v == pre:
						print pre,',' ,vn, '->',right
						print 'left recursion exists'
						return False
					if v not in first:
						if get_first_vn(vn, v) is False:
							return False
					first[vn] = first[vn].union(first[v])
					if not is_v_to_null(v):
						break
					if '$' in first[v]:
						first[vn].remove('$')
			return True


		for vn in vn_set:
			tmp = get_first_vn(' ', vn)
			# print tmp
			if not tmp:
				return False
		for vn in vn_set:
			if is_v_to_null(vn):
				first[vn].add('$')
		return True

	tmp = get_first()
	# print tmp
	if not tmp:
		return tmp, first, follow, forseen

	# print '===========first============='
	# for vn in vn_set:
	# 	print vn, ':', first[vn]
	

	"""算FOLLOW集"""
	def get_follow():
		follow[start] = set(['~'])
		
		def get_follow_vn(vn):
			# print '========',vn,'========='
			if vn not in follow:
				follow[vn] = set()
			else:
				return
			for p in productions:
				left = p['left']
				right = p['right']
				if vn in right:
					# print p
					index = right.index(vn)
					nxt = index + 1
					while nxt < len(right):
						nxt_v = right[nxt]
						follow[vn] = follow[vn].union(first[nxt_v])
						# print follow[vn]
						if is_v_to_null(nxt_v) == 1:
							follow[vn].remove('$')
							nxt += 1
						else:
							break
					if (index == len(right) - 1) or (nxt == len(right) and (is_v_to_null(right[nxt-1]) == 1)):
						if left not in follow:
							get_follow_vn(left)
						follow[vn] = follow[vn].union(follow[left])
			# print vn, ':', follow[vn]

		for vn in vn_set:
			get_follow_vn(vn)
	get_follow()
	# print '===========follow============='
	# for vn in vn_set:
	# 	print vn ,':', follow[vn]

	"""算SELECT集"""
	"""select集的下标和productions下标对应"""
	# select = []
	# for i in range(0,len(productions)):
	# 	p = productions[i]
	# 	left = p['left']
	# 	right = p['right']
	# 	flag = False
	# 	si = set()
	# 	"""如果右边有符号推不到空，select[i] = first(right)"""
	# 	for v in right:
	# 		si = si.union(first[v])
	# 		if not is_v_to_null(v):
	# 			flag = True
	# 			break
	# 	if '$' in si:
	# 		si.remove('$')
	# 	if not flag:
	# 		si = si.union(follow[left])
	# 	select.append(si)
	# 	print p
	# 	print si



	"""在生成预测分析表的时候，求select集"""
	"""
	prods_by_vn是以非终结符为关键字的字典，值为产生式右边构成的list
	预测分析表也以非终结符为关键字，值为以终结符为关键字的字典
	即分析表的本身和值都是字典
	"""
	for vn in vn_set:
		# print '=============',vn, '=============='
		forseen[vn] = {}
		rights = prods_by_vn[vn]
		vn_dict = {}
		for right in rights:
			# print right 
			"""
			算出该产生式的select集
			"""
			flag = False
			si = set()
			for v in right:
				si = si.union(first[v])
				if not is_v_to_null(v):
					flag = True
					break
			if '$' in si:
				si.remove('$')
			if not flag:
				si = si.union(follow[vn])
			# print si

			for v in si:
				if v in vn_dict:
					print 'not LL(1)'
					print vn, v, right
					return False, first, follow, forseen
				else:
					vn_dict[v] = []
				vn_dict[v] = right
		forseen[vn] = vn_dict
		# print vn, vn_dict

	return True,first, follow, forseen

def util(filename):
	start, vn_set, vt_set, productions = readSyntax(filename)
	isll, first, follow, forseen = preSolve(start, vn_set, vt_set, productions)
	if isll is False:
		print 'the parser is not LL(1)'
	else:
		outfile = open('ffs_table.txt','w+')
		outfile.write('===========FIRST=============\n')
		for vn in vn_set:
			outfile.write('%s\n: %s\n' %(vn, first[vn]))

		outfile.write('\n===========FOLLOW=============\n')
		for vn in vn_set:
			outfile.write('%s\n: %s\n' %(vn, follow[vn]))

		outfile.write('\n===========FORSEEN_TABLE=============\n')
		for vn in forseen:
			outfile.write('==========%s===========\n' %(vn))
			key = forseen[vn].keys()
			for vt in key:
				outfile.write('%s : %s\n' %(vt, forseen[vn][vt]))
	return isll, start,vn_set, vt_set, productions ,forseen
import string, copy

def joinHeaders(first, second, joined, on):
	joined.headers = first.headers[:]
	mappedHeaders = {}
	for header in second.headers:
		if header == on:
			continue
		i = 0
		newHeader = header
		while newHeader in first.headers:
			newHeader = '{0}_{1}'.format(newHeader, i)
			i += 1
		if i > 0:
			mappedHeaders[header] = newHeader

		joined.headers.append(newHeader)
	return mappedHeaders

def mergeRow(row, toMerge, mappedHeaders):
	for header in toMerge:
		if header in mappedHeaders:
			row[mappedHeaders[header]] = toMerge[header]
		else:
			row[header] = toMerge[header]

def mergeRows(first, second, joined, on, mappedHeaders):
	joined.rows = copy.deepcopy(first.rows)
	secondRows = copy.deepcopy(second.rows)

	for secondRow in secondRows:
		pivot = secondRow[on]
		for row in joined.rows:
			if row[on] == pivot:
				mergeRow(row, secondRow, mappedHeaders)
				break
		else:
			newRow = {}
			mergeRow(newRow, secondRow, mappedHeaders)
			joined.rows.append(newRow)

class Dataset:
	def __init__(self, filename = '', separator=',', header=True):
		self.headers = []
		self.rows = []

		try:
			infile = file(filename, 'r')
			if header:
				self.headers = infile.readline().strip().split(separator)
	
			for line in infile:
				row = line.strip().split(separator)
				if not header and not self.headers:
					self.headers = ["V{0}".format(i) for i in range(len(row))]
				self.rows.append({self.headers[i]:row[i] for i in range(len(row))})
			infile.close()
		except IOError:
			pass
	
	def export(self, filename):
		outfile = file(filename, 'w')
		outfile.write(','.join(self.headers))
		
		for row in self.rows:
			outfile.write('\n')
			outfile.write(','.join([row[x] for x in self.headers]))
		outfile.close()



	def join(self, other, on):
		"""Join self dataset with another dataset, creating a new dataset.
The original datasets remain unchanged.
The third argument is the header on which to join"""
		# check for correct join
		if not (on in self.headers or on in other.headers):
			print "Error: header '{0}' not found in both collections".format(on)
			return None

		# create new dataset
		joined = Dataset()
		
		# fill new dataset with combined data
		mappedHeaders = joinHeaders(self, other, joined, on)
		mergeRows(self, other, joined, on, mappedHeaders)
		joined.ensureFilled()

		# return newly created dataset
		return joined

	def pivot(self):
		"""Pivot this dataset into a new one, discarding current headers, using first column as new headers"""
		pivoted = Dataset()
		for (index, header) in enumerate(self.headers):
			for row in self.rows:
				if index == 0:
					pivoted.headers.append(row[header])
				else:
					if len(pivoted.rows) < index:
						pivoted.rows.extend([{} for x in range(index - len(pivoted.rows))])
					pivoted.rows[index - 1][row[self.headers[0]]] = row[header]
		return pivoted
		

	def ensureFilled(self):
		for row in self.rows:
			for header in self.headers:
				if not header in row:
					row[header] = None


	def append(self, other, ensureFilled = True):
		"""Append rows of another dataset to this one, leaving the other dataset unchanged"""
		self.rows.extend(other.rows)
		self.headers.extend([x for x in other.headers if not x in self.headers])
		if(ensureFilled):
			self.ensureFilled()
		return self



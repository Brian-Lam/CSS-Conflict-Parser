from os import listdir
from os.path import isfile, join
from collections import defaultdict

def main():
	# Hardcoded filepath, will implement user-input path if I have time
	filepath = "/Users/blam/ai-www/static/sass/"

	verbose_L1 = False
	verbose_L2 = True

	files = [f for f in listdir(filepath) if isfile(join(filepath, f)) and not f.startswith(".")]

	#Keep track of styles throughout all files
	styles = defaultdict(list)
	styles_reference = defaultdict(list)

	#Keep track of unconflicting files
	no_conflict = defaultdict(list)
	for _file in files:
		for _other_file in files:
			no_conflict[_file].append(_other_file)

	for _file in files:
		with open(filepath + _file) as f:
			# Keep track of whether we're in a styling block and what the current selectors are
			inside_block = False
			inside_comment = False
			selectors = []

			for line in f:
				# Check if we're still in a comment. If we are, check 
				# if we can get out. If we can't, skip this line.
				if "*/" in line:
					inside_comment = False
					# WARNING: Assuming comment is the whole 
					# line, potentially missing some styling
					continue
				# Check if a comment was started
				if "/*" in line:
					inside_comment = True
				if inside_comment:
					continue
				# This line opens and closes a block
				if "{" in line and "}" in line:
					# Media queries use a different syntax, can't split by space
					bracket_split = line.split("{")
					selectors = separateSelectors(bracket_split[0])
					# WARNING: This will clean out anything after the closing bracket
					rules_block = bracket_split[1].split("}")[0]						
					rules = separateRules(rules_block)
					#Filter out empty strings

					for rule in rules:
						rule_parts = rule.split(":") 
						attribute = rule_parts[0].strip()
						value = getValue(rule_parts)
						for selector in selectors:
							styles[selector].append(attribute)
							styles_reference[selector].append(formatRule(_file, attribute, value))


				# This line only opens a block, parse it for selectors
				elif "{" in line:
					inside_block = True
					bracket_split = line.split("{")

					#Update selectors globally for use later
					selectors = separateSelectors(bracket_split[0])
					rules = separateRules(bracket_split[1])

					# Parse any remaining rules on the line
					for rule in rules:
						rule_parts = rule.split(":") 
						attribute = rule_parts[0].strip()
						value = getValue(rule_parts)
						for selector in selectors:
							styles[selector].append(attribute)
							styles_reference[selector].append(formatRule(_file, attribute, value))
				# This line only closes a block
				elif "}" in line:
					inside_block = False
					# This shouldn't happen, implement later, low priority
				else:
					# Just a line with one rule, possibly more than one rule
					stripped = line.strip()
					rules = separateRules(stripped)
					for rule in rules:
						rule_parts = rule.split(":") 
						attribute = rule_parts[0].strip()
						value = getValue(rule_parts)
						for selector in selectors:
							styles[selector].append(attribute)
							styles_reference[selector].append(formatRule(_file, attribute, value))

	"""
	Print out all references to all attributes throughall out the CSS files
	"""
	if verbose_L1:
		for key, attrs in styles_reference.iteritems():
			print (key)
			for attr in attrs:
				print ("  - " + attr)

	"""
	Only display information if referenced in more than one file
	"""
	if verbose_L2:

		for key, attrs in styles_reference.iteritems():
			referenced = defaultdict(list)

			ref_track = defaultdict(list)
			attr_track = defaultdict(list)

			# Keep track of attributes and what pages reference them
			for attr in attrs:
				attr_parts = attr.split(" ")
				refed_from = attr_parts[0]
				refed_attr = attr_parts[1]
				refed_value = attr_parts[2] if attr_parts > 2 else " "
				if not refed_from in ref_track[refed_attr]:
					ref_track[refed_attr].append(refed_value + " in " + refed_from)
				attr_track[refed_attr].append(attr)
			
			for attr, refs in ref_track.iteritems():
				# Count unique values and references
				vals = []
				files = []
				for ref in refs:
					ref_parts = ref.split(" in ")
					value = ref_parts[0]
					from_file = ref_parts[1]
					vals.append(value)
					files.append(from_file)

				# Convert list into set so we only keep unique values
				vals_set = set(vals)
				file_set = set(files)

				if (len(vals_set) > 1 and len(file_set) > 1):
					print (key + " (" + attr + ")")
					for ref in refs:
						print ("  - " + ref)

					# Add to conflicts
					for _conflict in file_set:
						for conflicting_file in file_set:
							if conflicting_file in no_conflict[_conflict]: no_conflict[_conflict].remove(conflicting_file)


		unconflicting_files_header()
		for key, values in no_conflict.iteritems():
			print ("")
			print ("> " + key)
			for value in values:
				print (" - " + value)



"""
	Given a string of selectors, separate them into 
	individual components and return an array
	of the individual selectors
"""
def separateSelectors(_selectors):
	selectors = []

	# Media queries and @page keywords have a different format
	if "@media" in _selectors or "@page" in _selectors:
		selectors.append(_selectors.strip())
		return selectors
	for selector in _selectors.split(","):
		trimmed = selector.strip()
		if trimmed is not "":
			selectors.append(trimmed)
	return selectors

"""
	Given a string of rules, separate them into 
	individual components and return an 
	array of the individual rules

	Format of rules:
	String: "[attr]: [styling]"
"""
def separateRules(_rules):
	rules = []
	for rule in _rules.split(";"):
		trimmed = rule.strip()
		if trimmed is not "":
			rules.append(trimmed)
	return rules

"""
	Given a single CSS rule, return only the 
	attribute associated with it. 

	For example, input "font-size: 2 em" would
	return "font-size". 
"""
def getAttribute(_rule):
	return _rule.split(":")[0].strip()

"""
	Given an array of parts of a CSS rule, return
	only the value if it can be extracted. 
	Otherwise return an empty string.

"""
def getValue(_rule_parts):
	return _rule_parts[1].strip() if len(_rule_parts) > 1 else ""


def unconflicting_files_header():
	print ("")
	print ("******************************")
	print (" **** UNCONFLICTING FILES ****")
	print ("******************************")
	print ("")



"""
	Format rule for storage in dictionary so it can be parsed later
"""
def formatRule(_file, attribute, value):
	return str(_file) + " " + attribute + " " + str(value)

if __name__ == "__main__":
	main()
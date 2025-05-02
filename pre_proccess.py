import pandas as pd
import pickle
import math
import statistics
import re


def one_hot_encode(letter):
    letters = ['A', 'B', 'C', 'D', 'E']
    if letter not in letters:
        raise ValueError("Input must be a letter from 'A' to 'E'")
    one_hot = [1 if letter == l else 0 for l in letters]
    return one_hot

class Expression:
	def __init__(self, expression):
		self.raw = expression
		self.raw_terms = self.extract_terms(expression)
		self.num_terms = len(self.raw_terms)
		self.term_factors = {}
		self.next_var = 48
		self.reversed_term_factors = {}
		self.parsed_terms = [self.parse_term(term) for term in self.raw_terms]
		self.length = len(expression)
		self.numeric_factors = []

	def __str__(self):
		out = []
		out.append(f"Raw expression: {self.raw}")
		out.append(f"Extracted terms: {self.raw_terms}")
		out.append(f"Parsed terms: {self.parsed_terms}")
		out.append("Term factors:")
		for k, v in self.term_factors.items():
			out.append(f"  {k}: {v}")
		out.append("Reversed term factors:")
		for k, v in self.reversed_term_factors.items():
			out.append(f"  {k}: {v}")
		return "\n".join(out)
	
	def extract_terms(self, expression):
		return expression.split(" ")
	
	def extract_factors(self, term):
		algebreic = re.sub(r'-?\d+', '', term)
		nums = [float(num) for num in re.findall(r'-?\d+(?:\.\d+)?', term)]
		self.numeric_factors = nums
		return (algebreic, nums)

	def parse_term(self, term):
		parsed_term = []
		text_factors, numeric_factors = self.extract_factors(term)

		factors = list(text_factors) + numeric_factors

		for factor in factors:
			factor_str = str(factor)

			if factor_str not in self.term_factors.values():
				self.term_factors[chr(self.next_var)] = factor_str
				self.reversed_term_factors[factor_str] = chr(self.next_var)

				parsed_term.append(chr(self.next_var))

				self.next_var += 1
			else:
				parsed_term.append(self.reversed_term_factors[factor_str])

		return parsed_term

	def get_common_numeric_factors(self, factors1, factors2):
		factor_ratios = []
		for factor1 in factors1:
			possible = 0
			for factor2 in factors2:
				if factor2 != 0 and factor1 != 0:
					b = abs(factor1/factor2)
					a = possible

					possible = a if abs(a - 1) < abs(b - 1) and a != 0 else b
			factor_ratios.append(possible)
		return [statistics.mean(factor_ratios), statistics.stdev(factor_ratios)]
	
	def get_common_elements(self, list1, list2):
		return list(set(list1) & set(list2))

	def compare(self, expression):
		common_factors = self.get_common_elements(expression.term_factors.values(), self.term_factors.values())
		num_common_factors = len(common_factors)

		common_terms = self.get_common_elements(self.raw_terms, expression.raw_terms)
		num_common_terms = len(common_terms)

		if len(self.numeric_factors) >= 1 and len(expression.numeric_factors) >= 1:
			common_numeric_factors = self.get_common_numeric_factors(self.numeric_factors, expression.numeric_factors)
		else:
			common_numeric_factors = [0, 0]


		return [num_common_factors, num_common_terms] + common_numeric_factors

df = pd.read_parquet("data.parquet")

parsed_answers = [[Expression(answer[2:]) for answer in answers] for answers in df["options"]]
parsed_questions = [Expression(question) for question in df["question"]]

input_data = []

for x, parsed_answer in enumerate(parsed_answers):
	row = []
	for idx in range(len(parsed_answer)):
		for i in range(idx+1, 5):
			row += parsed_answer[idx].compare(parsed_answer[i])

		row.append(parsed_answer[idx].length)
		row.append(parsed_answer[idx].num_terms)

	for answer in parsed_answer:
		row += answer.compare(parsed_questions[x])

		term = answer.raw

		row.append(int('^' in term))
		row.append(int('√' in term))
		row.append(int('/' in term))
		row.append(int('(' in term or ')' in term))
		row.append(int('-' in term))

	row.append(parsed_questions[x].length)

	input_data.append(row)

data = pd.DataFrame({
	"input": input_data,
	"output": [one_hot_encode(answer) for answer in df["correct"]]
})

print(data)
len(data["input"][0])

data.to_pickle("data.pkl")
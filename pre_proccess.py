import pandas as pd
import re


df = pd.read_parquet("data.parquet")[:10]


class Expression:
	def __init__(self, expression):
		self.raw = expression
		self.raw_terms = self.extract_terms(expression)
		self.term_factors = {}
		self.next_var = 48
		self.reversed_term_factors = {}
		self.parsed_terms = [self.parse_term(term) for term in self.raw_terms]

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
	
	def get_common_elements(list1, list2):
		return list(set(list1) & set(list2))

	def compare(self, expression):
		common_factors = self.get_common_elements(expression.term_factors.values(), self.term_factors.values())
		num_common_factors = len(common_factors)

		common_terms = self.get_common_elements(self.raw_terms, expression.raw_terms)
		num_common_terms = len(common_terms)

		
		return [num_common_factors, num_common_terms]


parsed_answers = [[Expression(answer[2:]) for answer in answers] for answers in df["options"]]


prcs_df = pd.DataFrame()

for parsed_answer in parsed_answers:
	row = []
	for idx in range(len(parsed_answer)):
		compared = []
		for i in range(idx, 5):
			compared = parsed_answer[idx].compare()
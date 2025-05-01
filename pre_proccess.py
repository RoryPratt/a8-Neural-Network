import pandas as pd
from sympy import symbols, sympify, Mul
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.sympify import SympifyError
from tokenize import TokenError 
import re


df = pd.read_parquet("data.parquet")[:10]


class Expression:
	def __init__(self, expression):
		self.raw = expression
		self.raw_terms = self.extract_terms(expression)
		self.term_factors = {}
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

	def parse_term(self, term_raw):
		parsed_term = []
		term = self.safe_parse_expr(term_raw)
		factors = Mul.make_args(term)
		next_var = 48


		for factor in factors:
			factor_str = str(factor)

			if factor_str not in self.term_factors.values():
				self.term_factors[chr(next_var)] = factor_str
				self.reversed_term_factors[factor_str] = chr(next_var)

				parsed_term.append(chr(next_var))

				next_var += 1
			else:
				parsed_term.append(self.reversed_term_factors[factor_str])

		return parsed_term


df["parsed_options"] = [[Expression(answer[2:]) for answer in answers] for answers in df["options"]]

for items in df["parsed_options"]:
	for item in items:
		print(item)
# Copyright (c) 2024, BDF and contributors
# For license information, please see license.txt
import pandas as pd
import math
import frappe
from frappe.model.document import Document

class UploadMilkRateFile(Document):
	@frappe.whitelist()
	def get_rates(self, url):
		file_path = self.upload_excel
		data_df = pd.read_excel(f"{url.split('/')[2]}/public{file_path}", header=None)
		data_df = data_df.iloc[1:]
		data_df.columns=data_df.iloc[0]
		data_df = data_df[1:].reset_index(drop=True)

		def reformat_data(df):
			flag=1
			reformatted = []
			for row_index, row in df.iterrows():
				if flag:
					row_label = row.iloc[0]
					for col_index, value in enumerate(row.iloc[1:], start=1):
						col_label = df.columns[col_index]
						if math.isnan(value):
							flag=0
							continue
						reformatted.append(["{:.1f}".format(row_label), "{:.1f}".format(col_label), "{:.2f}".format(value)])
			return reformatted

		reformatted_data = reformat_data(data_df)
		self.milk_rate_chart.clear()
		for i in reformatted_data:
			if i[0] and i[1] and i[2]:
				self.append('milk_rate_chart', {
					'fat': float(i[0]), 'snf': float(i[1]), 'rate': float(i[2])
				})
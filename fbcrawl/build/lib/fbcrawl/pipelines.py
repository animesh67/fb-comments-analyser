# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from scrapy.exceptions import DropItem
from datetime import datetime
from scrapy.exporters import CsvItemExporter

class CommentPipeline(object):
	def open_spider(self, comments):
		f = open('comment.csv','wb')
		self.exporter = CsvItemExporter(f)
		self.exporter.start_exporting()

	def close_spider(self, comments):
		self.exporter.finish_exporting()
		
	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item

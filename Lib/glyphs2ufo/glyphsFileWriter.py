#!/usr/bin/python
#
# Copyright 2016 Georg Seifert. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http: #www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys, traceback
from classes import GSBase
from casting import needsQuotes, floatToString, feature_syntax_encode
import datetime


'''
	Usage
	
	writer = GlyphsWriter('Path/to/File.glyphs')
	writer.write(font)

'''


class GlyphsWriter(object):
	
	def __init__(self, filePath = None):
		
		if filePath is None:
			self.file = sys.stdout
		else:
			self.file = open(filePath, "w")
	
	def write(self, baseObject):
		
		self.writeDict(baseObject)
		self.file.write("\n")
		self.file.close()
	
	def writeDict(self, dictValue):
		self.file.write("{\n")
		forType = None
		if hasattr(dictValue, "_classesForName"):
			keys = dictValue._classesForName.keys()
		else:
			keys = dictValue.keys()
		keys.sort()
		for key in keys:
			
			if hasattr(dictValue, "_classesForName"):
				forType = dictValue._classesForName[key]
			try:
				if type(dictValue) == dict:
					value = dictValue[key]
				else:
					value = getattr(dictValue, key)
			except AttributeError:
				continue
			#print "__key", key
			self.writeKey(key)
			self.writeValue(value, key, forType=forType)
			self.file.write(";\n")
		self.file.write("}")
	
	def writeArray(self, arrayValue):
		self.file.write("(\n")
		idx = 0
		length = len(arrayValue)
		for value in arrayValue:
			self.writeValue(value)
			if idx < length - 1:
				self.file.write(",\n")
			else:
				self.file.write("\n")
			idx += 1
		self.file.write(")")
	
	def writeValue(self, value, forKey = None, forType = None):
		try:
			# print "__erite", value, forKey, forType
			if forKey == "transform":
				self.file.write("\"{%s}\"" % ", ".join([floatToString(f, 5) for f in value]))
			elif forKey == "position" or forKey == "place":
				self.file.write("\"{%s}\"" % ", ".join([floatToString(f) for f in value]))
			elif type(value) == list:
				self.writeArray(value)
			elif hasattr(value, "plistValue"):
				value = value.plistValue()
				self.file.write(value)
			elif type(value) == dict or isinstance(value, GSBase):
				self.writeDict(value)
			elif type(value) == float:
				self.file.write(floatToString(value, 3))
			elif type(value) == int:
				self.file.write(str(value))
			elif type(value) == bool:
				if value:
					self.file.write("1")
				else:
					self.file.write("0")
			elif type(value) == datetime.datetime:
				self.file.write("\"%s +0000\"" % str(value))
			else:
				if (forType == unicode):
					value = value.encode("utf-8")
				else:
					value = str(value)
				value = feature_syntax_encode(value)
				if needsQuotes(value) and forKey != "unicode":
					self.file.write("\"%s\"" % value)
				else:
					self.file.write(value)
		except:
			print traceback.format_exc()
	def writeKey(self, key):
		if needsQuotes(key):
			self.file.write("\"%s\" = " % key)
		else:
			self.file.write("%s = " % key)
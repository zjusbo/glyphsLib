#!/usr/bin/python
#
# Copyright 2016 Georg Seifert. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from casting import num, transform

__all__ = [
	"GFont",
]


class GBase():
	def __repr__(self):
		content = ""
		if hasattr(self, "_dict"):
			content = str(self._dict)
		return "<%s %s>" % (self.__class__.__name__, content)
	
	def classForName(self, name):
		return self._classesForName.get(name, str)

	def __setitem___(self, key, value):
		if not hasattr(self, "_dict"):
			self._dict = {}
		self._dict[key] = value
	def __setitem__(self, key, value):
		if type(value) is str and key in self._classesForName:
			value = self._classesForName[key](value)
		setattr(self, key, value)


class GCustomParameter(GBase):
	_classesForName = {
		"name": str,
		"value": str  # TODO: check 'name' to determine proper class
	}


class GInstance(GBase):
	_classesForName = {
		"exports": bool,
		"unitsPerEm": int,
		"customParameter": GCustomParameter,
	}

	def __init__(self):
		self.exports = True
		self.name = "Regular"


class GFontMaster(GBase):
	_classesForName = {
		"date": str,
		"unitsPerEm": int,
		"customParameter": GCustomParameter,
	}


class GNode(GBase):
	_classesForName = {	}

	def __init__(self, line = None):
		if line is not None:
			rx = '([-.e\d]+) ([-.e\d]+) (LINE|CURVE|OFFCURVE|n/a)(?: (SMOOTH))?'
			m = re.match(rx, line).groups()
			self.position = (num(m[0]), num(m[1]))
			self.type = m[2].lower()
			self.smooth = bool(m[3])
		else:
			self.position = (0, 0)
			self.type = 'line'
			self.smooth = False

	def __repr__(self):
		content = self.type
		if self.smooth:
			content += " smooth"
		return "<%s %g %g %s>" % (self.__class__.__name__, self.position[0], self.position[1], content)


class GPath(GBase):
	_classesForName = {
		"nodes": GNode,
		"closed": bool
	}


class GComponent(GBase):
	_classesForName = {
		"alignment": int,
		"transform": transform,
		"name": str,
	}

class GLayer(GBase):
	_classesForName = {
		"components": GComponent,
		"paths": GPath,

		"width": float
	}


class GGlyph(GBase):
	_classesForName = {
		"layers": GLayer,
	}


class GFont(GBase):
	
	_classesForName = {
		"date": str,
		"unitsPerEm": int,
		"fontMaster": GFontMaster,
		"glyphs": GGlyph,
		"instances": GInstance,
		"customParameters": GCustomParameter,
	}
	
	def __init__(self):
		print "__GFont init"
		self.familyName = "Unnamed font"

	def __repr__(self):
		return "<%s \"%s\">" % (self.__class__.__name__, self.familyName)

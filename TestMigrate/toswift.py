#!/usr/bin/python
import re
import codecs

rtype = r'([\w_]+)[ \*]*'
rtype_no = r'[\w_]+[ \*]*'
rname = r'([\w_\.]+)'
rmethod = r'([\w_]+)'
rvar = r'([@]?["]?[\w_ \.]*["]?)'
		
def get(reg, txt, default=None):
	""" Return list of matches 
		Usage: get(r'(\d+)test (.*)','3212test totiz')
		Out: ('3212', 'totiz')
		"""
	if None == reg or None == txt:
		return None

	matches = re.match(reg, txt)
	if None == matches:
		return default

	return matches.groups()

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

class ObjectiveCPropertyToSwift(object):
	TYPE_CASTS = dict(
		NSInteger = 'Int',
		BOOL = 'Bool',
		NSString = 'String',
		NSDictionary = 'ObjcDictionary',
		NSMutableDictionary = 'ObjcDictionary',
		NSArray = '[AnyObject]',
		NSMutableArray = '[AnyObject]',
		YES = 'true',
		NO = 'false',
	)
	
	def __init__(self, lines):
		super(ObjectiveCPropertyToSwift, self).__init__()
		self.lines = lines
	
	def toSwiftType(self, objcType):
		if objcType in self.__class__.TYPE_CASTS:
			return self.__class__.TYPE_CASTS[objcType]
		else:
			# Check String
			string = get(r'@("[\w_ ]*")', objcType)
			if None != string:
				return string[0]

			return objcType

	def remove_self(self, text):
		""" Remove self. """
		return text.replace('self.', '')

	def parse_with_format(self, line, reg, output_format, output_order=None):
		output = get(reg, line)
		if None != output:
			output = map(self.toSwiftType, output)
			if output_order:
				return output_format % tuple([output[index] for index in output_order])
			else:
				return output_format % tuple(output)
		else:
			return None
	
	def parse_with_formats(self, line, parse_formats):
		for parse_format in parse_formats:
			output = self.parse_with_format(line, parse_format['reg'], parse_format['output_format'], parse_format['output_order'])
			if None != output:
				output = self.remove_self(output)
				return output

		return None

# =================
# = Format Parser =
# =================
	def format_IBOutlet(self):
		parse_formats = []
		
		# IBOutlet: @property (weak, nonatomic) IBOutlet UITableView *menuListTable;
		parse_formats.append( dict(reg=r'@property \(weak, nonatomic\) IBOutlet (\w*)[\*\s]? [\*]?([\w_]*);', output_format='@IBOutlet weak var %s: %s!', output_order=[1,0]) )
		
		return parse_formats

	def format_IBAction(self):
		parse_formats = []
		
		# IBAction: - (IBAction)hitPlusButton:(id)sender;
		parse_formats.append( dict(reg=r'- \(IBAction\)(\w*):\(id\)sender.*', output_format="""@IBAction func %s(sender: AnyObject) {

}""", output_order=None) )
		# IBAction: - (IBAction)hitPlusButton:(UIButton *)sender;
		parse_formats.append( dict(reg=r'- \(IBAction\)(\w*):\((\w*) [\*]+\)sender.*', output_format="""@IBAction func %s(sender: %s) {

}""", output_order=None) )

		return parse_formats

	def format_Property(self):
		parse_formats = []
		
		# @property (nonatomic, strong) NSIndexPath *lastSelectedIndexPath;
		parse_formats.append( dict(reg=r'@property (.*) (\w*)[\*\s]? [\*]?(.*);', output_format='var %s: %s?', output_order=[2,1]) )
		
		return parse_formats

	def format_Define(self):
		parse_formats = []
		
		# NSString *CellIdentifier = @"Dining Home Loading";
		parse_formats.append( dict(reg=r'NSString \*([\w_]*) = @"(.*)"', output_format='let %s = "%s"', output_order=None) )
		
		# AsyncImageView *backgroundImageView = asyncImageWithTag(cell, 50);
		parse_formats.append( dict(reg=r'([\w_]*) \*([\w_]*) = ([\w_]*)WithTag\(([\w_]*), (\d*)\);', output_format='let %s = %s.%sWithTag(%s)', output_order=[1, 3, 2, 4]) )
		
		# UITableViewCell *cell = [tableView cellForRowAtIndexPath:indexPath];
		parse_formats.append( dict(reg=r'(\w*) \*([\w_]*) = \[([\w_]*) ([\w_]*):([\w_]*)\];', output_format='let %s = %s.%s(%s)', output_order=[1, 2, 3, 4]) )
		
		# UIColor *color = [UIColor clearColor];
		parse_formats.append( dict(reg=r'(\w*) \*([\w_]*) = \[([\w_]*) ([\w_]*)\];', output_format='let %s = %s.%s()', output_order=[1, 2, 3]) )
		
		# NSString *path = FOURLEAFBundle.mainBundle.resourcePath;
		parse_formats.append( dict(reg=r'([\w_]*) \*([\w_]*) = (.*);', output_format='let %s = %s', output_order=[1, 2]) )
		
		# Normal
		parse_formats.append( dict(reg=r'([\w_]*) \*([\w_]*);', output_format='let %s: %s?', output_order=None) )
		
		return parse_formats

	def format_DefineDelegate(self):
		parse_formats = []
		
		#  - (void)settingDidAssignTable:(NSString*)zone name:(NSString*)name split:(NSInteger)split;
		parse_formats.append( dict(reg=r'- \(void\)(\w*):\((\w*)[\*]?\)(\w*) (\w*):\((\w*)[\*]?\)(\w*) (\w*):\((\w*)\)(\w*);', output_format='func %s(%s: %s, %s %s: %s, %s %s: %s)', output_order=[0, 2, 1, 3, 5, 4, 6, 8, 7]) )
		
		#  - (void)settingDidAssignTable:(NSString*)zone name:(NSString*)name;
		parse_formats.append( dict(reg=r'- \(void\)(\w*):\((\w*)[\*]?\)(\w*) (\w*):\((\w*)[\*]?\)(\w*);', output_format='func %s(%s: %s, %s %s: %s)', output_order=[0, 2, 1, 3, 5, 4]) )
		
		#  - (void)settingDidAssignTable:(NSString*)zone;
		parse_formats.append( dict(reg=r'- \(void\)(\w*):\((\w*)[\*]?\)(\w*);', output_format='func %s(%s: %s)', output_order=[0, 2, 1]) )
		
		#  - (void)settingDidClear;
		parse_formats.append( dict(reg=r'- \(void\)([\w_]*);', output_format='func %s()', output_order=None) )
		
		return parse_formats

	def format_method(self):
		parse_formats = []

		# - (NSIndexPath*)subPathForIndexPath:(NSIndexPath*)indexPath {
		parse_formats.append( dict(reg=r'^- \((\w*)[ \*]*\)([\w_]*):\((\w*)[ \*]*\)([\w_]*)[ {]*$', output_format="""func %s(%s: %s?) -> %s {

}""", output_order=[1, 3, 2, 0]) )

		# - (NSIndexPath*)subPathForIndexPath:(NSIndexPath*)indexPath data:(NSArray*)data {
		parse_formats.append( dict(reg=r'^- \((\w*)[ \*]*\)([\w_]*):\((\w*)[ \*]*\)([\w_]*) ([\w_]*):\((\w*)[ \*]*\)([\w_]*)[ {]*$', output_format="""func %s(%s: %s?, %s %s: %s?) -> %s {

}""", output_order=[1, 3, 2, 4, 6, 5, 0]) )

		# - (BOOL)isFooterForPath:(NSIndexPath*)path subPath:(NSIndexPath*)subPath dataArr:(NSArray*)dataArr {
		parse_formats.append( dict(reg=r'^- \((\w*)[ \*]*\)([\w_]*):\((\w*)[ \*]*\)([\w_]*) ([\w_]*):\((\w*)[ \*]*\)([\w_]*) ([\w_]*):\((\w*)[ \*]*\)([\w_]*)[ {]*$', output_format="""func %s(%s: %s?, %s %s: %s?, %s %s: %s?) -> %s {

}""", output_order=[1, 3, 2, 4, 6, 5, 7, 9, 8, 0]) )

		# - (void)setZone:(NSString*)zone name:(NSString*)name split:(NSInteger)split shouldReload:(NSNumber*)shouldReload {
		parse_formats.append( dict(reg=r'^- \((\w*)[ \*]*\)([\w_]*):\((\w*)[ \*]*\)([\w_]*) ([\w_]*):\((\w*)[ \*]*\)([\w_]*) ([\w_]*):\((\w*)[ \*]*\)([\w_]*) ([\w_]*):\((\w*)[ \*]*\)([\w_]*)[ {]*$', output_format="""func %s(%s: %s?, %s %s: %s?, %s %s: %s?, %s %s: %s?) -> %s {

}""", output_order=[1, 3, 2, 4, 6, 5, 7, 9, 8, 10, 12, 11, 0]) )

		return parse_formats

	def format_method_call(self):
		parse_formats = []
		
		# [center removeObserver:self];
		parse_formats.append( dict(reg=r'^[ ]*\[' + rvar + r' ' + rmethod + r':' + rvar + r'\];[ ]*$', output_format='%s.%s(%s, %s:%s)', output_order=None) )

		# [center removeObserver:self name:UIKeyboardWillHideNotification];
		parse_formats.append( dict(reg=r'^[ ]*\[' + rvar + r' ' + rmethod + r':' + rvar + ' ' + rmethod + r':' + rvar + r'\];[ ]*$', output_format='%s.%s(%s, %s:%s)', output_order=None) )
		
		# [center removeObserver:self name:UIKeyboardWillHideNotification object:nil];
		parse_formats.append( dict(reg=r'^[ ]*\[' + rvar + r' ' + rmethod + r':' + rvar + ' ' + rmethod + r':' + rvar + r' ' + rmethod + r':' + rvar + r'\];[ ]*$', output_format='%s.%s(%s, %s:%s, %s:%s)', output_order=None) )
		
		# [center removeObserver:self name:UIKeyboardWillHideNotification object:nil object:nil];
		parse_formats.append( dict(reg=r'^[ ]*\[' + rvar + r' ' + rmethod + r':' + rvar + ' ' + rmethod + r':' + rvar + r' ' + rmethod + r':' + rvar + r' ' + rmethod + r':' + rvar + r'\];[ ]*$', output_format='%s.%s(%s, %s:%s, %s:%s, %s:%s)', output_order=None) )

		return parse_formats

	def format_statement(self):
		parse_formats = []
		
		#  backgroundImageView = asyncImageWithTag(cell, 50);
		parse_formats.append( dict(reg=r'^[ ]*([\w_]*) = ([\w_]*)WithTag\(([\w_]*), (\d*)\);[ ]*$', output_format='%s = %s.%sWithTag(%s)', output_order=[0, 2, 1, 3]) )
		
		# cell = [tableView createCell:@"Dining Order Custom Order Choice cell"];
		parse_formats.append( dict(reg=r'^[ ]*([\w_\.]*) = \[([\w_]*) ([\w_]*):' + rvar + '\];[ ]*$', output_format='%s = %s.%s(%s)', output_order=None) )
		
		# cell.backgroundColor = [UIColor clearColor];
		parse_formats.append( dict(reg=r'^[ ]*([\w_\.]*) = \[([\w_]*) ([\w_]*)\];[ ]*$', output_format='%s = %s.%s()', output_order=None) )
		
		# NSInteger optionSection = [self adjustSectionForOption:indexPath.section];
		# let optionSection = adjustSectionForOption(indexPath.section)
		parse_formats.append( dict(reg=r'^[ ]*' + rtype_no + rname + r'[ ]*=[ ]*\[' + rname + r' ' + rmethod + r':' + rvar + r'\];[ ]*$', output_format='let %s = %s.%s(%s)', output_order=None) )

		return parse_formats

	def run(self):
		for line in [line.strip() for line in self.lines.split('\n')]:
			parse_formats = []
			
			parse_formats += self.format_IBOutlet()
			parse_formats += self.format_IBAction()
			parse_formats += self.format_Property()
			parse_formats += self.format_Define()
			parse_formats += self.format_DefineDelegate()
			parse_formats += self.format_method()
			parse_formats += self.format_method_call()
			parse_formats += self.format_statement()

			converted_line = self.parse_with_formats(line, parse_formats)
			if None != converted_line:
				print bcolors.OKBLUE + converted_line + bcolors.ENDC
			else:
				print bcolors.FAIL + line + bcolors.ENDC

if __name__ == "__main__":
	import sys
	if len(sys.argv) == 1:
		text = ""
		stopword = "end"
		while True:
			line = raw_input()
			if line.strip() == stopword:
				break
			text += "%s\n" % line
		conn = ObjectiveCPropertyToSwift(text)
		conn.run()

	else:
		print 'usage convertToSwift'
		sys.exit()

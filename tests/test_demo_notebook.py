import unittest
import os
import subprocess

class TestNotebook(unittest.TestCase):
	def test_file(self):
		# list of strings representing the command
		args = ['jupyter', 
				'nbconvert',
				'--to',
				'script',
				'--execute',
				'demo.ipynb']

		try:
		# stdout = subprocess.PIPE lets you redirect the output
			res = subprocess.Popen(args, stdout=subprocess.PIPE)
		except OSError:
			print("error: popen")
			exit(-1) # if the subprocess call failed, there's not much point in continuing

		res.wait() # wait for process to finish; this also sets the returncode variable inside 'res'
		assert res.returncode == 0
		
		
if __name__ == '__main__':
	unittest.main()
	
	

'''
Quietbuster utility functions
'''

import logging
import os

def build_logger(log_dir: str, log_file: str) -> logging.Logger:
	'''
	Builds a custom logger that logs to both an external log file as well as the console.
	
	Args:
		None
	
	Returns:
		logging.Logger: A Logger object created from the current file.
	'''
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)

	file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
	console_handler = logging.StreamHandler()  # Log to the console
	file_handler.setLevel(logging.DEBUG)
	console_handler.setLevel(logging.DEBUG)
	
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	console_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
	return logger


def create_path(directory: str) -> None:
	'''
	Creates a directory from provided directory string parameter.

	Args:
		directory str: A string containing the path of the directory to create.
	
	Returns:
		None
	'''
	try:
		if not os.path.exists(directory):
			os.makedirs(directory)
			print(f"Created directory at {directory}...")
	except (FileNotFoundError, OSError) as e:
		print(f"Error while creating directory, could not create filepath... {e}")
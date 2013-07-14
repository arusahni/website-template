import os
from doit.tools import config_changed

DOIT_CONFIG = { 'default_tasks': ['styles'] }
JQUERY_VERSION = '1.10.2'

def task__jquery():
	return {
		'actions' : ['wget -P assets/js http://code.jquery.com/jquery-%s.min.js' % JQUERY_VERSION],
		'uptodate' : [config_changed_or_missing(JQUERY_VERSION, 'assets/js/jquery-%s.min.js' % JQUERY_VERSION)]
	}

def task_init():
	return { 'actions':None, 'task_dep':['_jquery'] }

def task_styles():
	def check_lessfiles(directory):
		return [os.path.join(directory,f) 
				for f in os.listdir(directory) 
				if f.endswith('.less')]
	return {
		'actions' : ['./lessc assets/css/less/main.less assets/css/main.css'],
		'file_dep': check_lessfiles('assets/css/less')
	}


# uptodate
class config_changed_or_missing(object):
    """check if passed config was modified or the object is missing
    	stolen and modified from doit source.
    @var config (str) or (dict)
    @var check_path (str)
    """
    def __init__(self, config, check_path):
        self.config = config
        self.check_path = check_path
        self.config_digest = None

    def _calc_digest(self):
        if isinstance(self.config, basestring):
            return self.config
        elif isinstance(self.config, dict):
            data = ''
            for key in sorted(self.config):
                data += key + repr(self.config[key])
            if isinstance(data, unicode): # pragma: no cover # python3
                byte_data = data.encode("utf-8")
            else:
                byte_data = data
            return hashlib.md5(byte_data).hexdigest()
        else:
            raise Exception(('Invalid type of config_changed parameter got %s' +
                             ', must be string or dict') % (type(self.config),))

    def configure_task(self, task):
        task.value_savers.append(lambda: {'_config_changed':self.config_digest})

    def __call__(self, task, values):
        """return True if confing values are UNCHANGED"""
        self.config_digest = self._calc_digest()
        last_success = values.get('_config_changed')
        if last_success is None:
            return False
        return (last_success == self.config_digest and os.path.exists(self.check_path))

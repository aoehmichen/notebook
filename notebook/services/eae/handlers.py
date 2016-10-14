import json
import pprint
import io
import os
import zipfile

from tornado import gen, web

from ...base.handlers import APIHandler, json_errors
from ...nbconvert.handlers import get_exporter
from jupyter_client.jsonutil import date_default
from notebook.utils import url_path_join, url_escape

class EaeHandler(APIHandler):

    @web.authenticated
    @json_errors
    @gen.coroutine
    def post(self):
		"""Eae submit query prep. From notebook data form
		
		POST /api/eae/submit
		"""

		data = self.get_json_body();
		print(data);
		
		exporter = get_exporter("script");
		print("Got the script exporter");
		
		to_zip = []
		
		for f in data['files']:
			if f.rfind(".ipynb") != -1:
				model = self.contents_manager.get(path=f)
				output, resources = exporter.from_notebook_node(model['content']);
				to_zip.append({ "content": output, "filename": os.path.splitext(model['name'])[0] + resources['output_extension'] });
			else:
				model = self.contents_manager.get(path=f)
				to_zip.append({ "filename": model['name'], "content": model['content']});
		pprint.pprint(to_zip);
		
		print("TODO: Zip file to /tmp/uuid.zip et hop on est boooooon");
		zip_path = "/tmp/" + data['id'] + '.zip';
		# Prepare the zip file
		zipf = zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED)
		for entry in to_zip:
			zipf.writestr(entry['filename'], entry['content'])
		zipf.close()
		
		
		self.set_status(200);
		self.set_header('Content-Type', 'application/json');
		self.finish(json.dumps({ "id": data['id'], "zip": zip_path }, default=date_default));
		
#-----------------------------------------------------------------------------
# URL to handler mappings
#-----------------------------------------------------------------------------

default_handlers = [
    (r"/api/eae/submit", EaeHandler)
]

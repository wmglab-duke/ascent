import os
from src.core.query import Query
from src.utils import Config, Object

# THIS LINE IS USER-SPECIFIC UNTIL THERE IS A FIXED PLACE FOR ANALYSIS SCRIPTS
project_root = '/Users/jakecariello/Box/Documents/Pipeline/access'

query_criteria = os.path.join(project_root, 'config/user/query_criteria/0.json')

# NECESSARY PREREQUISITE FOR USING QUERY
os.chdir(project_root)

q = Query(query_criteria)

q.run()

summary = q.summary()


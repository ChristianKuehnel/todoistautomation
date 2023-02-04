#!/usr/bin/env python3

from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.api import TodoistAPI
import yaml
from typing import Dict, List
from uuid import uuid4
import requests
import argparse
import sys
import schedule
import time
import traceback
import logging


class Rule:
    """Wrapper around the rules defined in the config file."""

    def __init__(self, ruleDict :Dict):
        self.query = ruleDict["query"]
        self.move_to = ruleDict.get("move_to", None)       
        self.update = ruleDict.get("update", None)

    @staticmethod
    def build_rules(ruleYaml :Dict) -> List["Rule"]:
        """Parse the rules from the config file."""
        result = []
        for d in ruleYaml:
            result.append(Rule(d))
        # TODO: validate that self.update matches the parameters defined in
        #   https://developer.todoist.com/rest/v2/?python#update-a-task
        return result


class TodoistAutomation:
    """ Automatic processing of Todoist tasks. """

    def __init__(self, config_path):
        self.config = yaml.load( open(config_path, 'r'), Loader=yaml.SafeLoader)
        self.api_token = self.config["todoist_api_token"]
        self.rules = Rule.build_rules(self.config["rules"])
        self.api = TodoistAPI(self.api_token)
        self._projects = None

    def move_task(self, task_id: str, project_id: str) -> bool:
        """Move a task to a new project. 
        
        Workaround until the move feature is implemented in the library:
        https://github.com/Doist/todoist-api-python/issues/8 
        """
        body = {
            "commands": [
                {
                    "type": "item_move",
                    "args": {"id": task_id, "project_id": project_id},
                    "uuid": uuid4().hex,
                },
            ],
        }
        response = requests.post(
            "https://api.todoist.com/sync/v9/sync",
            headers={"Authorization": f"Bearer {self.api_token}"},
            json=body,
        )
        return response.ok


    def get_project_id_by_name(self, name: str):
        """The the id for a project by name."""
        # caching project names
        if self._projects is None:
            self._projects = {p.name:p.id for p in self.api.get_projects()}
        return self._projects.get(name)

    def process_rules(self):
        """Process all tasks matching all rules in the config file."""
        for rule in self.rules:
            self.process_rule(rule)

    def process_rule(self, rule:Rule):
        """Process all tasks matching a rule."""
        for task in self.api.get_tasks(filter=rule.query):
            self.transform(task.id, rule)

    def transform(self, task_id : int, rule:Rule):
        """Modify a task based on a rule."""

        if rule.update != None:
            self.api.update_task(task_id, **rule.update)
            logging.info(f"Updating task {task_id} to {rule.update}")

        if rule.move_to != None:
            new_project_id = self.get_project_id_by_name(rule.move_to)
            self.move_task(task_id, new_project_id)
            logging.info(f"Moved task: {task_id} to project {new_project_id}")

"""Wrap main function for scheduler. Catch all excpetions and continue."""
def scheduler_job():
    logging.info("Running scheduled job...")
    try:
        ta = TodoistAutomation('/config/config.yaml')
        ta.process_rules()
        logging.info("Scheduler completed.")
    except Exception:
      logging.error(traceback.format_exc())
    sys.stdout.flush()

def main():
  parser = argparse.ArgumentParser(prog = 'todoistautomation')
  parser.add_argument('--container',action='store_true')
  args = parser.parse_args()

  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
      datefmt='%Y-%m-%d %H:%M:%S',
  )

  if args.container:
    logging.info("Starting scheduler...")
    sys.stdout.flush()
    # TODO: set interval via config file
    schedule.every(5).minutes.do(scheduler_job)
    
    logging.info("Running automation on startup...")
    schedule.run_all()
    sys.stdout.flush()

    while True:
        schedule.run_pending()
        time.sleep(60)
  else:
    ta = TodoistAutomation('./config.yaml')
    ta.process_rules()

if __name__ == "__main__":
    main()
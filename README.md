# todoistautomation

Simple tool to automatically modify tasks in Todoist based on a simple,
configurable rules. 

This is work in progress and not ready for produciton use.

## Usage

This tool was developed with the usecase of automatically moving tasks that I created via the Amazon Alexa integration. So I want all items from the *Alexa To-do list* moved to my *Inbox* and set the due date for today. I also want to move all takss from the *Alexa shopping list* moved to my own shopping list.

For this use case Create a `config.yaml` file to configure the automations:
```
# set you api token here
todoist_api_token: <your api token>
# list of automation rules
rules:
  - # the rule will modify all tasks that match this query
    # the query syntax if defined in https://todoist.com/help/articles/205248842
    query: "project:Alexa*To-do-Liste"
    # Move to a different project
    move_to: "Inbox"
    # attributes to be updates, as defined in the API doc:
    # https://developer.todoist.com/rest/v2/?python#update-a-task
    update:
      # make the task due today
      due_string: "today"
  - query: "project:Alexa*Einkaufsliste"
    move_to: "Einkaufsliste"
```

The easiest way to run this application is to deploy it as a docker container and mount the folder containing your `config.yaml`:

```bash
docker run -v .:/config ghcr.io/christiankuehnel/todoistautomation:release
```
